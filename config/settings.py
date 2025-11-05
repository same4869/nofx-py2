"""
配置管理模块

从环境变量中读取所有配置，使用pydantic-settings进行验证
确保与TypeScript版本的配置名称完全一致
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """系统配置（从.env文件读取）"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'  # 忽略额外的环境变量
    )
    
    # ==================== 服务器配置 ====================
    PORT: int = Field(default=3100, description="HTTP服务器端口")
    ENABLE_WEB_API: bool = Field(default=True, description="是否启用Web API")
    
    # ==================== 交易参数 ====================
    TRADING_INTERVAL_MINUTES: int = Field(default=5, description="交易循环间隔（分钟）")
    MAX_LEVERAGE: int = Field(default=10, description="最大杠杆倍数")
    MAX_POSITIONS: int = Field(default=5, description="最大持仓数量")
    MAX_HOLDING_HOURS: int = Field(default=36, description="最大持有时长（小时）")
    INITIAL_BALANCE: float = Field(default=2000.0, description="初始资金（USDT）")
    
    # 交易策略选择
    TRADING_STRATEGY: str = Field(
        default="balanced",
        description="交易策略：conservative/balanced/aggressive/ultra-short/swing-trend"
    )
    
    # 交易币种（逗号分隔）
    TRADING_SYMBOLS: str = Field(
        default="BTC,ETH,SOL,XRP,BNB,BCH",
        description="交易币种列表"
    )
    
    @property
    def trading_symbols_list(self) -> List[str]:
        """获取交易币种列表"""
        return [s.strip() for s in self.TRADING_SYMBOLS.split(',') if s.strip()]
    
    # ==================== 数据库配置 ====================
    DATABASE_URL: str = Field(
        default="file:./.voltagent/trading.db",
        description="SQLite数据库文件路径"
    )
    
    # ==================== Gate.io API 凭证 ====================
    GATE_API_KEY: str = Field(default="", description="Gate.io API密钥")
    GATE_API_SECRET: str = Field(default="", description="Gate.io API密钥")
    GATE_USE_TESTNET: bool = Field(default=True, description="使用测试网")
    
    # ==================== AI 模型配置 ====================
    OPENAI_API_KEY: str = Field(default="", description="OpenAI兼容API密钥")
    OPENAI_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="API基础地址（支持OpenAI、DeepSeek等）"
    )
    OPENAI_MODEL: str = Field(
        default="deepseek-chat",
        description="AI模型名称"
    )
    
    # ==================== 账户风控配置 ====================
    # 账户止损线和止盈线
    ACCOUNT_STOP_LOSS_USDT: float = Field(
        default=50.0,
        description="账户止损线（USDT）"
    )
    ACCOUNT_TAKE_PROFIT_USDT: float = Field(
        default=10000.0,
        description="账户止盈线（USDT）"
    )
    
    # 账户回撤保护
    ACCOUNT_DRAWDOWN_WARNING_PERCENT: int = Field(
        default=20,
        description="警告阈值（%）"
    )
    ACCOUNT_DRAWDOWN_NO_NEW_POSITION_PERCENT: int = Field(
        default=30,
        description="禁止开仓阈值（%）"
    )
    ACCOUNT_DRAWDOWN_FORCE_CLOSE_PERCENT: int = Field(
        default=50,
        description="强制平仓阈值（%）"
    )
    
    # 极端止损（防止爆仓）
    EXTREME_STOP_LOSS_PERCENT: int = Field(
        default=-30,
        description="极端止损线（%）"
    )
    
    # ==================== 监控和日志配置 ====================
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE_PATH: str = Field(default="./logs/trading.log", description="日志文件路径")
    LOG_TO_FILE: bool = Field(default=True, description="是否启用文件日志")
    
    # 账户记录间隔
    ACCOUNT_RECORD_INTERVAL_MINUTES: int = Field(
        default=10,
        description="账户记录间隔（分钟）"
    )
    
    # 监控器检查间隔
    MONITOR_CHECK_INTERVAL_SECONDS: int = Field(
        default=10,
        description="监控器检查间隔（秒）"
    )
    
    # 配置同步
    SYNC_CONFIG_ON_STARTUP: bool = Field(
        default=True,
        description="启动时同步配置到数据库"
    )
    
    # ==================== 开发/调试配置 ====================
    DEV_MODE: bool = Field(default=False, description="开发模式")
    DRY_RUN: bool = Field(default=False, description="测试模式（不真实下单）")
    API_TIMEOUT: int = Field(default=30, description="API请求超时（秒）")
    DB_POOL_SIZE: int = Field(default=5, description="数据库连接池大小")
    
    def validate_api_keys(self) -> bool:
        """验证必要的API密钥是否已设置"""
        if not self.GATE_API_KEY or not self.GATE_API_SECRET:
            return False
        if not self.OPENAI_API_KEY:
            return False
        return True
    
    def get_database_path(self) -> str:
        """获取数据库文件路径（去除file:前缀）"""
        if self.DATABASE_URL.startswith('file:'):
            return self.DATABASE_URL[5:]
        return self.DATABASE_URL


# 创建全局配置实例
settings = Settings()


# 打印配置摘要（用于启动时验证）
def print_config_summary():
    """打印配置摘要"""
    print("\n" + "=" * 80)
    print("📋 系统配置")
    print("=" * 80)
    print(f"服务器端口: {settings.PORT}")
    print(f"交易策略: {settings.TRADING_STRATEGY}")
    print(f"交易间隔: {settings.TRADING_INTERVAL_MINUTES} 分钟")
    print(f"最大杠杆: {settings.MAX_LEVERAGE}x")
    print(f"最大持仓: {settings.MAX_POSITIONS}")
    print(f"交易币种: {', '.join(settings.trading_symbols_list)}")
    print(f"使用测试网: {'是' if settings.GATE_USE_TESTNET else '否'}")
    print(f"AI模型: {settings.OPENAI_MODEL}")
    print(f"日志级别: {settings.LOG_LEVEL}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # 测试配置加载
    print_config_summary()
    
    # 验证API密钥
    if settings.validate_api_keys():
        print("✅ API密钥配置完整")
    else:
        print("⚠️  警告：API密钥未配置或不完整")

