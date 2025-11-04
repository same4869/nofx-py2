"""
阶段1测试脚本

测试项目基础模块是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio


def test_config():
    """测试配置加载"""
    print("\n" + "=" * 80)
    print("🧪 测试1：配置加载")
    print("=" * 80)
    
    from config.settings import settings, print_config_summary
    
    # 打印配置摘要
    print_config_summary()
    
    # 验证关键配置
    assert settings.PORT > 0, "端口配置无效"
    assert settings.MAX_LEVERAGE > 0, "杠杆配置无效"
    assert len(settings.trading_symbols_list) > 0, "交易币种配置无效"
    
    print(f"✅ 配置模块测试通过")
    print(f"   - 交易币种数量: {len(settings.trading_symbols_list)}")
    print(f"   - 数据库路径: {settings.get_database_path()}")


def test_risk_params():
    """测试风险参数"""
    print("\n" + "=" * 80)
    print("🧪 测试2：风险参数")
    print("=" * 80)
    
    from config.risk_params import RISK_PARAMS, print_risk_params_summary
    
    # 打印风险参数摘要
    print_risk_params_summary()
    
    # 验证风险参数
    assert RISK_PARAMS.MAX_POSITIONS > 0, "最大持仓数配置无效"
    assert RISK_PARAMS.MAX_LEVERAGE > 0, "最大杠杆配置无效"
    assert RISK_PARAMS.MAX_HOLDING_CYCLES > 0, "最大持仓周期配置无效"
    
    print(f"✅ 风险参数测试通过")
    print(f"   - 最大持仓周期: {RISK_PARAMS.MAX_HOLDING_CYCLES}")


def test_logger():
    """测试日志系统"""
    print("\n" + "=" * 80)
    print("🧪 测试3：日志系统")
    print("=" * 80)
    
    from core.logger import (
        logger, 
        log_info, 
        log_warning, 
        log_error,
        log_section_start,
        log_section_end,
        format_china_time
    )
    
    # 测试不同级别的日志
    log_info("这是一条信息日志 ✅")
    log_warning("这是一条警告日志 ⚠️")
    log_error("这是一条错误日志 ❌")
    
    # 测试分隔线
    log_section_start("测试章节")
    logger.info("章节内容")
    log_section_end()
    
    # 测试中国时区
    china_time = format_china_time()
    logger.info(f"当前中国时间: {china_time}")
    
    print(f"\n✅ 日志系统测试通过")


def test_time_utils():
    """测试时间工具"""
    print("\n" + "=" * 80)
    print("🧪 测试4：时间工具")
    print("=" * 80)
    
    from utils.time_utils import (
        get_china_time,
        get_china_time_iso,
        format_china_time,
        get_time_diff_hours,
        utc_to_china,
        timestamp_to_china_time
    )
    from datetime import datetime, timedelta
    import pytz
    
    # 测试获取中国时间
    china_now = get_china_time()
    print(f"当前中国时间: {china_now}")
    print(f"ISO格式: {get_china_time_iso()}")
    print(f"格式化: {format_china_time()}")
    
    # 测试时区转换
    utc_now = datetime.now(pytz.utc)
    china_converted = utc_to_china(utc_now)
    print(f"\nUTC时间: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"中国时间: {china_converted.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试时间差计算
    past_time = china_now - timedelta(hours=2, minutes=30)
    diff_hours = get_time_diff_hours(past_time)
    print(f"\n时间差测试: {diff_hours:.2f} 小时")
    
    assert abs(diff_hours - 2.5) < 0.01, "时间差计算错误"
    
    print(f"\n✅ 时间工具测试通过")


async def test_database():
    """测试数据库连接"""
    print("\n" + "=" * 80)
    print("🧪 测试5：数据库连接")
    print("=" * 80)
    
    from core.database import (
        init_database,
        get_session,
        close_database
    )
    from core.logger import logger
    
    # 初始化数据库
    await init_database()
    logger.info("✅ 数据库表创建成功")
    
    # 测试会话创建
    try:
        async with get_session() as session:
            logger.info("✅ 数据库会话创建成功")
            
            # 简单查询测试
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1, "数据库查询失败"
            logger.info("✅ 数据库查询测试通过")
    except Exception as e:
        logger.error(f"数据库会话测试失败: {e}")
        raise
    
    # 关闭数据库连接
    await close_database()
    
    print(f"\n✅ 数据库连接测试通过")


def test_models():
    """测试数据模型"""
    print("\n" + "=" * 80)
    print("🧪 测试6：数据模型")
    print("=" * 80)
    
    from core.models import (
        Trade, Position, AccountHistory,
        TradingSignal, AgentDecision, SystemConfig
    )
    
    # 验证所有模型都有正确的表名
    models = {
        'trades': Trade,
        'positions': Position,
        'account_history': AccountHistory,
        'trading_signals': TradingSignal,
        'agent_decisions': AgentDecision,
        'system_config': SystemConfig,
    }
    
    for table_name, model in models.items():
        assert model.__tablename__ == table_name, f"表名不匹配: {model.__tablename__}"
        print(f"✅ {model.__name__} -> {table_name}")
    
    print(f"\n✅ 数据模型测试通过（共{len(models)}个表）")


def test_integration():
    """集成测试：验证模块间协作"""
    print("\n" + "=" * 80)
    print("🧪 测试7：模块集成")
    print("=" * 80)
    
    from config.settings import settings
    from config.risk_params import RISK_PARAMS
    from utils.time_utils import get_china_time_iso
    from core.logger import logger
    
    # 验证配置和风险参数一致性
    assert settings.MAX_POSITIONS == RISK_PARAMS.MAX_POSITIONS
    assert settings.MAX_LEVERAGE == RISK_PARAMS.MAX_LEVERAGE
    
    logger.info(f"当前时间: {get_china_time_iso()}")
    logger.info(f"配置验证通过: MAX_POSITIONS={RISK_PARAMS.MAX_POSITIONS}")
    
    print(f"\n✅ 模块集成测试通过")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("🚀 阶段1测试套件")
    print("=" * 80)
    
    try:
        # 同步测试
        test_config()
        test_risk_params()
        test_logger()
        test_time_utils()
        test_models()
        test_integration()
        
        # 异步测试
        await test_database()
        
        # 总结
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！阶段1完成！")
        print("=" * 80)
        print("\n📋 已完成的模块：")
        print("   ✅ config/settings.py - 配置管理")
        print("   ✅ config/risk_params.py - 风险参数")
        print("   ✅ core/logger.py - 日志系统")
        print("   ✅ core/database.py - 数据库连接")
        print("   ✅ core/models.py - 数据模型")
        print("   ✅ utils/time_utils.py - 时间工具")
        print("\n🎯 下一步：准备开始阶段2（交易所API封装）")
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

