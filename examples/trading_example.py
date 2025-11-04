"""
交易示例脚本

演示如何使用已完成的模块进行交易分析和决策

这个脚本展示了如何：
1. 获取市场数据
2. 计算技术指标
3. 生成AI提示词
4. 分析交易信号
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.exchange import create_exchange_client
from services.market_analysis import (
    calculate_indicators,
    calculate_multi_timeframe_indicators,
)
from agents.trading_agent import (
    get_trading_strategy,
    get_strategy_params,
    generate_trading_prompt,
)
from core.logger import logger


async def analyze_market():
    """市场分析示例"""
    print("\n" + "=" * 80)
    print("📊 加密货币市场分析示例")
    print("=" * 80 + "\n")
    
    # 创建交易所客户端
    client = create_exchange_client()
    
    try:
        # 1. 获取BTC市场数据
        print("📍 步骤1：获取BTC市场数据")
        ticker = await client.get_futures_ticker('BTC')
        print(f"   当前价格: ${ticker['last']}")
        print(f"   24h涨跌: {ticker['change_percentage']}%")
        print(f"   24h成交量: {ticker['volume_24h']}\n")
        
        # 2. 获取多个时间周期的K线数据
        print("📍 步骤2：获取多时间周期K线数据")
        candles_5m = await client.get_futures_candles('BTC', '5m', 100)
        candles_15m = await client.get_futures_candles('BTC', '15m', 100)
        candles_1h = await client.get_futures_candles('BTC', '1h', 100)
        print(f"   5分钟K线: {len(candles_5m)}条")
        print(f"   15分钟K线: {len(candles_15m)}条")
        print(f"   1小时K线: {len(candles_1h)}条\n")
        
        # 3. 计算技术指标
        print("📍 步骤3：计算技术指标")
        indicators = calculate_indicators(candles_5m)
        print(f"   EMA20: ${indicators['ema20']:.2f}")
        print(f"   EMA50: ${indicators['ema50']:.2f}")
        print(f"   MACD: {indicators['macd']:.2f}")
        print(f"   RSI14: {indicators['rsi14']:.2f}")
        print(f"   当前成交量: {indicators['volume']:.0f}\n")
        
        # 4. 多时间周期分析
        print("📍 步骤4：多时间周期分析")
        multi_indicators = calculate_multi_timeframe_indicators({
            '5m': candles_5m,
            '15m': candles_15m,
            '1h': candles_1h,
        })
        
        for timeframe, ind in multi_indicators.items():
            trend = "看涨" if ind['ema20'] > ind['ema50'] else "看跌"
            print(f"   {timeframe}: {trend}, RSI={ind['rsi14']:.1f}")
        print()
        
        # 5. 获取当前策略参数
        print("📍 步骤5：获取交易策略参数")
        strategy = get_trading_strategy()
        params = get_strategy_params(strategy)
        print(f"   当前策略: {params.name}")
        print(f"   杠杆范围: {params.leverage_min}-{params.leverage_max}x")
        print(f"   仓位范围: {params.position_size_min}-{params.position_size_max}%")
        print(f"   止损范围: {params.stop_loss_low}% ~ {params.stop_loss_high}%\n")
        
        # 6. 生成AI提示词
        print("📍 步骤6：生成AI决策提示词")
        
        # 获取账户信息
        account = await client.get_account()
        positions = await client.get_positions()
        
        prompt_data = {
            'minutes_elapsed': 60,
            'iteration': 1,
            'interval_minutes': 5,
            'market_data': {
                'BTC': {
                    **indicators,
                    'price': float(ticker['last']),
                    'fundingRate': float(ticker.get('funding_rate', 0)),
                    'timeframes': multi_indicators,
                }
            },
            'account_info': {
                'totalBalance': float(account['total']),
                'availableBalance': float(account['available']),
                'returnPercent': 0,
            },
            'positions': positions,
        }
        
        prompt = generate_trading_prompt(prompt_data)
        print(f"   提示词长度: {len(prompt)} 字符")
        print(f"   包含市场数据: ✅")
        print(f"   包含多时间框架: ✅")
        print(f"   包含账户信息: ✅\n")
        
        # 7. 简单的交易信号分析
        print("📍 步骤7：交易信号分析")
        
        # 趋势判断
        if indicators['ema20'] > indicators['ema50']:
            trend_signal = "上升趋势 📈"
        elif indicators['ema20'] < indicators['ema50']:
            trend_signal = "下降趋势 📉"
        else:
            trend_signal = "震荡 ↔️"
        
        # RSI判断
        if indicators['rsi14'] > 70:
            rsi_signal = "超买 ⚠️"
        elif indicators['rsi14'] < 30:
            rsi_signal = "超卖 ⚠️"
        else:
            rsi_signal = "正常 ✅"
        
        # MACD判断
        if indicators['macd'] > 0:
            macd_signal = "多头 🟢"
        else:
            macd_signal = "空头 🔴"
        
        print(f"   趋势: {trend_signal}")
        print(f"   RSI状态: {rsi_signal}")
        print(f"   MACD: {macd_signal}\n")
        
        # 8. 多周期一致性检查
        print("📍 步骤8：多周期趋势一致性")
        bullish_count = 0
        bearish_count = 0
        
        for tf, ind in multi_indicators.items():
            if ind['ema20'] > ind['ema50']:
                bullish_count += 1
                print(f"   {tf}: 看涨")
            else:
                bearish_count += 1
                print(f"   {tf}: 看跌")
        
        if bullish_count >= 2:
            consistency = "多周期看涨信号 🚀"
        elif bearish_count >= 2:
            consistency = "多周期看跌信号 📉"
        else:
            consistency = "信号不一致，观望 ⏸️"
        
        print(f"\n   一致性结论: {consistency}\n")
        
        # 总结
        print("=" * 80)
        print("✅ 市场分析完成！")
        print("=" * 80)
        print("\n💡 提示：")
        print("   - 这是一个示例脚本，展示如何使用已完成的模块")
        print("   - 实际交易需要更复杂的决策逻辑")
        print("   - 可以将提示词发送给OpenAI进行AI决策")
        print("   - 建议在测试网环境下测试\n")
        
    finally:
        await client.close()


async def simple_trading_loop():
    """简单的交易循环示例（不实际下单）"""
    print("\n" + "=" * 80)
    print("🔄 交易循环示例（模拟）")
    print("=" * 80 + "\n")
    
    client = create_exchange_client()
    
    try:
        print("开始交易循环监控（按Ctrl+C停止）...\n")
        
        iteration = 1
        while iteration <= 3:  # 只运行3次作为示例
            print(f"--- 迭代 #{iteration} ---")
            
            # 获取市场数据
            ticker = await client.get_futures_ticker('BTC')
            candles = await client.get_futures_candles('BTC', '5m', 100)
            
            # 计算指标
            indicators = calculate_indicators(candles)
            
            # 显示关键信息
            print(f"时间: {indicators.get('timestamp', 'N/A')}")
            print(f"价格: ${float(ticker['last']):.2f}")
            print(f"EMA20: ${indicators['ema20']:.2f}")
            print(f"RSI14: {indicators['rsi14']:.2f}")
            
            # 简单的信号判断
            if indicators['rsi14'] > 70:
                print("⚠️  RSI超买，可能回调")
            elif indicators['rsi14'] < 30:
                print("⚠️  RSI超卖，可能反弹")
            else:
                print("✅ RSI正常范围")
            
            print()
            
            # 等待下一次迭代
            if iteration < 3:
                print("等待5秒...\n")
                await asyncio.sleep(5)
            
            iteration += 1
        
        print("=" * 80)
        print("✅ 示例循环完成")
        print("=" * 80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    finally:
        await client.close()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🚀 Open NOF1.ai - Python版交易示例")
    print("=" * 80)
    
    print("\n请选择示例：")
    print("1. 市场分析示例")
    print("2. 交易循环示例")
    print("3. 全部运行")
    
    # 自动运行市场分析示例
    choice = "1"
    
    if choice in ["1", "3"]:
        await analyze_market()
    
    if choice in ["2", "3"]:
        await simple_trading_loop()
    
    print("\n" + "=" * 80)
    print("👋 感谢使用！")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())

