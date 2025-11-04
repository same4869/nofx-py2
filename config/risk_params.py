"""
风险参数配置

复用TypeScript版本的风险参数逻辑（src/config/riskParams.ts）
所有参数值与TS版本保持一致
"""

from dataclasses import dataclass
from typing import Tuple
from .settings import settings


@dataclass(frozen=True)
class RiskParams:
    """风险参数配置（不可变）"""
    
    # 最大持仓数
    MAX_POSITIONS: int
    
    # 最大杠杆倍数
    MAX_LEVERAGE: int
    
    # 交易币种列表
    TRADING_SYMBOLS: Tuple[str, ...]
    
    # 最大持仓小时数
    MAX_HOLDING_HOURS: int
    
    # 最大持仓周期数（根据持仓小时数自动计算：小时数 * 6，因为每10分钟一个周期）
    @property
    def MAX_HOLDING_CYCLES(self) -> int:
        """计算最大持仓周期数"""
        return self.MAX_HOLDING_HOURS * 6
    
    # 极端止损线（单笔亏损百分比，防止爆仓的最后防线）
    EXTREME_STOP_LOSS_PERCENT: int
    
    # 账户回撤风控阈值
    # 禁止新开仓的回撤阈值（⚠️ 已禁用 - 相关检查已被注释，不再限制开仓）
    ACCOUNT_DRAWDOWN_NO_NEW_POSITION_PERCENT: int
    
    # 强制平仓的回撤阈值（⚠️ 已禁用 - 相关检查已被注释，不再强制平仓）
    ACCOUNT_DRAWDOWN_FORCE_CLOSE_PERCENT: int
    
    # 警告提醒的回撤阈值（达到此阈值时，提醒谨慎交易）
    ACCOUNT_DRAWDOWN_WARNING_PERCENT: int


def create_risk_params() -> RiskParams:
    """
    从环境变量创建风险参数实例
    
    与TypeScript版本的RISK_PARAMS完全对应
    """
    return RiskParams(
        MAX_POSITIONS=settings.MAX_POSITIONS,
        MAX_LEVERAGE=settings.MAX_LEVERAGE,
        TRADING_SYMBOLS=tuple(settings.trading_symbols_list),
        MAX_HOLDING_HOURS=settings.MAX_HOLDING_HOURS,
        EXTREME_STOP_LOSS_PERCENT=settings.EXTREME_STOP_LOSS_PERCENT,
        ACCOUNT_DRAWDOWN_NO_NEW_POSITION_PERCENT=settings.ACCOUNT_DRAWDOWN_NO_NEW_POSITION_PERCENT,
        ACCOUNT_DRAWDOWN_FORCE_CLOSE_PERCENT=settings.ACCOUNT_DRAWDOWN_FORCE_CLOSE_PERCENT,
        ACCOUNT_DRAWDOWN_WARNING_PERCENT=settings.ACCOUNT_DRAWDOWN_WARNING_PERCENT,
    )


# 创建全局风险参数实例
RISK_PARAMS = create_risk_params()


# 打印风险参数摘要
def print_risk_params_summary():
    """打印风险参数摘要"""
    print("\n" + "=" * 80)
    print("🛡️  风险参数配置")
    print("=" * 80)
    print(f"最大持仓数: {RISK_PARAMS.MAX_POSITIONS}")
    print(f"最大杠杆: {RISK_PARAMS.MAX_LEVERAGE}x")
    print(f"最大持仓时间: {RISK_PARAMS.MAX_HOLDING_HOURS}小时 ({RISK_PARAMS.MAX_HOLDING_CYCLES}周期)")
    print(f"极端止损线: {RISK_PARAMS.EXTREME_STOP_LOSS_PERCENT}%")
    print(f"回撤警告阈值: {RISK_PARAMS.ACCOUNT_DRAWDOWN_WARNING_PERCENT}%")
    print(f"禁止开仓阈值: {RISK_PARAMS.ACCOUNT_DRAWDOWN_NO_NEW_POSITION_PERCENT}%")
    print(f"强制平仓阈值: {RISK_PARAMS.ACCOUNT_DRAWDOWN_FORCE_CLOSE_PERCENT}%")
    print(f"交易币种: {', '.join(RISK_PARAMS.TRADING_SYMBOLS)}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # 测试风险参数加载
    print_risk_params_summary()

