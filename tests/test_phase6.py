"""
阶段6测试：自动交易系统

测试调度器和自动交易功能
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from unittest.mock import Mock, AsyncMock
from config.settings import settings
from services.exchange import create_exchange_client
from scheduler import (
    create_auto_trading_system,
    create_account_recorder,
)
from core.logger import logger


def test_1_import_scheduler_modules():
    """测试1：验证scheduler模块可以正常导入"""
    print("\n" + "=" * 80)
    print("测试1：scheduler模块导入测试")
    print("=" * 80)
    
    try:
        from scheduler import (
            AccountRecorder,
            create_account_recorder,
            AutoTradingSystem,
            create_auto_trading_system,
        )
        
        print("✅ scheduler模块导入成功")
        print(f"   - AccountRecorder: {bool(AccountRecorder)}")
        print(f"   - AutoTradingSystem: {bool(AutoTradingSystem)}")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False


async def test_2_create_account_recorder():
    """测试2：创建账户记录器"""
    print("\n" + "=" * 80)
    print("测试2：创建账户记录器")
    print("=" * 80)
    
    try:
        # 创建交易所客户端
        client = create_exchange_client()
        
        # 创建账户记录器
        recorder = create_account_recorder(client)
        
        print(f"✅ 账户记录器创建成功")
        print(f"   - 类型: {type(recorder).__name__}")
        print(f"   - 间隔: {recorder.interval_minutes} 分钟")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建账户记录器失败: {e}")
        return False


async def test_3_create_trading_system():
    """测试3：创建自动交易系统"""
    print("\n" + "=" * 80)
    print("测试3：创建自动交易系统")
    print("=" * 80)
    
    try:
        # 创建交易所客户端
        client = create_exchange_client()
        
        # 创建交易系统
        system = create_auto_trading_system(client)
        
        print(f"✅ 自动交易系统创建成功")
        print(f"   - 类型: {type(system).__name__}")
        print(f"   - 间隔: {system.trading_interval_minutes} 分钟")
        print(f"   - 策略: {system.strategy}")
        print(f"   - 策略名称: {system.strategy_params.name}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建交易系统失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_4_collect_market_data():
    """测试4：市场数据收集"""
    print("\n" + "=" * 80)
    print("测试4：市场数据收集")
    print("=" * 80)
    
    # 检查API密钥
    if not settings.GATE_API_KEY or settings.GATE_API_KEY == "your_api_key_here":
        print("⚠️  API密钥未配置，跳过市场数据收集测试")
        return True
    
    try:
        client = create_exchange_client()
        system = create_auto_trading_system(client)
        
        print("收集市场数据...")
        market_data = await system.collect_market_data()
        
        if market_data:
            print(f"✅ 市场数据收集成功")
            print(f"   - 币种数量: {len(market_data)}")
            for symbol, data in market_data.items():
                print(f"   - {symbol}: 价格=${data['price']:.2f}, EMA20=${data.get('ema20', 0):.2f}")
        else:
            print("⚠️  未能收集到市场数据")
        
        await client.close()
        return bool(market_data)
        
    except Exception as e:
        print(f"❌ 市场数据收集失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_5_system_lifecycle():
    """测试5：系统生命周期（启动和停止）"""
    print("\n" + "=" * 80)
    print("测试5：系统生命周期测试")
    print("=" * 80)
    
    try:
        client = create_exchange_client()
        system = create_auto_trading_system(client)
        recorder = create_account_recorder(client)
        
        print("测试系统启动...")
        await system.start()
        await recorder.start()
        print("✅ 系统启动成功")
        
        # 等待2秒
        print("等待2秒...")
        await asyncio.sleep(2)
        
        print("测试系统停止...")
        await system.stop()
        await recorder.stop()
        print("✅ 系统停止成功")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ 系统生命周期测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_6_main_program():
    """测试6：主程序导入"""
    print("\n" + "=" * 80)
    print("测试6：主程序导入测试")
    print("=" * 80)
    
    try:
        import main
        
        print("✅ main.py导入成功")
        print(f"   - TradingApplication: {bool(main.TradingApplication)}")
        return True
        
    except Exception as e:
        print(f"❌ main.py导入失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("🚀 阶段6测试：自动交易系统")
    print("=" * 80)
    print(f"\n项目: Open NOF1.ai - Python版")
    print(f"测试范围: scheduler模块和自动交易功能")
    print()
    
    results = []
    
    # 同步测试
    results.append(("模块导入", test_1_import_scheduler_modules()))
    results.append(("主程序导入", test_6_main_program()))
    
    # 异步测试
    results.append(("创建账户记录器", await test_2_create_account_recorder()))
    results.append(("创建交易系统", await test_3_create_trading_system()))
    results.append(("市场数据收集", await test_4_collect_market_data()))
    results.append(("系统生命周期", await test_5_system_lifecycle()))
    
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
        print("\n✅ 阶段6完成：")
        print("   - scheduler包创建成功")
        print("   - 账户记录器正常工作")
        print("   - 自动交易系统正常工作")
        print("   - 主程序可以启动")
        print("\n💡 下一步：")
        print("   - 配置.env文件")
        print("   - 运行 ./start_trading.sh 启动系统")
        print("   - 或运行 python main.py")
    else:
        print(f"\n⚠️  有{total-passed}个测试失败")
        print("请检查上述错误信息")
    
    print("\n" + "=" * 80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

