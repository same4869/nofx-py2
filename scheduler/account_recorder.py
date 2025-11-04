"""
账户资产记录器

定期记录账户资产状态，包含未实现盈亏

功能：
- 每10分钟记录一次账户资产
- 包含总资产、可用余额、未实现盈亏
- 计算收益率和已实现盈亏
- 保存到account_history表

对应TypeScript: src/scheduler/accountRecorder.ts
"""

import asyncio
from datetime import datetime
from typing import Optional

from core.logger import logger
from core.database import get_async_session, AsyncSession
from core.models import AccountHistory
from services.exchange import ExchangeClient
from config.settings import settings


class AccountRecorder:
    """账户资产记录器"""
    
    def __init__(self, exchange_client: ExchangeClient, interval_minutes: int = 10):
        """
        初始化账户记录器
        
        Args:
            exchange_client: 交易所客户端
            interval_minutes: 记录间隔（分钟）
        """
        self.exchange = exchange_client
        self.interval_minutes = interval_minutes
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def record_account(self):
        """
        记录账户资产（包含未实现盈亏）
        
        Returns:
            是否成功记录
        """
        try:
            # 1. 获取账户信息
            account = await self.exchange.get_account()
            
            # 提取账户数据
            # Gate.io的account['total']不包含未实现盈亏
            # 需要主动加上unrealized才是真实的总资产
            account_total = float(account.get('total', 0))
            available_balance = float(account.get('available', 0))
            unrealized_pnl = float(account.get('unrealized', 0))
            
            # 总资产 = account.total + unrealized（包含未实现盈亏）
            total_balance = account_total + unrealized_pnl
            
            # 2. 从数据库获取初始余额（第一条记录）
            async with get_async_session() as session:
                session: AsyncSession
                
                # 查询最早的记录作为初始余额
                from sqlalchemy import select
                stmt = select(AccountHistory).order_by(AccountHistory.timestamp.asc()).limit(1)
                result = await session.execute(stmt)
                first_record = result.scalar_one_or_none()
                
                if first_record:
                    initial_balance = float(first_record.total_value)
                else:
                    # 如果没有历史记录，使用当前余额作为初始值
                    initial_balance = total_balance
                
                # 3. 计算已实现盈亏和收益率
                realized_pnl = total_balance - initial_balance
                return_percent = (realized_pnl / initial_balance) * 100 if initial_balance > 0 else 0
                
                # 4. 保存到数据库
                record = AccountHistory(
                    timestamp=datetime.now(),
                    total_value=total_balance,
                    available_cash=available_balance,
                    unrealized_pnl=unrealized_pnl,
                    realized_pnl=realized_pnl,
                    return_percent=return_percent,
                )
                
                session.add(record)
                await session.commit()
                
                # 5. 输出日志
                logger.info(
                    f"📊 账户已记录: "
                    f"总资产={total_balance:.2f} USDT, "
                    f"可用={available_balance:.2f} USDT, "
                    f"未实现盈亏={'+' if unrealized_pnl >= 0 else ''}{unrealized_pnl:.2f} USDT, "
                    f"收益率={'+' if return_percent >= 0 else ''}{return_percent:.2f}%"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"记录账户资产失败: {e}")
            return False
    
    async def _run_loop(self):
        """运行记录循环"""
        logger.info(f"账户记录器已启动，间隔: {self.interval_minutes} 分钟")
        
        # 立即执行一次
        await self.record_account()
        
        # 定期执行
        interval_seconds = self.interval_minutes * 60
        
        while self._running:
            try:
                await asyncio.sleep(interval_seconds)
                if self._running:  # 再次检查，避免停止后还执行
                    await self.record_account()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"账户记录循环异常: {e}")
    
    async def start(self):
        """启动账户记录器"""
        if self._running:
            logger.warning("账户记录器已在运行中")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("账户记录器已启动")
    
    async def stop(self):
        """停止账户记录器"""
        if not self._running:
            logger.warning("账户记录器未在运行")
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("账户记录器已停止")


def create_account_recorder(exchange_client: ExchangeClient) -> AccountRecorder:
    """
    创建账户记录器实例
    
    Args:
        exchange_client: 交易所客户端
        
    Returns:
        AccountRecorder实例
    """
    interval_minutes = int(settings.ACCOUNT_RECORD_INTERVAL_MINUTES or 10)
    return AccountRecorder(exchange_client, interval_minutes)


# 导出
__all__ = [
    'AccountRecorder',
    'create_account_recorder',
]

