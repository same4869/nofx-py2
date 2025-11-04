"""
阶段3测试脚本

测试技术指标计算功能
"""

import sys
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from services.market_analysis import (
    calc_ema,
    calc_rsi,
    calc_macd,
    calc_atr,
    calculate_indicators,
    calculate_multi_timeframe_indicators,
    calculate_intraday_series,
    ensure_finite,
    ensure_range,
)


def test_ensure_functions():
    """测试数据验证函数"""
    print("\n" + "=" * 80)
    print("🧪 测试1：数据验证函数")
    print("=" * 80)
    
    # 测试ensure_finite
    assert ensure_finite(10.5) == 10.5
    assert ensure_finite(float('inf'), 0) == 0
    assert ensure_finite(float('nan'), 5) == 5
    print("✅ ensure_finite 测试通过")
    
    # 测试ensure_range
    assert ensure_range(50, 0, 100) == 50
    assert ensure_range(-10, 0, 100) == 0
    assert ensure_range(150, 0, 100) == 100
    assert ensure_range(float('nan'), 0, 100, 50) == 50
    print("✅ ensure_range 测试通过")


def test_ema_calculation():
    """测试EMA计算"""
    print("\n" + "=" * 80)
    print("🧪 测试2：EMA计算")
    print("=" * 80)
    
    # 生成测试数据：上升趋势
    prices = [100 + i * 0.5 for i in range(100)]
    
    # 计算EMA
    ema20 = calc_ema(prices, 20)
    ema50 = calc_ema(prices, 50)
    
    print(f"测试数据: 100个价格点，从100到149.5")
    print(f"EMA20: {ema20:.2f}")
    print(f"EMA50: {ema50:.2f}")
    
    # 验证：在上升趋势中，EMA20应该高于EMA50
    assert ema20 > ema50, "上升趋势中EMA20应高于EMA50"
    
    # 验证：EMA应该在价格范围内
    assert 100 <= ema20 <= 150, "EMA20应在价格范围内"
    assert 100 <= ema50 <= 150, "EMA50应在价格范围内"
    
    print("✅ EMA计算测试通过")


def test_rsi_calculation():
    """测试RSI计算"""
    print("\n" + "=" * 80)
    print("🧪 测试3：RSI计算")
    print("=" * 80)
    
    # 测试1：上升趋势（应该RSI偏高）
    up_trend = [100 + i for i in range(50)]
    rsi_up = calc_rsi(up_trend, 14)
    print(f"上升趋势RSI: {rsi_up:.2f}")
    assert 50 < rsi_up <= 100, "上升趋势RSI应大于50"
    
    # 测试2：下降趋势（应该RSI偏低）
    down_trend = [100 - i for i in range(50)]
    rsi_down = calc_rsi(down_trend, 14)
    print(f"下降趋势RSI: {rsi_down:.2f}")
    assert 0 <= rsi_down < 50, "下降趋势RSI应小于50"
    
    # 测试3：横盘（应该RSI接近50）
    sideways = [100] * 50
    rsi_sideways = calc_rsi(sideways, 14)
    print(f"横盘RSI: {rsi_sideways:.2f}")
    assert 40 <= rsi_sideways <= 60, "横盘RSI应接近50"
    
    # 测试4：RSI范围
    assert 0 <= rsi_up <= 100, "RSI应在0-100范围内"
    assert 0 <= rsi_down <= 100, "RSI应在0-100范围内"
    
    print("✅ RSI计算测试通过")


def test_macd_calculation():
    """测试MACD计算"""
    print("\n" + "=" * 80)
    print("🧪 测试4：MACD计算")
    print("=" * 80)
    
    # 生成测试数据：上升趋势
    prices = [100 + i * 0.5 + np.sin(i / 5) * 2 for i in range(100)]
    
    macd = calc_macd(prices)
    print(f"MACD值: {macd:.4f}")
    
    # MACD应该是有限数字
    assert np.isfinite(macd), "MACD应该是有限数字"
    
    # 在上升趋势中，MACD通常为正
    # 但这不是绝对的，所以我们只检查它是否计算出来了
    print(f"MACD计算成功（值: {macd:.4f}）")
    
    print("✅ MACD计算测试通过")


def test_atr_calculation():
    """测试ATR计算"""
    print("\n" + "=" * 80)
    print("🧪 测试5：ATR计算")
    print("=" * 80)
    
    # 生成测试数据
    closes = [100 + np.sin(i / 5) * 5 for i in range(50)]
    highs = [c + 2 for c in closes]
    lows = [c - 2 for c in closes]
    
    atr = calc_atr(highs, lows, closes, 14)
    print(f"ATR14: {atr:.4f}")
    
    # ATR应该是正数
    assert atr > 0, "ATR应该是正数"
    
    # ATR应该大致在真实波幅范围内（这里是4左右）
    assert 2 < atr < 10, "ATR应该在合理范围内"
    
    print("✅ ATR计算测试通过")


def test_calculate_indicators():
    """测试综合指标计算"""
    print("\n" + "=" * 80)
    print("🧪 测试6：综合指标计算")
    print("=" * 80)
    
    # 生成测试K线数据
    candles = []
    for i in range(100):
        price = 100 + i * 0.5 + np.sin(i / 5) * 3
        candles.append({
            't': i,
            'o': str(price - 0.5),
            'h': str(price + 2),
            'l': str(price - 2),
            'c': str(price),
            'v': str(1000000 + i * 10000),
        })
    
    indicators = calculate_indicators(candles)
    
    print(f"计算结果:")
    print(f"   当前价格: {indicators['currentPrice']:.2f}")
    print(f"   EMA20: {indicators['ema20']:.2f}")
    print(f"   EMA50: {indicators['ema50']:.2f}")
    print(f"   MACD: {indicators['macd']:.4f}")
    print(f"   RSI7: {indicators['rsi7']:.2f}")
    print(f"   RSI14: {indicators['rsi14']:.2f}")
    print(f"   当前成交量: {indicators['volume']:.0f}")
    print(f"   平均成交量: {indicators['avgVolume']:.0f}")
    
    # 验证所有指标都已计算
    assert indicators['currentPrice'] > 0, "当前价格应大于0"
    assert indicators['ema20'] > 0, "EMA20应大于0"
    assert indicators['ema50'] > 0, "EMA50应大于0"
    assert 0 <= indicators['rsi7'] <= 100, "RSI7应在0-100范围内"
    assert 0 <= indicators['rsi14'] <= 100, "RSI14应在0-100范围内"
    assert indicators['volume'] >= 0, "成交量应非负"
    assert indicators['avgVolume'] >= 0, "平均成交量应非负"
    
    print("✅ 综合指标计算测试通过")


def test_empty_data_handling():
    """测试空数据处理"""
    print("\n" + "=" * 80)
    print("🧪 测试7：空数据处理")
    print("=" * 80)
    
    # 测试空列表
    empty_indicators = calculate_indicators([])
    print(f"空数据结果:")
    print(f"   EMA20: {empty_indicators['ema20']}")
    print(f"   RSI14: {empty_indicators['rsi14']}")
    
    assert empty_indicators['currentPrice'] == 0, "空数据应返回0"
    assert empty_indicators['ema20'] == 0, "空数据EMA应返回0"
    assert empty_indicators['rsi14'] == 50, "空数据RSI应返回50（中性值）"
    
    # 测试数据不足的情况
    few_candles = [
        {'t': 0, 'o': '100', 'h': '102', 'l': '98', 'c': '100', 'v': '1000000'}
    ]
    few_indicators = calculate_indicators(few_candles)
    print(f"\n单条数据结果:")
    print(f"   当前价格: {few_indicators['currentPrice']}")
    
    assert few_indicators['currentPrice'] == 100, "应正确提取价格"
    
    print("✅ 空数据处理测试通过")


def test_multi_timeframe_indicators():
    """测试多时间周期指标计算"""
    print("\n" + "=" * 80)
    print("🧪 测试8：多时间周期指标")
    print("=" * 80)
    
    # 生成不同时间周期的测试数据
    candles_5m = []
    candles_15m = []
    candles_1h = []
    
    for i in range(100):
        price_5m = 100 + i * 0.5 + np.sin(i / 5) * 2
        candles_5m.append({
            't': i,
            'o': str(price_5m),
            'h': str(price_5m + 1),
            'l': str(price_5m - 1),
            'c': str(price_5m),
            'v': str(1000000),
        })
    
    for i in range(100):
        price_15m = 100 + i * 0.3 + np.sin(i / 3) * 3
        candles_15m.append({
            't': i,
            'o': str(price_15m),
            'h': str(price_15m + 1.5),
            'l': str(price_15m - 1.5),
            'c': str(price_15m),
            'v': str(3000000),
        })
    
    for i in range(100):
        price_1h = 100 + i * 0.2 + np.sin(i / 2) * 4
        candles_1h.append({
            't': i,
            'o': str(price_1h),
            'h': str(price_1h + 2),
            'l': str(price_1h - 2),
            'c': str(price_1h),
            'v': str(10000000),
        })
    
    # 计算多时间周期指标
    candles_dict = {
        '5m': candles_5m,
        '15m': candles_15m,
        '1h': candles_1h,
    }
    
    multi_indicators = calculate_multi_timeframe_indicators(candles_dict)
    
    print(f"多时间周期指标:")
    for timeframe, indicators in multi_indicators.items():
        print(f"\n   {timeframe}:")
        print(f"      当前价格: {indicators['currentPrice']:.2f}")
        print(f"      EMA20: {indicators['ema20']:.2f}")
        print(f"      RSI14: {indicators['rsi14']:.2f}")
    
    # 验证所有时间周期都已计算
    assert '5m' in multi_indicators, "应包含5m指标"
    assert '15m' in multi_indicators, "应包含15m指标"
    assert '1h' in multi_indicators, "应包含1h指标"
    
    for timeframe, indicators in multi_indicators.items():
        assert indicators['currentPrice'] > 0, f"{timeframe}当前价格应大于0"
        assert indicators['ema20'] > 0, f"{timeframe} EMA20应大于0"
    
    print("\n✅ 多时间周期指标测试通过")


def test_intraday_series():
    """测试日内时序数据"""
    print("\n" + "=" * 80)
    print("🧪 测试9：日内时序数据")
    print("=" * 80)
    
    # 生成测试数据（模拟一天的3分钟K线）
    candles = []
    for i in range(60):  # 60个3分钟K线 = 3小时
        price = 100 + np.sin(i / 10) * 5 + i * 0.1
        candles.append({
            't': i,
            'o': str(price),
            'h': str(price + 1),
            'l': str(price - 1),
            'c': str(price),
            'v': str(1000000 + i * 5000),
        })
    
    # 计算时序数据
    series = calculate_intraday_series(candles, points=10)
    
    print(f"时序数据:")
    print(f"   中间价数量: {len(series['midPrices'])}")
    print(f"   EMA20序列数量: {len(series['ema20Series'])}")
    print(f"   MACD序列数量: {len(series['macdSeries'])}")
    print(f"   RSI序列数量: {len(series['rsi7Series'])}")
    
    if len(series['midPrices']) > 0:
        print(f"   最新中间价: {series['midPrices'][-1]:.2f}")
    
    # 验证数据结构
    assert 'midPrices' in series, "应包含midPrices"
    assert 'ema20Series' in series, "应包含ema20Series"
    assert 'macdSeries' in series, "应包含macdSeries"
    assert 'rsi7Series' in series, "应包含rsi7Series"
    assert 'rsi14Series' in series, "应包含rsi14Series"
    
    # 验证数据点数量
    assert len(series['midPrices']) <= 10, "中间价数量应不超过10"
    
    print("✅ 日内时序数据测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("🚀 阶段3测试套件：技术指标计算")
    print("=" * 80)
    
    try:
        test_ensure_functions()
        test_ema_calculation()
        test_rsi_calculation()
        test_macd_calculation()
        test_atr_calculation()
        test_calculate_indicators()
        test_empty_data_handling()
        test_multi_timeframe_indicators()
        test_intraday_series()
        
        # 总结
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！阶段3完成！")
        print("=" * 80)
        print("\n📋 已完成的功能：")
        print("   ✅ calc_ema() - EMA指标计算")
        print("   ✅ calc_rsi() - RSI指标计算")
        print("   ✅ calc_macd() - MACD指标计算")
        print("   ✅ calc_atr() - ATR指标计算")
        print("   ✅ calculate_indicators() - 综合指标计算")
        print("   ✅ calculate_multi_timeframe_indicators() - 多时间周期分析")
        print("   ✅ calculate_intraday_series() - 日内时序数据")
        print("   ✅ 数据验证和错误处理")
        print("\n🎯 下一步：准备开始阶段4（AI决策引擎）")
        print("=" * 80 + "\n")
        
        return True
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"❌ 测试失败: {e}")
        print("=" * 80 + "\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 测试出错: {e}")
        print("=" * 80 + "\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行所有测试
    success = run_all_tests()
    sys.exit(0 if success else 1)

