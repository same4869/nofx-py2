"""
数据库模型定义

参考TypeScript版本的schema.ts
使用SQLAlchemy ORM定义所有数据表
确保与TypeScript版本的表结构完全一致
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    Index, UniqueConstraint
)
from sqlalchemy.sql import func

from core.database import Base


class Trade(Base):
    """
    交易记录表
    
    对应TypeScript: src/database/schema.ts - Trade接口
    """
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False, comment="订单ID")
    symbol = Column(String, nullable=False, comment="交易币种")
    side = Column(String, nullable=False, comment="方向：long/short")
    type = Column(String, nullable=False, comment="类型：open/close")
    price = Column(Float, nullable=False, comment="成交价格")
    quantity = Column(Float, nullable=False, comment="成交数量")
    leverage = Column(Integer, nullable=False, comment="杠杆倍数")
    pnl = Column(Float, nullable=True, comment="盈亏（仅平仓）")
    fee = Column(Float, nullable=True, comment="手续费")
    timestamp = Column(String, nullable=False, comment="时间戳（ISO格式）")
    status = Column(String, nullable=False, default='pending', comment="状态：pending/filled/cancelled")
    
    # 索引
    __table_args__ = (
        Index('idx_trades_timestamp', 'timestamp'),
        Index('idx_trades_symbol', 'symbol'),
    )
    
    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, side={self.side}, type={self.type}, price={self.price})>"


class Position(Base):
    """
    持仓表
    
    对应TypeScript: src/database/schema.ts - Position接口
    """
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, unique=True, comment="交易币种（唯一）")
    quantity = Column(Float, nullable=False, comment="持仓数量")
    entry_price = Column(Float, nullable=False, comment="开仓价格")
    current_price = Column(Float, nullable=False, comment="当前价格")
    liquidation_price = Column(Float, nullable=False, comment="强平价格")
    unrealized_pnl = Column(Float, nullable=False, comment="未实现盈亏")
    leverage = Column(Integer, nullable=False, comment="杠杆倍数")
    side = Column(String, nullable=False, comment="方向：long/short")
    profit_target = Column(Float, nullable=True, comment="止盈目标")
    stop_loss = Column(Float, nullable=True, comment="止损价格")
    tp_order_id = Column(String, nullable=True, comment="止盈订单ID")
    sl_order_id = Column(String, nullable=True, comment="止损订单ID")
    entry_order_id = Column(String, nullable=False, comment="开仓订单ID")
    opened_at = Column(String, nullable=False, comment="开仓时间（ISO格式）")
    confidence = Column(Float, nullable=True, comment="信心度")
    risk_usd = Column(Float, nullable=True, comment="风险金额（USD）")
    peak_pnl_percent = Column(Float, default=0.0, comment="历史最高盈亏百分比")
    partial_close_percentage = Column(Float, default=0.0, comment="已通过分批止盈平掉的百分比(0-100)")
    
    def __repr__(self):
        return f"<Position(symbol={self.symbol}, side={self.side}, pnl={self.unrealized_pnl})>"


class AccountHistory(Base):
    """
    账户历史表
    
    对应TypeScript: src/database/schema.ts - AccountHistory接口
    """
    __tablename__ = 'account_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, nullable=False, comment="时间戳（ISO格式）")
    total_value = Column(Float, nullable=False, comment="总资产")
    available_cash = Column(Float, nullable=False, comment="可用资金")
    unrealized_pnl = Column(Float, nullable=False, comment="未实现盈亏")
    realized_pnl = Column(Float, nullable=False, comment="已实现盈亏")
    return_percent = Column(Float, nullable=False, comment="收益率（%）")
    sharpe_ratio = Column(Float, nullable=True, comment="夏普比率")
    
    # 索引
    __table_args__ = (
        Index('idx_history_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AccountHistory(total={self.total_value}, return={self.return_percent}%)>"


class TradingSignal(Base):
    """
    技术指标表
    
    对应TypeScript: src/database/schema.ts - TradingSignal接口
    """
    __tablename__ = 'trading_signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, comment="交易币种")
    timestamp = Column(String, nullable=False, comment="时间戳（ISO格式）")
    price = Column(Float, nullable=False, comment="价格")
    ema_20 = Column(Float, nullable=False, comment="EMA20")
    ema_50 = Column(Float, nullable=True, comment="EMA50")
    macd = Column(Float, nullable=False, comment="MACD")
    rsi_7 = Column(Float, nullable=False, comment="RSI7")
    rsi_14 = Column(Float, nullable=False, comment="RSI14")
    volume = Column(Float, nullable=False, comment="成交量")
    open_interest = Column(Float, nullable=True, comment="未平仓合约")
    funding_rate = Column(Float, nullable=True, comment="资金费率")
    atr_3 = Column(Float, nullable=True, comment="ATR3")
    atr_14 = Column(Float, nullable=True, comment="ATR14")
    
    # 索引
    __table_args__ = (
        Index('idx_signals_timestamp', 'timestamp'),
        Index('idx_signals_symbol', 'symbol'),
    )
    
    def __repr__(self):
        return f"<TradingSignal(symbol={self.symbol}, price={self.price})>"


class AgentDecision(Base):
    """
    AI决策记录表
    
    对应TypeScript: src/database/schema.ts - AgentDecision接口
    """
    __tablename__ = 'agent_decisions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, nullable=False, comment="时间戳（ISO格式）")
    iteration = Column(Integer, nullable=False, comment="迭代次数")
    market_analysis = Column(Text, nullable=False, comment="市场分析（JSON）")
    decision = Column(Text, nullable=False, comment="AI决策内容")
    actions_taken = Column(Text, nullable=False, comment="执行的操作（JSON）")
    account_value = Column(Float, nullable=False, comment="账户价值")
    positions_count = Column(Integer, nullable=False, comment="持仓数量")
    
    # 索引
    __table_args__ = (
        Index('idx_decisions_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AgentDecision(iteration={self.iteration}, account={self.account_value})>"


class SystemConfig(Base):
    """
    系统配置表
    
    对应TypeScript: src/database/schema.ts - SystemConfig接口
    用于存储运行时配置（如止损止盈线等）
    """
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True, comment="配置键")
    value = Column(String, nullable=False, comment="配置值")
    updated_at = Column(String, nullable=False, comment="更新时间（ISO格式）")
    
    def __repr__(self):
        return f"<SystemConfig(key={self.key}, value={self.value})>"


# 导出所有模型（用于数据库初始化）
__all__ = [
    'Base',
    'Trade',
    'Position',
    'AccountHistory',
    'TradingSignal',
    'AgentDecision',
    'SystemConfig',
]


if __name__ == "__main__":
    # 打印所有表的信息
    print("\n" + "=" * 80)
    print("📋 数据库表结构")
    print("=" * 80 + "\n")
    
    for model in [Trade, Position, AccountHistory, TradingSignal, AgentDecision, SystemConfig]:
        print(f"表名: {model.__tablename__}")
        print(f"模型: {model.__name__}")
        print(f"列数: {len(model.__table__.columns)}")
        print("-" * 80)
    
    print("\n✅ 模型定义测试完成")

