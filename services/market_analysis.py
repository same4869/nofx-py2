"""
市场数据分析模块

提供技术指标计算和多时间周期分析功能
支持EMA、MACD、RSI、ATR等常用技术指标

参考TypeScript版本：src/scheduler/tradingLoop.ts
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
try:
    import pandas_ta as ta
except ImportError:
    ta = None  # pandas_ta是可选的

from core.logger import logger


def ensure_finite(value: float, default_value: float = 0.0) -> float:
    """
    确保数值是有效的有限数字，否则返回默认值
    
    Args:
        value: 待检查的数值
        default_value: 默认值
        
    Returns:
        有限数字或默认值
    """
    if not np.isfinite(value) or np.isnan(value):
        return default_value
    return float(value)


def ensure_range(
    value: float, 
    min_val: float, 
    max_val: float, 
    default_value: Optional[float] = None
) -> float:
    """
    确保数值在指定范围内
    
    Args:
        value: 待检查的数值
        min_val: 最小值
        max_val: 最大值
        default_value: 默认值（如果为None，使用中间值）
        
    Returns:
        范围内的数值
    """
    if not np.isfinite(value) or np.isnan(value):
        return default_value if default_value is not None else (min_val + max_val) / 2
    
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return float(value)


def calc_ema(prices: List[float], period: int) -> float:
    """
    计算指数移动平均线（EMA）
    
    Args:
        prices: 价格列表
        period: 周期
        
    Returns:
        EMA值
        
    算法说明：
    EMA = Price(t) * k + EMA(t-1) * (1 - k)
    其中 k = 2 / (period + 1)
    """
    if not prices or len(prices) == 0:
        return 0.0
    
    # 转换为numpy数组并过滤无效值
    prices_arr = np.array([p for p in prices if np.isfinite(p)])
    if len(prices_arr) == 0:
        return 0.0
    
    k = 2.0 / (period + 1)
    ema = prices_arr[0]
    
    for i in range(1, len(prices_arr)):
        ema = prices_arr[i] * k + ema * (1 - k)
    
    return ensure_finite(ema, 0.0)


def calc_rsi(prices: List[float], period: int = 14) -> float:
    """
    计算相对强弱指数（RSI）
    
    Args:
        prices: 价格列表
        period: 周期，默认14
        
    Returns:
        RSI值（0-100）
        
    算法说明：
    RSI = 100 - (100 / (1 + RS))
    其中 RS = 平均涨幅 / 平均跌幅
    """
    if not prices or len(prices) < period + 1:
        return 50.0  # 数据不足，返回中性值
    
    # 转换为numpy数组并过滤无效值
    prices_arr = np.array([p for p in prices if np.isfinite(p)])
    if len(prices_arr) < period + 1:
        return 50.0
    
    gains = 0.0
    losses = 0.0
    
    # 计算最近period个周期的涨跌
    for i in range(len(prices_arr) - period, len(prices_arr)):
        change = prices_arr[i] - prices_arr[i - 1]
        if change > 0:
            gains += change
        else:
            losses -= change  # losses是正数
    
    avg_gain = gains / period
    avg_loss = losses / period
    
    # 避免除零
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    # 确保RSI在0-100范围内
    return ensure_range(rsi, 0.0, 100.0, 50.0)


def calc_macd(prices: List[float]) -> float:
    """
    计算MACD指标
    
    Args:
        prices: 价格列表
        
    Returns:
        MACD值（快线 - 慢线）
        
    算法说明：
    MACD = EMA(12) - EMA(26)
    """
    if not prices or len(prices) < 26:
        return 0.0  # 数据不足
    
    # 转换为numpy数组并过滤无效值
    prices_arr = [p for p in prices if np.isfinite(p)]
    if len(prices_arr) < 26:
        return 0.0
    
    ema12 = calc_ema(prices_arr, 12)
    ema26 = calc_ema(prices_arr, 26)
    macd = ema12 - ema26
    
    return ensure_finite(macd, 0.0)


def calc_atr(
    highs: List[float], 
    lows: List[float], 
    closes: List[float], 
    period: int = 14
) -> float:
    """
    计算平均真实波幅（ATR）
    
    Args:
        highs: 最高价列表
        lows: 最低价列表
        closes: 收盘价列表
        period: 周期，默认14
        
    Returns:
        ATR值
        
    算法说明：
    TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
    ATR = average(TR, period)
    """
    if (not highs or not lows or not closes or 
        len(highs) < period + 1 or 
        len(lows) < period + 1 or 
        len(closes) < period + 1):
        return 0.0
    
    # 转换为numpy数组并过滤无效值
    highs_arr = np.array([h for h in highs if np.isfinite(h)])
    lows_arr = np.array([l for l in lows if np.isfinite(l)])
    closes_arr = np.array([c for c in closes if np.isfinite(c)])
    
    min_len = min(len(highs_arr), len(lows_arr), len(closes_arr))
    if min_len < period + 1:
        return 0.0
    
    # 确保三个数组长度一致
    highs_arr = highs_arr[:min_len]
    lows_arr = lows_arr[:min_len]
    closes_arr = closes_arr[:min_len]
    
    # 计算真实波幅
    true_ranges = []
    for i in range(1, len(highs_arr)):
        high = highs_arr[i]
        low = lows_arr[i]
        prev_close = closes_arr[i - 1]
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)
    
    # 计算最近period个周期的平均
    recent_tr = true_ranges[-period:]
    if len(recent_tr) == 0:
        return 0.0
    
    atr = sum(recent_tr) / len(recent_tr)
    
    return ensure_finite(atr, 0.0)


def calculate_indicators(candles: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    计算技术指标（综合）
    
    Args:
        candles: K线数据列表，每个元素为字典，包含：
            - t: 时间戳
            - o: 开盘价（字符串）
            - h: 最高价（字符串）
            - l: 最低价（字符串）
            - c: 收盘价（字符串）
            - v: 成交量（字符串）
            
    Returns:
        技术指标字典，包含：
            - currentPrice: 当前价格
            - ema20: 20周期EMA
            - ema50: 50周期EMA
            - macd: MACD值
            - rsi7: 7周期RSI
            - rsi14: 14周期RSI
            - volume: 当前成交量
            - avgVolume: 平均成交量
            
    对应TypeScript: calculateIndicators()
    """
    if not candles or len(candles) == 0:
        return {
            'currentPrice': 0.0,
            'ema20': 0.0,
            'ema50': 0.0,
            'macd': 0.0,
            'rsi7': 50.0,
            'rsi14': 50.0,
            'atr': 0.0,
            'volume': 0.0,
            'avgVolume': 0.0,
        }
    
    # 提取价格和成交量数据
    closes = []
    highs = []
    lows = []
    volumes = []
    
    for candle in candles:
        # 支持字典格式（Gate.io API返回）
        if isinstance(candle, dict):
            # 收盘价
            close = float(candle.get('c', 0))
            if np.isfinite(close):
                closes.append(close)
            
            # 最高价
            high = float(candle.get('h', 0))
            if np.isfinite(high):
                highs.append(high)
            
            # 最低价
            low = float(candle.get('l', 0))
            if np.isfinite(low):
                lows.append(low)
            
            # 成交量
            vol = float(candle.get('v', 0))
            if np.isfinite(vol) and vol >= 0:
                volumes.append(vol)
        
        # 支持列表格式（兼容旧代码）
        elif isinstance(candle, (list, tuple)) and len(candle) >= 6:
            close = float(candle[4])  # close
            if np.isfinite(close):
                closes.append(close)
            
            high = float(candle[2])   # high
            if np.isfinite(high):
                highs.append(high)
            
            low = float(candle[3])    # low
            if np.isfinite(low):
                lows.append(low)
            
            vol = float(candle[5])    # volume
            if np.isfinite(vol) and vol >= 0:
                volumes.append(vol)
    
    # 如果没有有效数据，返回默认值
    if len(closes) == 0:
        return {
            'currentPrice': 0.0,
            'ema20': 0.0,
            'ema50': 0.0,
            'macd': 0.0,
            'rsi7': 50.0,
            'rsi14': 50.0,
            'atr': 0.0,
            'volume': 0.0,
            'avgVolume': 0.0,
        }
    
    # 计算各项指标
    current_price = closes[-1] if closes else 0.0
    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    macd = calc_macd(closes)
    rsi7 = calc_rsi(closes, 7)
    rsi14 = calc_rsi(closes, 14)
    atr = calc_atr(highs, lows, closes, 14)  # 添加ATR计算
    current_volume = volumes[-1] if volumes else 0.0
    avg_volume = sum(volumes) / len(volumes) if volumes else 0.0
    
    return {
        'currentPrice': ensure_finite(current_price, 0.0),
        'ema20': ensure_finite(ema20, 0.0),
        'ema50': ensure_finite(ema50, 0.0),
        'macd': ensure_finite(macd, 0.0),
        'rsi7': ensure_range(rsi7, 0.0, 100.0, 50.0),
        'rsi14': ensure_range(rsi14, 0.0, 100.0, 50.0),
        'atr': ensure_finite(atr, 0.0),  # 添加ATR到返回结果
        'volume': ensure_finite(current_volume, 0.0),
        'avgVolume': ensure_finite(avg_volume, 0.0),
    }


def calculate_indicators_pandas(candles: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    使用pandas-ta计算技术指标（如果可用）
    
    这是一个备选方案，使用pandas-ta库提供的现成指标计算
    如果pandas-ta不可用，会自动回退到手动计算方法
    
    Args:
        candles: K线数据列表
        
    Returns:
        技术指标字典
    """
    if ta is None:
        # pandas-ta不可用，使用手动计算
        return calculate_indicators(candles)
    
    if not candles or len(candles) == 0:
        return calculate_indicators(candles)
    
    try:
        # 转换为DataFrame
        df = pd.DataFrame(candles)
        
        # 确保数值列是float类型
        for col in ['o', 'h', 'l', 'c', 'v']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 重命名列以匹配pandas-ta要求
        df = df.rename(columns={
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
        })
        
        # 计算指标
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.macd(append=True)
        df.ta.rsi(length=7, append=True)
        df.ta.rsi(length=14, append=True)
        
        # 提取最新值
        result = {
            'currentPrice': ensure_finite(df['close'].iloc[-1], 0.0),
            'ema20': ensure_finite(df['EMA_20'].iloc[-1], 0.0),
            'ema50': ensure_finite(df['EMA_50'].iloc[-1], 0.0),
            'macd': ensure_finite(df['MACD_12_26_9'].iloc[-1], 0.0),
            'rsi7': ensure_range(df['RSI_7'].iloc[-1], 0.0, 100.0, 50.0),
            'rsi14': ensure_range(df['RSI_14'].iloc[-1], 0.0, 100.0, 50.0),
            'volume': ensure_finite(df['volume'].iloc[-1], 0.0),
            'avgVolume': ensure_finite(df['volume'].mean(), 0.0),
        }
        
        return result
        
    except Exception as e:
        logger.warning(f"pandas-ta计算指标失败，回退到手动计算: {e}")
        return calculate_indicators(candles)


def calculate_multi_timeframe_indicators(
    candles_dict: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Dict[str, float]]:
    """
    计算多时间周期指标
    
    Args:
        candles_dict: 多时间周期K线数据，格式为：
            {
                '1m': [candle1, candle2, ...],
                '5m': [candle1, candle2, ...],
                '1h': [candle1, candle2, ...],
                ...
            }
            
    Returns:
        多时间周期指标字典，格式为：
            {
                '1m': {indicators},
                '5m': {indicators},
                '1h': {indicators},
                ...
            }
            
    对应TypeScript: collectMarketData() 中的多时间框架分析
    """
    result = {}
    
    for timeframe, candles in candles_dict.items():
        try:
            indicators = calculate_indicators(candles)
            result[timeframe] = indicators
            logger.debug(f"计算 {timeframe} 指标成功: EMA20={indicators['ema20']:.2f}")
        except Exception as e:
            logger.error(f"计算 {timeframe} 指标失败: {e}")
            result[timeframe] = calculate_indicators([])  # 返回默认值
    
    return result


def calculate_intraday_series(candles: List[Dict[str, Any]], points: int = 10) -> Dict[str, List[float]]:
    """
    计算日内时序数据
    
    Args:
        candles: K线数据列表（至少60个数据点）
        points: 返回的数据点数量，默认10
        
    Returns:
        时序数据字典，包含：
            - midPrices: 中间价序列
            - ema20Series: EMA20序列
            - macdSeries: MACD序列
            - rsi7Series: RSI7序列
            - rsi14Series: RSI14序列
            
    对应TypeScript: calculateIntradaySeries()
    """
    if not candles or len(candles) == 0:
        return {
            'midPrices': [],
            'ema20Series': [],
            'macdSeries': [],
            'rsi7Series': [],
            'rsi14Series': [],
        }
    
    # 提取收盘价
    closes = []
    for candle in candles:
        if isinstance(candle, dict):
            close = float(candle.get('c', 0))
            if np.isfinite(close):
                closes.append(close)
    
    if len(closes) < points:
        return {
            'midPrices': closes,
            'ema20Series': [],
            'macdSeries': [],
            'rsi7Series': [],
            'rsi14Series': [],
        }
    
    # 计算每个数据点的指标
    ema20_series = []
    macd_series = []
    rsi7_series = []
    rsi14_series = []
    
    # 使用滑动窗口计算
    for i in range(max(0, len(closes) - points), len(closes)):
        window = closes[:i + 1]
        
        if len(window) >= 26:  # 足够计算MACD
            ema20_series.append(calc_ema(window, 20))
            macd_series.append(calc_macd(window))
        
        if len(window) >= 15:  # 足够计算RSI14
            rsi7_series.append(calc_rsi(window, 7))
            rsi14_series.append(calc_rsi(window, 14))
    
    return {
        'midPrices': closes[-points:] if len(closes) >= points else closes,
        'ema20Series': ema20_series,
        'macdSeries': macd_series,
        'rsi7Series': rsi7_series,
        'rsi14Series': rsi14_series,
    }


if __name__ == "__main__":
    # 测试技术指标计算
    print("\n" + "=" * 80)
    print("🧪 测试技术指标计算")
    print("=" * 80 + "\n")
    
    # 生成测试数据
    test_prices = [100 + i + np.sin(i / 5) * 5 for i in range(100)]
    
    # 测试EMA
    print("📍 测试1：EMA计算")
    ema20 = calc_ema(test_prices, 20)
    ema50 = calc_ema(test_prices, 50)
    print(f"   EMA20: {ema20:.2f}")
    print(f"   EMA50: {ema50:.2f}")
    print(f"   ✅ EMA计算成功\n")
    
    # 测试RSI
    print("📍 测试2：RSI计算")
    rsi14 = calc_rsi(test_prices, 14)
    print(f"   RSI14: {rsi14:.2f}")
    print(f"   ✅ RSI计算成功\n")
    
    # 测试MACD
    print("📍 测试3：MACD计算")
    macd = calc_macd(test_prices)
    print(f"   MACD: {macd:.2f}")
    print(f"   ✅ MACD计算成功\n")
    
    # 测试ATR
    print("📍 测试4：ATR计算")
    test_highs = [p + 2 for p in test_prices]
    test_lows = [p - 2 for p in test_prices]
    atr = calc_atr(test_highs, test_lows, test_prices, 14)
    print(f"   ATR14: {atr:.2f}")
    print(f"   ✅ ATR计算成功\n")
    
    # 测试综合指标计算
    print("📍 测试5：综合指标计算")
    test_candles = [
        {
            't': i,
            'o': str(test_prices[i]),
            'h': str(test_highs[i]),
            'l': str(test_lows[i]),
            'c': str(test_prices[i]),
            'v': str(1000000 + i * 10000),
        }
        for i in range(len(test_prices))
    ]
    
    indicators = calculate_indicators(test_candles)
    print(f"   当前价格: {indicators['currentPrice']:.2f}")
    print(f"   EMA20: {indicators['ema20']:.2f}")
    print(f"   EMA50: {indicators['ema50']:.2f}")
    print(f"   MACD: {indicators['macd']:.2f}")
    print(f"   RSI7: {indicators['rsi7']:.2f}")
    print(f"   RSI14: {indicators['rsi14']:.2f}")
    print(f"   成交量: {indicators['volume']:.0f}")
    print(f"   ✅ 综合指标计算成功\n")
    
    print("=" * 80)
    print("🎉 所有测试通过！")
    print("=" * 80 + "\n")

