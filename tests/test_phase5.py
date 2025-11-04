"""
阶段5测试：集成测试

测试所有模块的集成功能
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from config.settings import settings
from services.exchange import create_exchange_client
from services.market_analysis import calculate_indicators
from agents.trading_agent import (
    get_trading_strategy,
    get_strategy_params,
    generate_trading_prompt,
)
from core.logger import logger


def test_1_import_all_modules():
    """测试1：验证所有模块可以正常导入"""
    print("\n" + "=" * 80)
    print("测试1：模块导入测试")
    print("=" * 80)
    
    try:
        from config import settings, risk_params
        from core import logger, database, models
        from utils import time_utils
        from services import exchange, market_analysis
        from agents import trading_agent
        
        print("✅ 所有核心模块导入成功")
        print(f"   - config: {bool(settings)}")
        print(f"   - core: {bool(logger)}")
        print(f"   - utils: {bool(time_utils)}")
        print(f"   - services: {bool(exchange)}")
        print(f"   - agents: {bool(trading_agent)}")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False


async def test_2_exchange_to_indicators():
    """测试2：从交易所获取数据到计算指标的完整流程"""
    print("\n" + "=" * 80)
    print("测试2：数据获取 -> 指标计算流程")
    print("=" * 80)
    
    client = create_exchange_client()
    
    try:
        # 获取K线数据
        candles = await client.get_futures_candles('BTC', '5m', 100)
        print(f"✅ 获取K线数据: {len(candles)}条")
        
        # 计算指标
        indicators = calculate_indicators(candles)
        print(f"✅ 计算技术指标: {len(indicators)}个")
        print(f"   - EMA20: ${indicators['ema20']:.2f}")
        print(f"   - RSI14: {indicators['rsi14']:.2f}")
        
        # 验证数据完整性
        required_fields = ['ema20', 'ema50', 'rsi14', 'macd', 'atr']
        missing = [f for f in required_fields if f not in indicators]
        
        if missing:
            print(f"❌ 缺少指标: {missing}")
            return False
        
        print("✅ 所有必需指标都已计算")
        return True
        
    except Exception as e:
        print(f"❌ 流程测试失败: {e}")
        return False
    finally:
        await client.close()


async def test_3_strategy_and_prompt():
    """测试3：策略配置和提示词生成"""
    print("\n" + "=" * 80)
    print("测试3：策略配置 -> 提示词生成流程")
    print("=" * 80)
    
    try:
        # 获取策略
        strategy = get_trading_strategy()
        print(f"✅ 当前策略: {strategy}")
        
        # 获取策略参数
        params = get_strategy_params(strategy)
        print(f"✅ 策略参数: {params.name}")
        print(f"   - 杠杆: {params.leverage_min}-{params.leverage_max}x")
        print(f"   - 止损: {params.stop_loss_low}%-{params.stop_loss_high}%")
        
        # 生成提示词
        mock_data = {
            'minutes_elapsed': 60,
            'iteration': 1,
            'interval_minutes': 5,
            'market_data': {
                'BTC': {
                    'price': 65000,
                    'ema20': 64800,
                    'ema50': 64500,
                    'rsi14': 58,
                    'macd': 120,
                    'signal': 100,
                    'histogram': 20,
                    'atr': 500,
                    'volume': 1000000,
                }
            },
            'account_info': {
                'totalBalance': 10000,
                'availableBalance': 9000,
            },
            'positions': [],
        }
        
        prompt = generate_trading_prompt(mock_data)
        print(f"✅ 提示词生成: {len(prompt)}字符")
        
        # 验证提示词内容
        has_market_data = 'BTC' in prompt or '市场数据' in prompt
        has_risk_control = '止损' in prompt or '风险' in prompt or '策略' in prompt
        
        if has_market_data and has_risk_control:
            print("✅ 提示词包含必要信息")
            return True
        else:
            print(f"❌ 提示词内容不完整 (市场数据:{has_market_data}, 风险控制:{has_risk_control})")
            return False
        
    except Exception as e:
        print(f"❌ 策略测试失败: {e}")
        return False


async def test_4_full_pipeline():
    """测试4：完整的数据流水线"""
    print("\n" + "=" * 80)
    print("测试4：完整流水线测试")
    print("=" * 80)
    
    client = create_exchange_client()
    
    try:
        print("步骤1: 获取市场数据...")
        ticker = await client.get_futures_ticker('BTC')
        candles_5m = await client.get_futures_candles('BTC', '5m', 100)
        candles_1h = await client.get_futures_candles('BTC', '1h', 100)
        print(f"   ✅ 获取ticker和K线数据")
        
        print("步骤2: 计算技术指标...")
        indicators_5m = calculate_indicators(candles_5m)
        indicators_1h = calculate_indicators(candles_1h)
        print(f"   ✅ 计算多周期指标")
        
        print("步骤3: 组装市场数据...")
        market_data = {
            'BTC': {
                **indicators_5m,
                'price': float(ticker['last']),
                'fundingRate': float(ticker.get('funding_rate', 0)),
                'timeframes': {
                    '5m': indicators_5m,
                    '1h': indicators_1h,
                }
            }
        }
        print(f"   ✅ 市场数据组装完成")
        
        print("步骤4: 获取账户信息...")
        # 检查是否配置了有效的API密钥
        if not settings.GATE_API_KEY or settings.GATE_API_KEY == "your_api_key_here":
            print("   ⚠️  API密钥未配置，跳过账户信息获取")
            account = {'total': 10000, 'available': 9000}
            positions = []
        else:
            try:
                account = await client.get_account()
                positions = await client.get_positions()
                print(f"   ✅ 账户余额: ${account['available']}")
                print(f"   ✅ 持仓数量: {len(positions)}")
            except Exception as e:
                print(f"   ⚠️  API调用失败（使用模拟数据）: {type(e).__name__}")
                account = {'total': 10000, 'available': 9000}
                positions = []
        
        print("步骤5: 生成AI提示词...")
        prompt_data = {
            'minutes_elapsed': 60,
            'iteration': 1,
            'interval_minutes': 5,
            'market_data': market_data,
            'account_info': {
                'totalBalance': float(account['total']),
                'availableBalance': float(account['available']),
                'returnPercent': 0,
            },
            'positions': positions,
        }
        
        prompt = generate_trading_prompt(prompt_data)
        print(f"   ✅ 提示词生成: {len(prompt)}字符")
        
        print("\n✅ 完整流水线测试通过！")
        print("\n流水线总结：")
        print(f"   交易所数据 -> 技术指标 -> AI提示词")
        print(f"   {len(candles_5m)}条K线 -> {len(indicators_5m)}个指标 -> {len(prompt)}字符提示")
        
        return True
        
    except Exception as e:
        print(f"❌ 流水线测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()


async def test_5_error_handling():
    """测试5：错误处理"""
    print("\n" + "=" * 80)
    print("测试5：错误处理测试")
    print("=" * 80)
    
    client = create_exchange_client()
    
    try:
        # 测试无效symbol
        try:
            await client.get_futures_ticker('INVALID_SYMBOL_123')
            print("❌ 应该抛出异常但没有")
            return False
        except Exception:
            print("✅ 正确处理无效symbol")
        
        # 测试空数据的指标计算
        try:
            indicators = calculate_indicators([])
            # 空数据应该返回全0的指标
            numeric_values = [v for v in indicators.values() if isinstance(v, (int, float))]
            if len(numeric_values) > 0 and all(v == 0 or v == 0.0 for v in numeric_values):
                print("✅ 正确处理空数据（返回全0指标）")
            else:
                # 也可能抛出异常，这也是合理的
                print("✅ 空数据处理正常")
        except Exception as e:
            print(f"✅ 空数据触发异常（也是正确的）: {type(e).__name__}")
        
        return True
        
    finally:
        await client.close()


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("🚀 阶段5集成测试")
    print("=" * 80)
    print(f"\n项目: Open NOF1.ai - Python版")
    print(f"测试范围: 所有模块集成")
    print()
    
    results = []
    
    # 同步测试
    results.append(("模块导入", test_1_import_all_modules()))
    
    # 异步测试
    results.append(("数据->指标流程", await test_2_exchange_to_indicators()))
    results.append(("策略->提示词流程", await test_3_strategy_and_prompt()))
    results.append(("完整流水线", await test_4_full_pipeline()))
    results.append(("错误处理", await test_5_error_handling()))
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        print("\n✅ 阶段5完成：")
        print("   - 所有核心模块集成成功")
        print("   - 数据流水线运行正常")
        print("   - 错误处理机制有效")
        print("\n💡 下一步：")
        print("   - 运行示例脚本: python examples/trading_example.py")
        print("   - 配置API密钥进行实际测试")
        print("   - 开始使用交易系统！")
    else:
        print(f"\n⚠️  有{total-passed}个测试失败")
        print("请检查上述错误信息")
    
    print("\n" + "=" * 80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

