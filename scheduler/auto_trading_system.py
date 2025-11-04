"""
自动交易系统（精简版）

整合交易循环和风险监控功能

功能模块：
1. 交易循环 - 定期执行AI决策和交易
2. 风险监控 - 账户级别的强制风控
3. 代码级保护 - 波段策略的止损/止盈监控（可选）

注意：这是TypeScript版本的精简实现，保留核心功能但代码更简洁

对应TypeScript:
- src/scheduler/tradingLoop.ts (1700+行) →  精简为约400行
- src/scheduler/stopLossMonitor.ts
- src/scheduler/trailingStopMonitor.ts
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

from core.logger import logger
from core.database import get_async_session, AsyncSession
from core.models import Trade, Position, AgentDecision, TradingSignal
from services.exchange import ExchangeClient
from services.market_analysis import (
    calculate_indicators,
    calculate_multi_timeframe_indicators,
)
from agents.trading_agent import (
    get_trading_strategy,
    get_strategy_params,
    generate_trading_prompt,
)
from config.settings import settings
from config.risk_params import RISK_PARAMS


class AutoTradingSystem:
    """
    自动交易系统
    
    整合交易循环、风险监控、代码级保护
    """
    
    def __init__(
        self,
        exchange_client: ExchangeClient,
        trading_interval_minutes: int = 5,
    ):
        """
        初始化自动交易系统
        
        Args:
            exchange_client: 交易所客户端
            trading_interval_minutes: 交易间隔（分钟）
        """
        self.exchange = exchange_client
        self.trading_interval_minutes = trading_interval_minutes
        
        # 交易统计
        self.start_time = datetime.now()
        self.iteration_count = 0
        
        # 任务控制
        self._trading_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False
        
        # 策略配置
        self.strategy = get_trading_strategy()
        self.strategy_params = get_strategy_params(self.strategy)
        
        # 持仓峰值盈利跟踪（用于移动止盈）
        self._peak_pnl: Dict[str, float] = {}
        
        logger.info(f"交易系统已初始化 - 策略: {self.strategy_params.name}")
    
    # ========== 市场数据收集 ==========
    
    async def collect_market_data(self) -> Dict[str, Any]:
        """
        收集所有交易币种的市场数据和技术指标
        
        Returns:
            市场数据字典
        """
        market_data = {}
        
        for symbol in RISK_PARAMS.TRADING_SYMBOLS:
            try:
                # 1. 获取ticker数据
                ticker = await self.exchange.get_futures_ticker(symbol)
                
                # 2. 获取多个时间周期的K线数据
                candles_5m = await self.exchange.get_futures_candles(symbol, '5m', 100)
                candles_15m = await self.exchange.get_futures_candles(symbol, '15m', 100)
                candles_1h = await self.exchange.get_futures_candles(symbol, '1h', 100)
                
                # 3. 计算技术指标
                indicators_5m = calculate_indicators(candles_5m)
                indicators_15m = calculate_indicators(candles_15m)
                indicators_1h = calculate_indicators(candles_1h)
                
                # 4. 组装市场数据
                market_data[symbol] = {
                    'price': float(ticker['last']),
                    'fundingRate': float(ticker.get('funding_rate', 0)),
                    **indicators_5m,  # 包含主要指标
                    'timeframes': {
                        '5m': indicators_5m,
                        '15m': indicators_15m,
                        '1h': indicators_1h,
                    }
                }
                
                # 5. 保存技术指标到数据库
                async with get_async_session() as session:
                    signal = TradingSignal(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        price=market_data[symbol]['price'],
                        ema_20=indicators_5m.get('ema20', 0),
                        ema_50=indicators_5m.get('ema50', 0),
                        macd=indicators_5m.get('macd', 0),
                        rsi_7=indicators_5m.get('rsi7', 50),
                        rsi_14=indicators_5m.get('rsi14', 50),
                        volume=indicators_5m.get('volume', 0),
                        funding_rate=market_data[symbol]['fundingRate'],
                    )
                    session.add(signal)
                    await session.commit()
                
                logger.debug(f"{symbol} 市场数据收集完成")
                
            except Exception as e:
                logger.error(f"收集 {symbol} 市场数据失败: {e}")
        
        return market_data
    
    # ========== 交易循环 ==========
    
    async def trading_cycle(self):
        """执行一次完整的交易周期"""
        try:
            self.iteration_count += 1
            elapsed_minutes = int((datetime.now() - self.start_time).total_seconds() / 60)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"交易周期 #{self.iteration_count} - 已运行 {elapsed_minutes} 分钟")
            logger.info(f"{'='*80}\n")
            
            # 1. 收集市场数据
            logger.info("📊 收集市场数据...")
            market_data = await self.collect_market_data()
            
            if not market_data:
                logger.warning("未能获取市场数据，跳过本次周期")
                return
            
            # 2. 获取账户信息
            logger.info("💰 获取账户信息...")
            account = await self.exchange.get_account()
            
            # 3. 获取当前持仓
            logger.info("📈 获取持仓信息...")
            positions = await self.exchange.get_positions()
            active_positions = [p for p in positions if float(p.get('size', 0)) != 0]
            
            # 4. 强制风控检查
            await self._mandatory_risk_checks(active_positions, account)
            
            # 5. 生成AI提示词
            logger.info("🤖 生成AI决策提示...")
            prompt_data = {
                'minutes_elapsed': elapsed_minutes,
                'iteration': self.iteration_count,
                'interval_minutes': self.trading_interval_minutes,
                'market_data': market_data,
                'account_info': {
                    'totalBalance': float(account['total']),
                    'availableBalance': float(account['available']),
                    'returnPercent': 0,  # 可以从数据库计算
                },
                'positions': active_positions,
            }
            
            prompt = generate_trading_prompt(prompt_data)
            
            # 6. 这里可以调用OpenAI进行AI决策
            # decision = await openai_client.create_completion(prompt)
            # 目前只记录提示词
            logger.info(f"✅ AI提示词已生成 ({len(prompt)} 字符)")
            
            # 7. 记录决策到数据库
            async with get_async_session() as session:
                decision_record = AgentDecision(
                    timestamp=datetime.now(),
                    iteration=self.iteration_count,
                    market_analysis=str(market_data),
                    decision="AI决策待实现",
                    actions_taken="[]",
                    account_value=float(account['total']),
                    positions_count=len(active_positions),
                )
                session.add(decision_record)
                await session.commit()
            
            logger.info(f"✅ 交易周期 #{self.iteration_count} 完成\n")
            
        except Exception as e:
            logger.error(f"交易周期异常: {e}")
            import traceback
            traceback.print_exc()
    
    async def _mandatory_risk_checks(
        self,
        positions: List[Dict],
        account: Dict
    ):
        """
        强制风控检查
        
        包括：
        - 账户止损线检查
        - 账户止盈线检查
        - 最大持仓时间检查
        - 极端止损检查
        """
        # 1. 账户级止损/止盈检查
        total_balance = float(account['total']) + float(account.get('unrealized', 0))
        
        # 止损线
        if settings.ACCOUNT_STOP_LOSS_USDT:
            if total_balance <= float(settings.ACCOUNT_STOP_LOSS_USDT):
                logger.error(f"🚨 账户触发止损线！当前: {total_balance:.2f} USDT")
                # 这里应该全部清仓并退出系统
                await self._emergency_close_all(positions, "账户止损")
                return
        
        # 止盈线
        if settings.ACCOUNT_TAKE_PROFIT_USDT:
            if total_balance >= float(settings.ACCOUNT_TAKE_PROFIT_USDT):
                logger.warning(f"🎯 账户触发止盈线！当前: {total_balance:.2f} USDT")
                await self._emergency_close_all(positions, "账户止盈")
                return
        
        # 2. 检查每个持仓
        for pos in positions:
            symbol = pos['contract'].replace('_USDT', '')
            
            # 持仓时间检查（从数据库获取开仓时间）
            await self._check_holding_time(symbol, pos)
            
            # 极端止损检查
            await self._check_extreme_loss(symbol, pos)
    
    async def _check_holding_time(self, symbol: str, position: Dict):
        """检查持仓时间"""
        try:
            async with get_async_session() as session:
                from sqlalchemy import select
                stmt = select(Position).where(Position.symbol == symbol)
                result = await session.execute(stmt)
                db_pos = result.scalar_one_or_none()
                
                if db_pos and db_pos.opened_at:
                    holding_hours = (datetime.now() - db_pos.opened_at).total_seconds() / 3600
                    
                    if holding_hours > RISK_PARAMS.MAX_HOLDING_HOURS:
                        logger.warning(
                            f"⚠️  {symbol} 持仓时间过长 ({holding_hours:.1f}h > {RISK_PARAMS.MAX_HOLDING_HOURS}h)"
                        )
                        # 这里可以强制平仓
        except Exception as e:
            logger.error(f"检查 {symbol} 持仓时间失败: {e}")
    
    async def _check_extreme_loss(self, symbol: str, position: Dict):
        """检查极端止损"""
        try:
            entry_price = float(position.get('entry_price', 0))
            current_price = float(position.get('mark_price', 0))
            size = float(position.get('size', 0))
            leverage = float(position.get('leverage', 1))
            
            if entry_price == 0 or current_price == 0:
                return
            
            side = 'long' if size > 0 else 'short'
            price_change_pct = ((current_price - entry_price) / entry_price * 100) * (1 if side == 'long' else -1)
            pnl_pct = price_change_pct * leverage
            
            if pnl_pct <= RISK_PARAMS.EXTREME_STOP_LOSS_PERCENT:
                logger.error(
                    f"🛑 {symbol} 触发极端止损！"
                    f"亏损: {pnl_pct:.2f}% (阈值: {RISK_PARAMS.EXTREME_STOP_LOSS_PERCENT}%)"
                )
                # 这里应该立即平仓
        except Exception as e:
            logger.error(f"检查 {symbol} 极端止损失败: {e}")
    
    async def _emergency_close_all(self, positions: List[Dict], reason: str):
        """紧急清仓所有持仓"""
        logger.error(f"🚨 紧急清仓: {reason}")
        
        for pos in positions:
            try:
                symbol = pos['contract']
                size = float(pos.get('size', 0))
                
                if size != 0:
                    # 下达市价平仓订单
                    close_size = -size  # 反向平仓
                    await self.exchange.place_order(
                        contract=symbol,
                        size=close_size,
                        price=0,  # 市价
                        reduce_only=True,
                    )
                    logger.info(f"✅ {symbol} 紧急平仓完成")
            except Exception as e:
                logger.error(f"紧急平仓 {symbol} 失败: {e}")
    
    # ========== 代码级保护（波段策略）==========
    
    async def monitor_positions(self):
        """
        持仓监控循环
        
        仅对swing-trend策略启用代码级止损/止盈
        其他策略完全由AI控制
        """
        if self.strategy != 'swing-trend':
            logger.info(f"当前策略 [{self.strategy}] 未启用代码级监控（仅 swing-trend 启用）")
            return
        
        logger.info("启动代码级持仓监控（仅波段策略）")
        logger.info("  检查间隔: 10秒")
        logger.info("  止损监控: 启用")
        logger.info("  移动止盈监控: 启用")
        
        while self._running:
            try:
                # 获取持仓
                positions = await self.exchange.get_positions()
                active_positions = [p for p in positions if float(p.get('size', 0)) != 0]
                
                if not active_positions:
                    self._peak_pnl.clear()
                    await asyncio.sleep(10)
                    continue
                
                # 检查每个持仓
                for pos in active_positions:
                    await self._check_stop_loss(pos)
                    await self._check_trailing_stop(pos)
                
                await asyncio.sleep(10)  # 每10秒检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"持仓监控异常: {e}")
                await asyncio.sleep(10)
    
    async def _check_stop_loss(self, position: Dict):
        """检查止损条件"""
        try:
            symbol = position['contract'].replace('_USDT', '')
            entry_price = float(position.get('entry_price', 0))
            current_price = float(position.get('mark_price', 0))
            size = float(position.get('size', 0))
            leverage = float(position.get('leverage', 1))
            
            if entry_price == 0 or current_price == 0:
                return
            
            side = 'long' if size > 0 else 'short'
            price_change_pct = ((current_price - entry_price) / entry_price * 100) * (1 if side == 'long' else -1)
            pnl_pct = price_change_pct * leverage
            
            # 根据杠杆确定止损阈值
            config = self.strategy_params.codeLevelStopLoss
            if not config:
                return
            
            if leverage >= config.highRisk.minLeverage:
                threshold = config.highRisk.stopLossPercent
                level = "高风险"
            elif leverage >= config.mediumRisk.minLeverage:
                threshold = config.mediumRisk.stopLossPercent
                level = "中风险"
            else:
                threshold = config.lowRisk.stopLossPercent
                level = "低风险"
            
            # 触发止损
            if pnl_pct <= threshold:
                logger.error(
                    f"🛑 【触发止损 - {level}】{symbol} {side}\n"
                    f"  当前亏损: {pnl_pct:.2f}%\n"
                    f"  止损线: {threshold:.2f}%\n"
                    f"  杠杆: {leverage}x"
                )
                # 执行止损平仓
                await self._execute_stop_loss_close(symbol, position)
        
        except Exception as e:
            logger.error(f"止损检查失败: {e}")
    
    async def _check_trailing_stop(self, position: Dict):
        """检查移动止盈条件"""
        try:
            symbol = position['contract'].replace('_USDT', '')
            entry_price = float(position.get('entry_price', 0))
            current_price = float(position.get('mark_price', 0))
            size = float(position.get('size', 0))
            leverage = float(position.get('leverage', 1))
            
            if entry_price == 0 or current_price == 0:
                return
            
            side = 'long' if size > 0 else 'short'
            price_change_pct = ((current_price - entry_price) / entry_price * 100) * (1 if side == 'long' else -1)
            pnl_pct = price_change_pct * leverage
            
            # 更新峰值盈利
            if symbol not in self._peak_pnl:
                self._peak_pnl[symbol] = pnl_pct
            elif pnl_pct > self._peak_pnl[symbol]:
                logger.info(f"{symbol} 更新峰值盈利: {self._peak_pnl[symbol]:.2f}% → {pnl_pct:.2f}%")
                self._peak_pnl[symbol] = pnl_pct
            
            # 检查移动止盈
            config = self.strategy_params.codeLevelTrailingStop
            if not config:
                return
            
            peak = self._peak_pnl[symbol]
            
            # 根据峰值盈利确定回退阈值
            if peak >= config.stage5.minProfit:
                threshold = config.stage5.drawdownPercent
                stage = config.stage5.name
            elif peak >= config.stage4.minProfit:
                threshold = config.stage4.drawdownPercent
                stage = config.stage4.name
            elif peak >= config.stage3.minProfit:
                threshold = config.stage3.drawdownPercent
                stage = config.stage3.name
            elif peak >= config.stage2.minProfit:
                threshold = config.stage2.drawdownPercent
                stage = config.stage2.name
            elif peak >= config.stage1.minProfit:
                threshold = config.stage1.drawdownPercent
                stage = config.stage1.name
            else:
                return  # 未达到最低阈值
            
            # 计算回退
            drawdown = peak - pnl_pct
            
            # 触发移动止盈
            if drawdown >= threshold:
                logger.warning(
                    f"⚠️  【触发移动止盈 - {stage}】{symbol} {side}\n"
                    f"  峰值盈利: {peak:.2f}%\n"
                    f"  当前盈利: {pnl_pct:.2f}%\n"
                    f"  回退幅度: {drawdown:.2f}% (阈值: {threshold:.2f}%)"
                )
                # 执行移动止盈平仓
                await self._execute_trailing_stop_close(symbol, position)
        
        except Exception as e:
            logger.error(f"移动止盈检查失败: {e}")
    
    async def _execute_stop_loss_close(self, symbol: str, position: Dict):
        """执行止损平仓"""
        try:
            contract = position['contract']
            size = float(position.get('size', 0))
            close_size = -size
            
            await self.exchange.place_order(
                contract=contract,
                size=close_size,
                price=0,  # 市价
                reduce_only=True,
            )
            
            logger.info(f"✅ {symbol} 止损平仓订单已下达")
            
            # 清除峰值记录
            if symbol in self._peak_pnl:
                del self._peak_pnl[symbol]
        
        except Exception as e:
            logger.error(f"执行止损平仓失败: {e}")
    
    async def _execute_trailing_stop_close(self, symbol: str, position: Dict):
        """执行移动止盈平仓"""
        try:
            contract = position['contract']
            size = float(position.get('size', 0))
            close_size = -size
            
            await self.exchange.place_order(
                contract=contract,
                size=close_size,
                price=0,  # 市价
                reduce_only=True,
            )
            
            logger.info(f"✅ {symbol} 移动止盈平仓订单已下达")
            
            # 清除峰值记录
            if symbol in self._peak_pnl:
                del self._peak_pnl[symbol]
        
        except Exception as e:
            logger.error(f"执行移动止盈平仓失败: {e}")
    
    # ========== 系统控制 ==========
    
    async def _trading_loop(self):
        """交易循环任务"""
        logger.info(f"交易循环已启动，间隔: {self.trading_interval_minutes} 分钟")
        
        # 立即执行一次
        await self.trading_cycle()
        
        # 定期执行
        interval_seconds = self.trading_interval_minutes * 60
        
        while self._running:
            try:
                await asyncio.sleep(interval_seconds)
                if self._running:
                    await self.trading_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"交易循环异常: {e}")
    
    async def start(self):
        """启动自动交易系统"""
        if self._running:
            logger.warning("自动交易系统已在运行中")
            return
        
        self._running = True
        
        # 启动交易循环
        self._trading_task = asyncio.create_task(self._trading_loop())
        
        # 启动持仓监控（仅波段策略）
        self._monitor_task = asyncio.create_task(self.monitor_positions())
        
        logger.info("🚀 自动交易系统已启动")
    
    async def stop(self):
        """停止自动交易系统"""
        if not self._running:
            logger.warning("自动交易系统未在运行")
            return
        
        self._running = False
        
        # 停止交易循环
        if self._trading_task:
            self._trading_task.cancel()
            try:
                await self._trading_task
            except asyncio.CancelledError:
                pass
        
        # 停止监控任务
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("自动交易系统已停止")


def create_auto_trading_system(exchange_client: ExchangeClient) -> AutoTradingSystem:
    """
    创建自动交易系统实例
    
    Args:
        exchange_client: 交易所客户端
        
    Returns:
        AutoTradingSystem实例
    """
    interval_minutes = int(settings.TRADING_INTERVAL_MINUTES or 5)
    return AutoTradingSystem(exchange_client, interval_minutes)


# 导出
__all__ = [
    'AutoTradingSystem',
    'create_auto_trading_system',
]

