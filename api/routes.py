"""
API路由

提供RESTful API端点，用于Web监控界面

功能：
- 账户总览
- 持仓查询
- 交易记录
- AI决策日志
- 交易统计
- 实时价格

对应TypeScript: src/api/routes.ts
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from core.logger import logger
from core.database import get_async_session
from core.models import Trade, Position, AccountHistory, AgentDecision
from services.exchange import ExchangeClient
from config.risk_params import RISK_PARAMS


def create_api_app(exchange_client: ExchangeClient) -> FastAPI:
    """
    创建FastAPI应用
    
    Args:
        exchange_client: 交易所客户端实例
        
    Returns:
        FastAPI应用实例
    """
    app = FastAPI(
        title="Open NOF1.ai API",
        description="AI驱动的加密货币自动交易系统 - Web API",
        version="1.0.0",
    )
    
    # 静态文件服务
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # ========== API路由 ==========
    
    @app.get("/")
    async def index():
        """主页 - 返回监控界面"""
        index_file = Path(__file__).parent.parent / "static" / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Open NOF1.ai API", "version": "1.0.0"}
    
    @app.get("/api/account")
    async def get_account():
        """
        获取账户总览
        
        Returns:
            账户信息，包括总资产、可用余额、未实现盈亏等
        """
        try:
            # 1. 从交易所获取实时账户数据
            account = await exchange_client.get_account()
            
            # 2. 从数据库获取初始资金
            async with get_async_session() as session:
                from sqlalchemy import select
                stmt = select(AccountHistory).order_by(AccountHistory.timestamp.asc()).limit(1)
                result = await session.execute(stmt)
                first_record = result.scalar_one_or_none()
                
                initial_balance = float(first_record.total_value) if first_record else 100.0
            
            # 3. 计算收益
            unrealized_pnl = float(account.get('unrealized', 0))
            total_balance = float(account.get('total', 0))
            
            # 收益率（基于总资产，不包含未实现盈亏）
            return_percent = ((total_balance - initial_balance) / initial_balance) * 100
            
            return {
                "totalBalance": total_balance,
                "availableBalance": float(account.get('available', 0)),
                "positionMargin": float(account.get('margin', 0)),
                "unrealisedPnl": unrealized_pnl,
                "returnPercent": return_percent,
                "initialBalance": initial_balance,
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"获取账户信息失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/positions")
    async def get_positions():
        """
        获取当前持仓
        
        Returns:
            当前持仓列表
        """
        try:
            # 1. 从交易所获取实时持仓
            gate_positions = await exchange_client.get_positions()
            
            # 2. 从数据库获取止损止盈信息
            async with get_async_session() as session:
                from sqlalchemy import select
                stmt = select(Position)
                result = await session.execute(stmt)
                db_positions = result.scalars().all()
                
                # 创建映射
                db_pos_map = {pos.symbol: pos for pos in db_positions}
            
            # 3. 过滤并格式化持仓
            positions = []
            for p in gate_positions:
                size = float(p.get('size', 0))
                if size == 0:
                    continue
                
                symbol = p['contract'].replace('_USDT', '')
                db_pos = db_pos_map.get(symbol)
                
                positions.append({
                    "symbol": symbol,
                    "quantity": abs(size),
                    "entryPrice": float(p.get('entry_price', 0)),
                    "currentPrice": float(p.get('mark_price', 0)),
                    "liquidationPrice": float(p.get('liq_price', 0)),
                    "unrealizedPnl": float(p.get('unrealized_pnl', 0)),
                    "leverage": int(p.get('leverage', 1)),
                    "side": "long" if size > 0 else "short",
                    "openValue": float(p.get('margin', 0)),
                    "profitTarget": float(db_pos.profit_target) if db_pos and db_pos.profit_target else None,
                    "stopLoss": float(db_pos.stop_loss) if db_pos and db_pos.stop_loss else None,
                    "openedAt": db_pos.opened_at.isoformat() if db_pos and db_pos.opened_at else datetime.now().isoformat(),
                })
            
            return {"positions": positions}
            
        except Exception as e:
            logger.error(f"获取持仓信息失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/history")
    async def get_history(limit: Optional[int] = Query(None, description="限制返回数量")):
        """
        获取账户价值历史（用于绘图）
        
        Args:
            limit: 可选，限制返回数量
            
        Returns:
            账户历史记录列表
        """
        try:
            async with get_async_session() as session:
                from sqlalchemy import select
                
                stmt = select(AccountHistory).order_by(AccountHistory.timestamp.desc())
                if limit:
                    stmt = stmt.limit(limit)
                
                result = await session.execute(stmt)
                records = result.scalars().all()
                
                # 反转顺序（从旧到新）
                history = [
                    {
                        "timestamp": record.timestamp.isoformat(),
                        "totalValue": float(record.total_value),
                        "unrealizedPnl": float(record.unrealized_pnl) if record.unrealized_pnl else 0,
                        "returnPercent": float(record.return_percent) if record.return_percent else 0,
                    }
                    for record in reversed(records)
                ]
                
                return {"history": history}
                
        except Exception as e:
            logger.error(f"获取账户历史失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/trades")
    async def get_trades(
        limit: int = Query(10, description="限制返回数量"),
        symbol: Optional[str] = Query(None, description="筛选特定币种")
    ):
        """
        获取交易记录
        
        Args:
            limit: 限制返回数量，默认10
            symbol: 可选，筛选特定币种
            
        Returns:
            交易记录列表
        """
        try:
            async with get_async_session() as session:
                from sqlalchemy import select
                
                stmt = select(Trade).order_by(Trade.timestamp.desc())
                
                if symbol:
                    stmt = stmt.where(Trade.symbol == symbol)
                
                stmt = stmt.limit(limit)
                
                result = await session.execute(stmt)
                trades_list = result.scalars().all()
                
                trades = [
                    {
                        "id": trade.id,
                        "orderId": trade.order_id,
                        "symbol": trade.symbol,
                        "side": trade.side,
                        "type": trade.type,
                        "price": float(trade.price) if trade.price else 0,
                        "quantity": float(trade.quantity) if trade.quantity else 0,
                        "leverage": int(trade.leverage) if trade.leverage else 1,
                        "pnl": float(trade.pnl) if trade.pnl else None,
                        "fee": float(trade.fee) if trade.fee else 0,
                        "timestamp": trade.timestamp.isoformat() if trade.timestamp else None,
                        "status": trade.status,
                    }
                    for trade in trades_list
                ]
                
                return {"trades": trades}
                
        except Exception as e:
            logger.error(f"获取交易记录失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/logs")
    async def get_logs(limit: int = Query(20, description="限制返回数量")):
        """
        获取AI决策日志
        
        Args:
            limit: 限制返回数量，默认20
            
        Returns:
            AI决策日志列表
        """
        try:
            async with get_async_session() as session:
                from sqlalchemy import select
                
                stmt = select(AgentDecision).order_by(AgentDecision.timestamp.desc()).limit(limit)
                result = await session.execute(stmt)
                decisions = result.scalars().all()
                
                logs = [
                    {
                        "id": decision.id,
                        "timestamp": decision.timestamp.isoformat() if decision.timestamp else None,
                        "iteration": decision.iteration,
                        "decision": decision.decision,
                        "actionsTaken": decision.actions_taken,
                        "accountValue": float(decision.account_value) if decision.account_value else 0,
                        "positionsCount": decision.positions_count,
                    }
                    for decision in decisions
                ]
                
                return {"logs": logs}
                
        except Exception as e:
            logger.error(f"获取决策日志失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/stats")
    async def get_stats():
        """
        获取交易统计
        
        Returns:
            交易统计数据
        """
        try:
            async with get_async_session() as session:
                from sqlalchemy import select, func
                
                # 统计总交易次数（只统计有盈亏的平仓交易）
                stmt_total = select(func.count()).select_from(Trade).where(
                    Trade.type == 'close',
                    Trade.pnl.isnot(None)
                )
                total_trades = await session.scalar(stmt_total) or 0
                
                # 统计盈利交易
                stmt_win = select(func.count()).select_from(Trade).where(
                    Trade.type == 'close',
                    Trade.pnl.isnot(None),
                    Trade.pnl > 0
                )
                win_trades = await session.scalar(stmt_win) or 0
                
                # 计算胜率
                win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
                
                # 计算总盈亏
                stmt_pnl = select(func.sum(Trade.pnl)).where(
                    Trade.type == 'close',
                    Trade.pnl.isnot(None)
                )
                total_pnl = await session.scalar(stmt_pnl) or 0
                
                # 最大单笔盈利
                stmt_max_win = select(func.max(Trade.pnl)).where(
                    Trade.type == 'close',
                    Trade.pnl.isnot(None)
                )
                max_win = await session.scalar(stmt_max_win) or 0
                
                # 最大单笔亏损
                stmt_max_loss = select(func.min(Trade.pnl)).where(
                    Trade.type == 'close',
                    Trade.pnl.isnot(None)
                )
                max_loss = await session.scalar(stmt_max_loss) or 0
                
                return {
                    "totalTrades": total_trades,
                    "winTrades": win_trades,
                    "lossTrades": total_trades - win_trades,
                    "winRate": win_rate,
                    "totalPnl": float(total_pnl),
                    "maxWin": float(max_win),
                    "maxLoss": float(max_loss),
                }
                
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/prices")
    async def get_prices(
        symbols: str = Query("BTC,ETH,SOL", description="币种列表，逗号分隔")
    ):
        """
        获取多个币种的实时价格
        
        Args:
            symbols: 币种列表，逗号分隔，默认"BTC,ETH,SOL"
            
        Returns:
            价格字典
        """
        try:
            symbol_list = [s.strip() for s in symbols.split(',')]
            prices = {}
            
            for symbol in symbol_list:
                try:
                    ticker = await exchange_client.get_futures_ticker(symbol)
                    prices[symbol] = float(ticker['last'])
                except Exception as e:
                    logger.warning(f"获取 {symbol} 价格失败: {e}")
                    prices[symbol] = 0
            
            return {"prices": prices}
            
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


# 导出
__all__ = ['create_api_app']

