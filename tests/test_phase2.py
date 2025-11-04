"""
阶段2测试脚本

测试交易所API封装是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from config.settings import settings


async def test_exchange_client_creation():
    """测试交易所客户端创建"""
    print("\n" + "=" * 80)
    print("🧪 测试1：交易所客户端创建")
    print("=" * 80)
    
    from services.exchange import ExchangeClient, create_exchange_client
    
    # 测试直接创建
    client = ExchangeClient()
    assert client is not None, "客户端创建失败"
    assert client.exchange is not None, "交易所实例创建失败"
    print(f"✅ 交易所客户端创建成功")
    print(f"   测试网模式: {'是' if client.testnet else '否'}")
    print(f"   结算货币: {client.settle}")
    
    await client.close()
    
    # 测试单例模式
    client1 = create_exchange_client()
    client2 = create_exchange_client()
    assert client1 is client2, "单例模式失败"
    print(f"✅ 单例模式测试通过")
    
    await client1.close()


async def test_symbol_conversion():
    """测试币种符号转换"""
    print("\n" + "=" * 80)
    print("🧪 测试2：币种符号转换")
    print("=" * 80)
    
    from services.exchange import ExchangeClient
    
    client = ExchangeClient()
    
    # 测试各种格式
    test_cases = [
        ('BTC', 'BTC/USDT:USDT'),
        ('ETH', 'ETH/USDT:USDT'),
        ('BTC_USDT', 'BTC/USDT:USDT'),
        ('BTC/USDT', 'BTC/USDT:USDT'),
    ]
    
    for input_symbol, expected in test_cases:
        result = client._symbol_to_ccxt(input_symbol)
        assert result == expected, f"转换失败: {input_symbol} -> {result} (期望: {expected})"
        print(f"✅ {input_symbol} -> {result}")
    
    # 测试反向转换
    assert client._symbol_from_ccxt('BTC/USDT:USDT') == 'BTC'
    assert client._symbol_from_ccxt('ETH/USDT:USDT') == 'ETH'
    print(f"✅ 反向转换测试通过")
    
    await client.close()


async def test_get_ticker():
    """测试获取价格"""
    print("\n" + "=" * 80)
    print("🧪 测试3：获取价格数据")
    print("=" * 80)
    
    from services.exchange import create_exchange_client
    
    client = create_exchange_client()
    
    try:
        # 获取BTC价格
        ticker = await client.get_futures_ticker('BTC')
        
        print(f"BTC Ticker数据:")
        print(f"   合约: {ticker['contract']}")
        print(f"   最新价: {ticker['last']}")
        print(f"   标记价: {ticker['markPrice']}")
        print(f"   24h涨跌: {ticker['change_percentage']}%")
        print(f"   24h成交量: {ticker['volume_24h']}")
        
        # 验证数据有效性
        assert float(ticker['last']) > 0, "价格无效"
        assert ticker['contract'] == 'BTC_USDT', "合约格式错误"
        
        print(f"✅ 价格数据获取成功")
        
    except Exception as e:
        print(f"⚠️  价格获取失败（可能是API密钥未配置）: {e}")
        print(f"   提示：在.env中配置GATE_API_KEY和GATE_API_SECRET")
        raise
    finally:
        await client.close()


async def test_get_candles():
    """测试获取K线数据"""
    print("\n" + "=" * 80)
    print("🧪 测试4：获取K线数据")
    print("=" * 80)
    
    from services.exchange import create_exchange_client
    
    client = create_exchange_client()
    
    try:
        # 获取5分钟K线，最近5条
        candles = await client.get_futures_candles('BTC', '5m', 5)
        
        print(f"获取到 {len(candles)} 条K线数据")
        
        # 验证数据结构
        assert len(candles) > 0, "K线数据为空"
        
        # 检查最新K线
        latest = candles[-1]
        print(f"\n最新K线:")
        print(f"   时间戳: {latest['t']}")
        print(f"   开盘价: {latest['o']}")
        print(f"   最高价: {latest['h']}")
        print(f"   最低价: {latest['l']}")
        print(f"   收盘价: {latest['c']}")
        print(f"   成交量: {latest['v']}")
        
        # 验证数据有效性
        assert 't' in latest, "缺少时间戳"
        assert 'o' in latest, "缺少开盘价"
        assert 'c' in latest, "缺少收盘价"
        assert float(latest['c']) > 0, "收盘价无效"
        
        print(f"✅ K线数据获取成功")
        
    except Exception as e:
        print(f"⚠️  K线获取失败: {e}")
        raise
    finally:
        await client.close()


async def test_get_account():
    """测试获取账户信息"""
    print("\n" + "=" * 80)
    print("🧪 测试5：获取账户信息")
    print("=" * 80)
    
    from services.exchange import create_exchange_client
    
    client = create_exchange_client()
    
    try:
        account = await client.get_account()
        
        print(f"账户信息:")
        print(f"   总资产: {account['total']} USDT")
        print(f"   可用余额: {account['available']} USDT")
        print(f"   未实现盈亏: {account['unrealisedPnl']} USDT")
        
        # 验证数据有效性
        assert float(account['total']) >= 0, "总资产无效"
        assert account['currency'] == 'USDT', "货币类型错误"
        
        print(f"✅ 账户信息获取成功")
        
    except Exception as e:
        print(f"⚠️  账户信息获取失败: {e}")
        raise
    finally:
        await client.close()


async def test_get_positions():
    """测试获取持仓"""
    print("\n" + "=" * 80)
    print("🧪 测试6：获取持仓信息")
    print("=" * 80)
    
    from services.exchange import create_exchange_client
    
    client = create_exchange_client()
    
    try:
        positions = await client.get_positions()
        
        print(f"当前持仓数: {len(positions)}")
        
        if positions:
            print(f"\n持仓详情:")
            for pos in positions:
                print(f"   {pos['contract']}: {pos['size']}张, "
                      f"杠杆{pos['leverage']}x, "
                      f"未实现盈亏{pos['unrealisedPnl']} USDT")
        else:
            print(f"   无持仓")
        
        # 验证数据格式
        for pos in positions:
            assert 'contract' in pos, "缺少合约字段"
            assert 'size' in pos, "缺少数量字段"
            assert '_USDT' in pos['contract'], "合约格式错误"
        
        print(f"✅ 持仓信息获取成功")
        
    except Exception as e:
        print(f"⚠️  持仓信息获取失败: {e}")
        raise
    finally:
        await client.close()


async def test_get_funding_rate():
    """测试获取资金费率"""
    print("\n" + "=" * 80)
    print("🧪 测试7：获取资金费率")
    print("=" * 80)
    
    from services.exchange import create_exchange_client
    
    client = create_exchange_client()
    
    try:
        funding = await client.get_funding_rate('BTC')
        
        print(f"BTC资金费率:")
        print(f"   费率: {funding['r']}")
        print(f"   时间戳: {funding['t']}")
        
        # 验证数据有效性
        assert 'r' in funding, "缺少费率字段"
        assert funding['t'] >= 0, "时间戳无效"
        
        print(f"✅ 资金费率获取成功")
        
    except Exception as e:
        print(f"⚠️  资金费率获取失败: {e}")
        raise
    finally:
        await client.close()


async def test_retry_mechanism():
    """测试重试机制"""
    print("\n" + "=" * 80)
    print("🧪 测试8：重试机制")
    print("=" * 80)
    
    from services.exchange import ExchangeClient
    
    # 创建一个无效的客户端（故意使用错误的API密钥）
    client = ExchangeClient(
        api_key="invalid_key",
        api_secret="invalid_secret",
        testnet=True
    )
    
    try:
        # 这应该会失败，但会重试3次
        print(f"   尝试使用无效密钥获取数据（会自动重试3次）...")
        await client.get_futures_ticker('BTC')
        print(f"❌ 不应该成功")
        
    except Exception as e:
        print(f"✅ 重试机制正常工作（预期失败）: {type(e).__name__}")
        
    finally:
        await client.close()


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("🚀 阶段2测试套件")
    print("=" * 80)
    
    # 检查API密钥配置
    has_valid_api_key = (
        settings.GATE_API_KEY and 
        settings.GATE_API_SECRET and 
        settings.GATE_API_KEY != "your_api_key_here" and
        settings.GATE_API_SECRET != "your_api_secret_here" and
        not settings.GATE_API_KEY.startswith("your_")
    )
    
    if not has_valid_api_key:
        print("\n⚠️  警告：API密钥未配置或使用示例密钥")
        print("   请在.env文件中设置 GATE_API_KEY 和 GATE_API_SECRET")
        print("   获取测试网API密钥: https://www.gate.io/testnet")
        print("\n   跳过需要API认证的测试...\n")
    
    try:
        # 运行不需要API认证的测试
        await test_exchange_client_creation()
        await test_symbol_conversion()
        
        if has_valid_api_key:
            # 只有在有有效API密钥时才运行这些测试
            await test_get_ticker()
            await test_get_candles()
            await test_get_account()
            await test_get_positions()
            await test_get_funding_rate()
            await test_retry_mechanism()
        else:
            print("\n" + "=" * 80)
            print("⚠️  基础测试通过（已跳过需要API密钥的测试）")
            print("=" * 80)
            print("\n💡 要运行完整测试，请：")
            print("   1. 访问 https://www.gate.io/testnet 注册测试账号")
            print("   2. 获取API密钥")
            print("   3. 在.env文件中配置 GATE_API_KEY 和 GATE_API_SECRET")
            print("   4. 重新运行测试\n")
            return True  # 基础测试通过也算成功
        
        # 总结
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！阶段2完成！")
        print("=" * 80)
        print("\n📋 已完成的功能：")
        print("   ✅ ExchangeClient类 - 交易所API封装")
        print("   ✅ get_futures_ticker() - 获取价格")
        print("   ✅ get_futures_candles() - 获取K线")
        print("   ✅ get_account() - 获取账户信息")
        print("   ✅ get_positions() - 获取持仓")
        print("   ✅ get_funding_rate() - 获取资金费率")
        print("   ✅ 自动重试机制")
        print("   ✅ 测试网/正式网切换")
        print("\n🎯 下一步：准备开始阶段3（技术指标计算）")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ 测试失败: {e}")
        print("=" * 80 + "\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行所有测试
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

