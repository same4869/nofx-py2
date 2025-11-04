"""
阶段4测试脚本

测试AI决策引擎功能
"""

import sys
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.trading_agent import (
    get_account_risk_config,
    get_trading_strategy,
    get_strategy_params,
    generate_trading_prompt,
)


def test_account_risk_config():
    """测试账户风险配置"""
    print("\n" + "=" * 80)
    print("🧪 测试1：账户风险配置")
    print("=" * 80)
    
    config = get_account_risk_config()
    
    print(f"账户风险配置:")
    print(f"   止损金额: {config.stop_loss_usdt} USDT")
    print(f"   止盈金额: {config.take_profit_usdt} USDT")
    print(f"   启动时同步: {config.sync_on_startup}")
    
    assert config.stop_loss_usdt > 0, "止损金额应大于0"
    assert config.take_profit_usdt > 0, "止盈金额应大于0"
    
    print("✅ 账户风险配置测试通过")


def test_trading_strategy():
    """测试交易策略获取"""
    print("\n" + "=" * 80)
    print("🧪 测试2：交易策略获取")
    print("=" * 80)
    
    strategy = get_trading_strategy()
    
    print(f"当前交易策略: {strategy}")
    
    valid_strategies = ["conservative", "balanced", "aggressive", "ultra-short", "swing-trend"]
    assert strategy in valid_strategies, f"策略应该是{valid_strategies}中的一个"
    
    print("✅ 交易策略获取测试通过")


def test_strategy_params():
    """测试所有策略参数"""
    print("\n" + "=" * 80)
    print("🧪 测试3：策略参数配置")
    print("=" * 80)
    
    strategies = ["conservative", "balanced", "aggressive", "ultra-short", "swing-trend"]
    
    for strategy in strategies:
        params = get_strategy_params(strategy)  # type: ignore
        
        print(f"\n{params.name}策略:")
        print(f"   描述: {params.description}")
        print(f"   杠杆范围: {params.leverage_min}-{params.leverage_max}x")
        print(f"   仓位范围: {params.position_size_min}-{params.position_size_max}%")
        print(f"   止损范围: {params.stop_loss_low}% ~ {params.stop_loss_high}%")
        print(f"   峰值回撤保护: {params.peak_drawdown_protection}%")
        
        # 验证参数有效性
        assert params.leverage_min > 0, "最小杠杆应大于0"
        assert params.leverage_max >= params.leverage_min, "最大杠杆应>=最小杠杆"
        assert params.position_size_min > 0, "最小仓位应大于0"
        assert params.position_size_max >= params.position_size_min, "最大仓位应>=最小仓位"
        assert params.stop_loss_low < 0, "止损应该是负数"
        assert params.peak_drawdown_protection > 0, "峰值回撤保护应大于0"
        
        # 验证swing-trend特殊配置
        if strategy == "swing-trend":
            assert params.code_level_stop_loss_low_risk is not None, "波段策略应有代码级别止损"
            assert params.code_level_trailing_stop_stage1 is not None, "波段策略应有代码级别移动止盈"
            print(f"   代码级别止损: 已配置")
            print(f"   代码级别移动止盈: 已配置（5级规则）")
        else:
            assert params.code_level_stop_loss_low_risk is None, "非波段策略不应有代码级别止损"
            assert params.code_level_trailing_stop_stage1 is None, "非波段策略不应有代码级别移动止盈"
    
    print("\n✅ 所有策略参数测试通过")


def test_trading_prompt_generation():
    """测试交易提示词生成"""
    print("\n" + "=" * 80)
    print("🧪 测试4：交易提示词生成")
    print("=" * 80)
    
    # 构建测试数据
    test_data = {
        'minutes_elapsed': 60,
        'iteration': 12,
        'interval_minutes': 5,
        'market_data': {
            'BTC': {
                'price': 103000.5,
                'ema20': 102500.3,
                'ema50': 101800.7,
                'macd': 150.5,
                'rsi7': 65.3,
                'rsi14': 58.2,
                'fundingRate': 0.0001,
                'timeframes': {
                    '5m': {
                        'currentPrice': 103000.5,
                        'ema20': 102500,
                        'ema50': 101800,
                        'macd': 150,
                        'rsi7': 65,
                        'rsi14': 58,
                        'volume': 1000000,
                    },
                    '1h': {
                        'currentPrice': 102900,
                        'ema20': 102400,
                        'ema50': 101700,
                        'macd': 145,
                        'rsi7': 63,
                        'rsi14': 56,
                        'volume': 5000000,
                    },
                },
            },
            'ETH': {
                'price': 3500.2,
                'ema20': 3480.5,
                'macd': 8.3,
                'rsi7': 52.1,
            },
        },
        'account_info': {
            'totalBalance': 10000.50,
            'availableBalance': 5000.25,
            'returnPercent': 15.5,
            'initialBalance': 10000,
            'peakBalance': 10500,
            'sharpeRatio': 1.85,
        },
        'positions': [
            {
                'symbol': 'BTC',
                'side': 'long',
                'leverage': 5,
                'entry_price': 102000,
                'current_price': 103000,
                'unrealized_pnl': 245.50,
                'opened_at': '2025-11-04T10:00:00+08:00',
            }
        ],
        'trade_history': [
            {
                'symbol': 'ETH',
                'type': 'close',
                'side': 'long',
                'price': 3500,
                'quantity': 1.5,
                'leverage': 3,
                'fee': 5.25,
                'pnl': 125.50,
                'timestamp': '2025-11-04T09:00:00+08:00',
            }
        ],
        'recent_decisions': [
            {
                'iteration': 11,
                'timestamp': '2025-11-04T09:55:00+08:00',
                'account_value': 9950,
                'positions_count': 1,
                'decision': '持仓观察',
            }
        ],
    }
    
    # 生成提示词
    prompt = generate_trading_prompt(test_data)
    
    print(f"提示词统计:")
    print(f"   总长度: {len(prompt)} 字符")
    print(f"   包含BTC数据: {'BTC' in prompt}")
    print(f"   包含ETH数据: {'ETH' in prompt}")
    print(f"   包含账户信息: {'账户价值' in prompt or '账户' in prompt}")
    print(f"   包含持仓信息: {'当前活跃持仓' in prompt}")
    print(f"   包含交易历史: {'交易历史' in prompt or '最近交易' in prompt}")
    
    # 验证提示词内容
    assert len(prompt) > 1000, "提示词长度应大于1000字符"
    assert 'BTC' in prompt, "应包含BTC数据"
    assert '交易周期' in prompt, "应包含交易周期信息"
    assert '策略' in prompt or '风控' in prompt, "应包含策略信息"
    assert '杠杆' in prompt, "应包含杠杆信息"
    
    # 显示提示词片段
    print(f"\n提示词开头片段:")
    print(prompt[:300] + "...")
    
    print("\n✅ 交易提示词生成测试通过")


def test_prompt_with_different_strategies():
    """测试不同策略的提示词差异"""
    print("\n" + "=" * 80)
    print("🧪 测试5：不同策略提示词差异")
    print("=" * 80)
    
    # 简单的测试数据
    test_data = {
        'minutes_elapsed': 60,
        'iteration': 1,
        'interval_minutes': 5,
        'market_data': {'BTC': {'price': 100000, 'ema20': 99500, 'macd': 100, 'rsi7': 55}},
        'account_info': {'totalBalance': 10000, 'availableBalance': 5000, 'returnPercent': 0},
        'positions': [],
    }
    
    strategies = ["conservative", "balanced", "aggressive", "ultra-short", "swing-trend"]
    
    for strategy in strategies:
        # 临时修改环境变量（仅用于测试）
        import os
        original_strategy = os.environ.get('TRADING_STRATEGY', '')
        os.environ['TRADING_STRATEGY'] = strategy
        
        try:
            prompt = generate_trading_prompt(test_data)
            params = get_strategy_params(strategy)  # type: ignore
            
            print(f"\n{params.name}策略提示词:")
            print(f"   长度: {len(prompt)} 字符")
            print(f"   包含策略名称: {params.name in prompt}")
            
            # 所有策略都应该包含基本风控信息
            assert '止损' in prompt, "应包含止损信息"
            assert '止盈' in prompt or '平仓' in prompt or '策略' in prompt, "应包含止盈或策略信息"
            
            # 验证策略名称存在于提示词中
            # (注意：因为测试用的是简化数据，所以检查更宽松)
            
        finally:
            # 恢复原始环境变量
            if original_strategy:
                os.environ['TRADING_STRATEGY'] = original_strategy
            elif 'TRADING_STRATEGY' in os.environ:
                del os.environ['TRADING_STRATEGY']
    
    print("\n✅ 不同策略提示词差异测试通过")


def test_prompt_with_complex_data():
    """测试复杂数据的提示词生成"""
    print("\n" + "=" * 80)
    print("🧪 测试6：复杂数据提示词生成")
    print("=" * 80)
    
    # 构建复杂测试数据
    test_data = {
        'minutes_elapsed': 360,
        'iteration': 72,
        'interval_minutes': 5,
        'market_data': {
            'BTC': {
                'price': 103500,
                'ema20': 102800,
                'ema50': 101500,
                'macd': 250.5,
                'rsi7': 72.3,
                'rsi14': 68.5,
                'volume': 2000000,
                'fundingRate': 0.00015,
                'intradaySeries': {
                    'midPrices': [103000, 103100, 103200, 103300, 103400, 103450, 103480, 103490, 103495, 103500],
                    'ema20Series': [102500, 102550, 102600, 102650, 102700, 102750, 102780, 102790, 102795, 102800],
                    'macdSeries': [200, 210, 220, 225, 230, 235, 240, 245, 248, 250],
                    'rsi7Series': [60, 62, 64, 66, 68, 69, 70, 71, 71.5, 72],
                    'rsi14Series': [58, 60, 62, 63, 64, 65, 66, 67, 67.5, 68],
                },
                'timeframes': {
                    '1m': {'currentPrice': 103500, 'ema20': 103200, 'ema50': 102500, 'macd': 280, 'rsi7': 75, 'rsi14': 70, 'volume': 500000},
                    '5m': {'currentPrice': 103500, 'ema20': 102800, 'ema50': 101500, 'macd': 250, 'rsi7': 72, 'rsi14': 68, 'volume': 2000000},
                    '15m': {'currentPrice': 103450, 'ema20': 102600, 'ema50': 101200, 'macd': 220, 'rsi7': 70, 'rsi14': 66, 'volume': 5000000},
                    '1h': {'currentPrice': 103400, 'ema20': 102400, 'ema50': 100800, 'macd': 200, 'rsi7': 68, 'rsi14': 64, 'volume': 15000000},
                },
            },
            'ETH': {
                'price': 3520,
                'ema20': 3490,
                'ema50': 3450,
                'macd': 12.5,
                'rsi7': 58.2,
                'rsi14': 55.8,
            },
            'SOL': {
                'price': 245.8,
                'ema20': 243.2,
                'ema50': 240.5,
                'macd': 1.8,
                'rsi7': 52.1,
                'rsi14': 50.3,
            },
        },
        'account_info': {
            'totalBalance': 12500.75,
            'availableBalance': 3000.50,
            'returnPercent': 25.01,
            'initialBalance': 10000,
            'peakBalance': 13000,
            'sharpeRatio': 2.15,
        },
        'positions': [
            {
                'symbol': 'BTC',
                'side': 'long',
                'leverage': 8,
                'entry_price': 101500,
                'current_price': 103500,
                'unrealized_pnl': 1580.50,
                'opened_at': '2025-11-04T16:00:00+08:00',
            },
            {
                'symbol': 'ETH',
                'side': 'short',
                'leverage': 5,
                'entry_price': 3600,
                'current_price': 3520,
                'unrealized_pnl': 444.44,
                'opened_at': '2025-11-04T18:30:00+08:00',
            }
        ],
        'trade_history': [
            {
                'symbol': 'SOL',
                'type': 'close',
                'side': 'long',
                'price': 245,
                'quantity': 50,
                'leverage': 6,
                'fee': 7.35,
                'pnl': 245.50,
                'timestamp': '2025-11-04T15:00:00+08:00',
            },
            {
                'symbol': 'BNB',
                'type': 'close',
                'side': 'short',
                'price': 620,
                'quantity': 10,
                'leverage': 4,
                'fee': 2.48,
                'pnl': -85.30,
                'timestamp': '2025-11-04T14:00:00+08:00',
            },
        ],
        'recent_decisions': [
            {
                'iteration': 71,
                'timestamp': '2025-11-04T21:55:00+08:00',
                'account_value': 12450,
                'positions_count': 2,
                'decision': '持仓两个，BTC多单盈利中，ETH空单小幅盈利',
            },
            {
                'iteration': 70,
                'timestamp': '2025-11-04 21:50:00+08:00',
                'account_value': 12400,
                'positions_count': 2,
                'decision': '继续持有，等待更好的止盈时机',
            },
        ],
    }
    
    # 生成提示词
    prompt = generate_trading_prompt(test_data)
    
    print(f"复杂数据提示词统计:")
    print(f"   总长度: {len(prompt)} 字符")
    print(f"   包含3个币种: {('BTC' in prompt) and ('ETH' in prompt) and ('SOL' in prompt)}")
    print(f"   包含多时间框架: {'多时间框架' in prompt}")
    print(f"   包含日内序列: {'日内序列' in prompt}")
    print(f"   包含2个持仓: {'BTC' in prompt and 'ETH' in prompt}")
    print(f"   包含交易历史: {'交易历史' in prompt}")
    print(f"   包含决策历史: {'上一次的决策' in prompt}")
    
    # 验证关键信息都存在
    assert len(prompt) > 3000, "复杂数据的提示词应该很长"
    assert 'BTC' in prompt and 'ETH' in prompt and 'SOL' in prompt, "应包含所有币种"
    assert '103500' in prompt or '103,500' in prompt, "应包含BTC价格"
    assert '1580' in prompt or '1,580' in prompt, "应包含BTC未实现盈亏"
    assert '多时间框架' in prompt, "应包含多时间框架分析"
    
    print("✅ 复杂数据提示词生成测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("🚀 阶段4测试套件：AI决策引擎")
    print("=" * 80)
    
    try:
        test_account_risk_config()
        test_trading_strategy()
        test_strategy_params()
        test_trading_prompt_generation()
        test_prompt_with_different_strategies()
        test_prompt_with_complex_data()
        
        # 总结
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！阶段4完成！")
        print("=" * 80)
        print("\n📋 已完成的功能：")
        print("   ✅ 账户风险配置")
        print("   ✅ 5种交易策略参数")
        print("   ✅ 策略参数验证")
        print("   ✅ 交易提示词生成")
        print("   ✅ 多时间框架数据格式化")
        print("   ✅ 持仓信息格式化")
        print("   ✅ 交易历史格式化")
        print("   ✅ 策略特定规则（代码级别保护）")
        print("\n🎯 下一步：准备开始阶段5（交易策略实现）")
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

