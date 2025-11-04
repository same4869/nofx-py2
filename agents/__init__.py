"""
AI交易代理模块

包含策略参数、提示词生成和AI决策逻辑
"""

from .trading_agent import (
    TradingStrategy,
    StrategyParams,
    AccountRiskConfig,
    get_account_risk_config,
    get_trading_strategy,
    get_strategy_params,
    generate_trading_prompt,
)

__all__ = [
    'TradingStrategy',
    'StrategyParams',
    'AccountRiskConfig',
    'get_account_risk_config',
    'get_trading_strategy',
    'get_strategy_params',
    'generate_trading_prompt',
]

