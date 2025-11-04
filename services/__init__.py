"""
服务层模块

包含交易所API、技术分析等服务
"""

from .exchange import (
    ExchangeClient,
    create_exchange_client,
    close_exchange_client,
)

from .market_analysis import (
    calc_ema,
    calc_rsi,
    calc_macd,
    calc_atr,
    calculate_indicators,
    calculate_multi_timeframe_indicators,
    calculate_intraday_series,
)

__all__ = [
    # 交易所API
    'ExchangeClient',
    'create_exchange_client',
    'close_exchange_client',
    
    # 技术指标
    'calc_ema',
    'calc_rsi',
    'calc_macd',
    'calc_atr',
    'calculate_indicators',
    'calculate_multi_timeframe_indicators',
    'calculate_intraday_series',
]

