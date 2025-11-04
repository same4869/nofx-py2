#!/usr/bin/env python
"""
Open NOF1.ai - Python版主程序

AI驱动的加密货币自动交易系统

启动所有服务：
- 数据库初始化
- 自动交易系统
- 账户记录器
- Web API（可选）

Usage:
    python main.py

对应TypeScript: src/index.ts
"""

import asyncio
import signal
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.logger import logger
from core.database import init_database
from services.exchange import create_exchange_client
from scheduler import create_auto_trading_system, create_account_recorder
from agents.trading_agent import get_trading_strategy, get_strategy_params
from config.settings import settings
from config.risk_params import RISK_PARAMS

# Web API（可选）
try:
    import uvicorn
    from api import create_api_app
    WEB_API_AVAILABLE = True
except ImportError:
    WEB_API_AVAILABLE = False
    logger.warning("FastAPI/uvicorn未安装，Web API将不可用")


class TradingApplication:
    """交易应用主类"""
    
    def __init__(self):
        self.exchange_client = None
        self.trading_system = None
        self.account_recorder = None
        self.web_server = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """初始化系统"""
        logger.info("🚀 启动 AI 加密货币自动交易系统")
        logger.info("="*80)
        
        # 1. 初始化数据库
        logger.info("📦 初始化数据库...")
        await init_database()
        logger.info("✅ 数据库初始化完成")
        
        # 2. 创建交易所客户端
        logger.info("🔗 连接交易所...")
        self.exchange_client = create_exchange_client()
        logger.info("✅ 交易所连接成功")
        
        # 3. 创建交易系统
        logger.info("⚙️  创建自动交易系统...")
        self.trading_system = create_auto_trading_system(self.exchange_client)
        
        # 4. 创建账户记录器
        logger.info("📊 创建账户记录器...")
        self.account_recorder = create_account_recorder(self.exchange_client)
    
    async def start(self):
        """启动所有服务"""
        logger.info("\n" + "="*80)
        logger.info("启动服务...")
        logger.info("="*80 + "\n")
        
        # 1. 启动自动交易系统
        await self.trading_system.start()
        
        # 2. 启动账户记录器
        await self.account_recorder.start()
        
        # 3. 启动Web API服务器（可选）
        if WEB_API_AVAILABLE and settings.ENABLE_WEB_API:
            await self._start_web_server()
        
        # 4. 显示系统信息
        self._print_system_info()
        
        logger.info("\n✅ 所有服务已启动！")
        logger.info("按 Ctrl+C 停止系统\n")
    
    async def _start_web_server(self):
        """启动Web服务器"""
        try:
            port = int(settings.PORT or 3000)
            
            # 创建FastAPI应用
            app = create_api_app(self.exchange_client)
            
            # 创建uvicorn配置
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=port,
                log_level="info",
                access_log=False,  # 禁用访问日志，避免干扰
            )
            
            # 在后台启动服务器
            self.web_server = uvicorn.Server(config)
            
            # 使用asyncio.create_task在后台运行
            asyncio.create_task(self.web_server.serve())
            
            logger.info(f"🌐 Web监控界面: http://localhost:{port}")
            logger.info(f"📡 API文档: http://localhost:{port}/docs")
            
        except Exception as e:
            logger.error(f"启动Web服务器失败: {e}")
    
    def _print_system_info(self):
        """打印系统配置信息"""
        strategy = get_trading_strategy()
        params = get_strategy_params(strategy)
        is_code_level_enabled = strategy == "swing-trend"
        
        logger.info("\n" + "="*80)
        logger.info("系统配置信息")
        logger.info("="*80)
        logger.info(f"\n📈 交易策略: {params.name}")
        logger.info(f"   {params.description}")
        
        if is_code_level_enabled:
            logger.info(f"\n🛡️  代码级保护: 启用 (波段策略)")
            logger.info("   - 自动止损监控（每10秒）")
            logger.info("   - 移动止盈监控（每10秒）")
        else:
            logger.info(f"\n⚠️   代码级保护: 未启用")
            logger.info("   止损止盈完全由AI控制")
        
        logger.info(f"\n⚙️  系统参数:")
        logger.info(f"   - 交易间隔: {settings.TRADING_INTERVAL_MINUTES} 分钟")
        logger.info(f"   - 账户记录间隔: {settings.ACCOUNT_RECORD_INTERVAL_MINUTES} 分钟")
        logger.info(f"   - 支持币种: {', '.join(RISK_PARAMS.TRADING_SYMBOLS)}")
        logger.info(f"   - 最大杠杆: {RISK_PARAMS.MAX_LEVERAGE}x")
        logger.info(f"   - 最大持仓数: {RISK_PARAMS.MAX_POSITIONS}")
        
        if settings.ACCOUNT_STOP_LOSS_USDT:
            logger.info(f"\n🔴 账户止损线: {settings.ACCOUNT_STOP_LOSS_USDT} USDT")
        if settings.ACCOUNT_TAKE_PROFIT_USDT:
            logger.info(f"🟢 账户止盈线: {settings.ACCOUNT_TAKE_PROFIT_USDT} USDT")
        
        logger.info(f"\n🌐 交易所: {'Gate.io 测试网' if settings.GATE_USE_TESTNET else 'Gate.io 正式网'}")
        
        if WEB_API_AVAILABLE and settings.ENABLE_WEB_API:
            port = int(settings.PORT or 3000)
            logger.info(f"\n🖥️  Web监控: http://localhost:{port}")
            logger.info(f"📡 API文档: http://localhost:{port}/docs")
        
        logger.info("="*80)
    
    async def stop(self):
        """停止所有服务"""
        logger.info("\n\n正在关闭系统...")
        
        try:
            # 1. 停止自动交易系统
            if self.trading_system:
                logger.info("⏸️  停止自动交易系统...")
                await self.trading_system.stop()
                logger.info("✅ 自动交易系统已停止")
            
            # 2. 停止账户记录器
            if self.account_recorder:
                logger.info("⏸️  停止账户记录器...")
                await self.account_recorder.stop()
                logger.info("✅ 账户记录器已停止")
            
            # 3. 停止Web服务器
            if self.web_server:
                logger.info("⏸️  停止Web服务器...")
                self.web_server.should_exit = True
                logger.info("✅ Web服务器已停止")
            
            # 4. 关闭交易所客户端
            if self.exchange_client:
                logger.info("🔌 关闭交易所连接...")
                await self.exchange_client.close()
                logger.info("✅ 交易所连接已关闭")
            
            logger.info("\n✅ 系统已安全关闭")
        except Exception as e:
            logger.error(f"关闭系统时出错: {e}")
    
    async def run(self):
        """运行应用"""
        try:
            # 初始化
            await self.initialize()
            
            # 启动服务
            await self.start()
            
            # 等待关闭信号
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"应用运行异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 关闭服务
            await self.stop()
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        signal_name = signal.Signals(signum).name
        logger.info(f"\n收到信号: {signal_name}")
        self._shutdown_event.set()


async def main():
    """主函数"""
    app = TradingApplication()
    
    # 注册信号处理
    signal.signal(signal.SIGINT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)
    
    # 运行应用
    await app.run()


if __name__ == "__main__":
    # 运行主程序
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n程序已被用户中断")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)

