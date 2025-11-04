"""
AI交易代理

基于OpenAI SDK的AI决策引擎
支持多种交易策略和风险管理

参考TypeScript版本：src/agents/tradingAgent.ts
"""

from typing import Literal, Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from config.settings import settings
from config.risk_params import RISK_PARAMS
from utils.time_utils import format_china_time
from core.logger import logger


# 交易策略类型
TradingStrategy = Literal["conservative", "balanced", "aggressive", "ultra-short", "swing-trend"]


@dataclass
class AccountRiskConfig:
    """
    账户风险配置
    
    Attributes:
        stop_loss_usdt: 账户止损金额(USDT)
        take_profit_usdt: 账户止盈金额(USDT)
        sync_on_startup: 启动时同步配置
    """
    stop_loss_usdt: float
    take_profit_usdt: float
    sync_on_startup: bool


@dataclass
class TrailingStopLevel:
    """移动止盈级别配置"""
    trigger: float  # 触发盈利百分比
    stop_at: float  # 移动止损线百分比


@dataclass
class PartialTakeProfitStage:
    """分批止盈阶段配置"""
    trigger: float  # 触发盈利百分比
    close_percent: float  # 平仓百分比


@dataclass
class VolatilityAdjustment:
    """波动率调整系数"""
    leverage_factor: float  # 杠杆调整系数
    position_factor: float  # 仓位调整系数


@dataclass
class CodeLevelStopLoss:
    """代码级别止损配置（仅swing-trend策略）"""
    min_leverage: int
    max_leverage: float
    stop_loss_percent: float
    description: str


@dataclass
class CodeLevelTrailingStopStage:
    """代码级别移动止盈阶段配置（仅swing-trend策略）"""
    name: str
    min_profit: float
    max_profit: float
    drawdown_percent: float
    description: str


@dataclass
class StrategyParams:
    """
    策略参数配置
    
    包含杠杆、仓位、止损止盈等完整的策略参数
    """
    name: str
    description: str
    
    # 杠杆配置
    leverage_min: int
    leverage_max: int
    leverage_recommend_normal: str
    leverage_recommend_good: str
    leverage_recommend_strong: str
    
    # 仓位配置
    position_size_min: int
    position_size_max: int
    position_size_recommend_normal: str
    position_size_recommend_good: str
    position_size_recommend_strong: str
    
    # 止损配置
    stop_loss_low: float
    stop_loss_mid: float
    stop_loss_high: float
    
    # 移动止盈配置
    trailing_stop_level1: TrailingStopLevel
    trailing_stop_level2: TrailingStopLevel
    trailing_stop_level3: TrailingStopLevel
    
    # 分批止盈配置
    partial_take_profit_stage1: PartialTakeProfitStage
    partial_take_profit_stage2: PartialTakeProfitStage
    partial_take_profit_stage3: PartialTakeProfitStage
    
    # 峰值回撤保护
    peak_drawdown_protection: float
    
    # 波动率调整
    volatility_adjustment_high: VolatilityAdjustment
    volatility_adjustment_normal: VolatilityAdjustment
    volatility_adjustment_low: VolatilityAdjustment
    
    # 策略描述
    entry_condition: str
    risk_tolerance: str
    trading_style: str
    
    # 代码级别止损（仅swing-trend）
    code_level_stop_loss_low_risk: Optional[CodeLevelStopLoss] = None
    code_level_stop_loss_medium_risk: Optional[CodeLevelStopLoss] = None
    code_level_stop_loss_high_risk: Optional[CodeLevelStopLoss] = None
    
    # 代码级别移动止盈（仅swing-trend）
    code_level_trailing_stop_stage1: Optional[CodeLevelTrailingStopStage] = None
    code_level_trailing_stop_stage2: Optional[CodeLevelTrailingStopStage] = None
    code_level_trailing_stop_stage3: Optional[CodeLevelTrailingStopStage] = None
    code_level_trailing_stop_stage4: Optional[CodeLevelTrailingStopStage] = None
    code_level_trailing_stop_stage5: Optional[CodeLevelTrailingStopStage] = None


def get_account_risk_config() -> AccountRiskConfig:
    """
    从环境变量读取账户风险配置
    
    Returns:
        账户风险配置对象
        
    对应TypeScript: getAccountRiskConfig()
    """
    return AccountRiskConfig(
        stop_loss_usdt=float(settings.ACCOUNT_STOP_LOSS_USDT),
        take_profit_usdt=float(settings.ACCOUNT_TAKE_PROFIT_USDT),
        sync_on_startup=settings.SYNC_CONFIG_ON_STARTUP,
    )


def get_trading_strategy() -> TradingStrategy:
    """
    从环境变量读取交易策略
    
    Returns:
        交易策略类型
        
    对应TypeScript: getTradingStrategy()
    """
    strategy = settings.TRADING_STRATEGY.lower()
    
    valid_strategies = ["conservative", "balanced", "aggressive", "ultra-short", "swing-trend"]
    
    if strategy in valid_strategies:
        return strategy  # type: ignore
    
    logger.warning(f"未知的交易策略: {strategy}，使用默认策略: balanced")
    return "balanced"


def get_strategy_params(strategy: TradingStrategy) -> StrategyParams:
    """
    获取策略参数（基于MAX_LEVERAGE动态计算）
    
    Args:
        strategy: 交易策略类型
        
    Returns:
        策略参数对象
        
    对应TypeScript: getStrategyParams()
    """
    max_leverage = RISK_PARAMS.MAX_LEVERAGE
    
    # 根据MAX_LEVERAGE动态计算各策略的杠杆范围
    # 保守策略：30%-60% 的最大杠杆
    conservative_lev_min = max(1, int(max_leverage * 0.3))
    conservative_lev_max = max(2, int(max_leverage * 0.6))
    conservative_lev_normal = conservative_lev_min
    conservative_lev_good = int((conservative_lev_min + conservative_lev_max) / 2)
    conservative_lev_strong = conservative_lev_max
    
    # 平衡策略：60%-85% 的最大杠杆
    balanced_lev_min = max(2, int(max_leverage * 0.6))
    balanced_lev_max = max(3, int(max_leverage * 0.85))
    balanced_lev_normal = balanced_lev_min
    balanced_lev_good = int((balanced_lev_min + balanced_lev_max) / 2)
    balanced_lev_strong = balanced_lev_max
    
    # 激进策略：85%-100% 的最大杠杆
    aggressive_lev_min = max(3, int(max_leverage * 0.85))
    aggressive_lev_max = max_leverage
    aggressive_lev_normal = aggressive_lev_min
    aggressive_lev_good = int((aggressive_lev_min + aggressive_lev_max) / 2)
    aggressive_lev_strong = aggressive_lev_max
    
    strategy_configs: Dict[TradingStrategy, StrategyParams] = {
        "ultra-short": StrategyParams(
            name="超短线",
            description="极短周期快进快出，5分钟执行，适合高频交易",
            leverage_min=max(3, int(max_leverage * 0.5)),
            leverage_max=max(5, int(max_leverage * 0.75)),
            leverage_recommend_normal=f"{max(3, int(max_leverage * 0.5))}倍",
            leverage_recommend_good=f"{max(4, int(max_leverage * 0.625))}倍",
            leverage_recommend_strong=f"{max(5, int(max_leverage * 0.75))}倍",
            position_size_min=18,
            position_size_max=25,
            position_size_recommend_normal="18-20%",
            position_size_recommend_good="20-23%",
            position_size_recommend_strong="23-25%",
            stop_loss_low=-2.5,
            stop_loss_mid=-2.0,
            stop_loss_high=-1.5,
            trailing_stop_level1=TrailingStopLevel(trigger=4, stop_at=1.5),
            trailing_stop_level2=TrailingStopLevel(trigger=8, stop_at=4),
            trailing_stop_level3=TrailingStopLevel(trigger=15, stop_at=8),
            partial_take_profit_stage1=PartialTakeProfitStage(trigger=15, close_percent=50),
            partial_take_profit_stage2=PartialTakeProfitStage(trigger=25, close_percent=50),
            partial_take_profit_stage3=PartialTakeProfitStage(trigger=35, close_percent=100),
            peak_drawdown_protection=20,
            volatility_adjustment_high=VolatilityAdjustment(leverage_factor=0.7, position_factor=0.8),
            volatility_adjustment_normal=VolatilityAdjustment(leverage_factor=1.0, position_factor=1.0),
            volatility_adjustment_low=VolatilityAdjustment(leverage_factor=1.1, position_factor=1.0),
            entry_condition="至少2个时间框架信号一致，优先1-5分钟级别",
            risk_tolerance="单笔交易风险控制在18-25%之间，快进快出",
            trading_style="超短线交易，5分钟执行周期，快速捕捉短期波动",
        ),
        
        "swing-trend": StrategyParams(
            name="波段趋势",
            description="中长线波段交易，20分钟执行，捕捉中期趋势，适合稳健成长",
            leverage_min=max(2, int(max_leverage * 0.2)),
            leverage_max=max(5, int(max_leverage * 0.5)),
            leverage_recommend_normal=f"{max(2, int(max_leverage * 0.2))}倍",
            leverage_recommend_good=f"{max(3, int(max_leverage * 0.35))}倍",
            leverage_recommend_strong=f"{max(5, int(max_leverage * 0.5))}倍",
            position_size_min=20,
            position_size_max=35,
            position_size_recommend_normal="20-25%",
            position_size_recommend_good="25-30%",
            position_size_recommend_strong="30-35%",
            stop_loss_low=-9,
            stop_loss_mid=-7.5,
            stop_loss_high=-5.5,
            trailing_stop_level1=TrailingStopLevel(trigger=15, stop_at=8),
            trailing_stop_level2=TrailingStopLevel(trigger=30, stop_at=20),
            trailing_stop_level3=TrailingStopLevel(trigger=50, stop_at=35),
            partial_take_profit_stage1=PartialTakeProfitStage(trigger=50, close_percent=40),
            partial_take_profit_stage2=PartialTakeProfitStage(trigger=80, close_percent=60),
            partial_take_profit_stage3=PartialTakeProfitStage(trigger=120, close_percent=100),
            peak_drawdown_protection=35,
            volatility_adjustment_high=VolatilityAdjustment(leverage_factor=0.5, position_factor=0.6),
            volatility_adjustment_normal=VolatilityAdjustment(leverage_factor=1.0, position_factor=1.0),
            volatility_adjustment_low=VolatilityAdjustment(leverage_factor=1.2, position_factor=1.1),
            entry_condition="必须1分钟、3分钟、5分钟、15分钟这4个时间框架信号全部强烈一致",
            risk_tolerance="单笔交易风险控制在12-20%之间，注重趋势质量而非交易频率",
            trading_style="波段趋势交易，20分钟执行周期，耐心等待高质量趋势信号",
            # 代码级别止损
            code_level_stop_loss_low_risk=CodeLevelStopLoss(
                min_leverage=5,
                max_leverage=7,
                stop_loss_percent=-8,
                description="5-7倍杠杆，亏损 -8% 时止损"
            ),
            code_level_stop_loss_medium_risk=CodeLevelStopLoss(
                min_leverage=8,
                max_leverage=12,
                stop_loss_percent=-6,
                description="8-12倍杠杆，亏损 -6% 时止损"
            ),
            code_level_stop_loss_high_risk=CodeLevelStopLoss(
                min_leverage=13,
                max_leverage=float('inf'),
                stop_loss_percent=-5,
                description="13倍以上杠杆，亏损 -5% 时止损"
            ),
            # 代码级别移动止盈
            code_level_trailing_stop_stage1=CodeLevelTrailingStopStage(
                name="阶段1",
                min_profit=4,
                max_profit=6,
                drawdown_percent=1.5,
                description="峰值4-6%，回退1.5%平仓（保底2.5%）"
            ),
            code_level_trailing_stop_stage2=CodeLevelTrailingStopStage(
                name="阶段2",
                min_profit=6,
                max_profit=10,
                drawdown_percent=2,
                description="峰值6-10%，回退2%平仓（保底4%）"
            ),
            code_level_trailing_stop_stage3=CodeLevelTrailingStopStage(
                name="阶段3",
                min_profit=10,
                max_profit=15,
                drawdown_percent=2.5,
                description="峰值10-15%，回退2.5%平仓（保底7.5%）"
            ),
            code_level_trailing_stop_stage4=CodeLevelTrailingStopStage(
                name="阶段4",
                min_profit=15,
                max_profit=25,
                drawdown_percent=3,
                description="峰值15-25%，回退3%平仓（保底12%）"
            ),
            code_level_trailing_stop_stage5=CodeLevelTrailingStopStage(
                name="阶段5",
                min_profit=25,
                max_profit=float('inf'),
                drawdown_percent=5,
                description="峰值25%+，回退5%平仓（保底20%）"
            ),
        ),
        
        "conservative": StrategyParams(
            name="稳健",
            description="低风险低杠杆，严格入场条件，适合保守投资者",
            leverage_min=conservative_lev_min,
            leverage_max=conservative_lev_max,
            leverage_recommend_normal=f"{conservative_lev_normal}倍",
            leverage_recommend_good=f"{conservative_lev_good}倍",
            leverage_recommend_strong=f"{conservative_lev_strong}倍",
            position_size_min=15,
            position_size_max=22,
            position_size_recommend_normal="15-17%",
            position_size_recommend_good="17-20%",
            position_size_recommend_strong="20-22%",
            stop_loss_low=-3.5,
            stop_loss_mid=-3.0,
            stop_loss_high=-2.5,
            trailing_stop_level1=TrailingStopLevel(trigger=6, stop_at=2),
            trailing_stop_level2=TrailingStopLevel(trigger=12, stop_at=6),
            trailing_stop_level3=TrailingStopLevel(trigger=20, stop_at=12),
            partial_take_profit_stage1=PartialTakeProfitStage(trigger=20, close_percent=50),
            partial_take_profit_stage2=PartialTakeProfitStage(trigger=30, close_percent=50),
            partial_take_profit_stage3=PartialTakeProfitStage(trigger=40, close_percent=100),
            peak_drawdown_protection=25,
            volatility_adjustment_high=VolatilityAdjustment(leverage_factor=0.6, position_factor=0.7),
            volatility_adjustment_normal=VolatilityAdjustment(leverage_factor=1.0, position_factor=1.0),
            volatility_adjustment_low=VolatilityAdjustment(leverage_factor=1.0, position_factor=1.0),
            entry_condition="至少3个关键时间框架信号一致，4个或更多更佳",
            risk_tolerance="单笔交易风险控制在15-22%之间，严格控制回撤",
            trading_style="谨慎交易，宁可错过机会也不冒险，优先保护本金",
        ),
        
        "balanced": StrategyParams(
            name="平衡",
            description="中等风险杠杆，合理入场条件，适合大多数投资者",
            leverage_min=balanced_lev_min,
            leverage_max=balanced_lev_max,
            leverage_recommend_normal=f"{balanced_lev_normal}倍",
            leverage_recommend_good=f"{balanced_lev_good}倍",
            leverage_recommend_strong=f"{balanced_lev_strong}倍",
            position_size_min=20,
            position_size_max=27,
            position_size_recommend_normal="20-23%",
            position_size_recommend_good="23-25%",
            position_size_recommend_strong="25-27%",
            stop_loss_low=-3.0,
            stop_loss_mid=-2.5,
            stop_loss_high=-2.0,
            trailing_stop_level1=TrailingStopLevel(trigger=8, stop_at=3),
            trailing_stop_level2=TrailingStopLevel(trigger=15, stop_at=8),
            trailing_stop_level3=TrailingStopLevel(trigger=25, stop_at=15),
            partial_take_profit_stage1=PartialTakeProfitStage(trigger=30, close_percent=50),
            partial_take_profit_stage2=PartialTakeProfitStage(trigger=40, close_percent=50),
            partial_take_profit_stage3=PartialTakeProfitStage(trigger=50, close_percent=100),
            peak_drawdown_protection=30,
            volatility_adjustment_high=VolatilityAdjustment(leverage_factor=0.7, position_factor=0.8),
            volatility_adjustment_normal=VolatilityAdjustment(leverage_factor=1.0, position_factor=1.0),
            volatility_adjustment_low=VolatilityAdjustment(leverage_factor=1.1, position_factor=1.0),
            entry_condition="至少2个关键时间框架信号一致，3个或更多更佳",
            risk_tolerance="单笔交易风险控制在20-27%之间，平衡风险与收益",
            trading_style="在风险可控前提下积极把握机会，追求稳健增长",
        ),
        
        "aggressive": StrategyParams(
            name="激进",
            description="高风险高杠杆，宽松入场条件，适合激进投资者",
            leverage_min=aggressive_lev_min,
            leverage_max=aggressive_lev_max,
            leverage_recommend_normal=f"{aggressive_lev_normal}倍",
            leverage_recommend_good=f"{aggressive_lev_good}倍",
            leverage_recommend_strong=f"{aggressive_lev_strong}倍",
            position_size_min=25,
            position_size_max=32,
            position_size_recommend_normal="25-28%",
            position_size_recommend_good="28-30%",
            position_size_recommend_strong="30-32%",
            stop_loss_low=-2.5,
            stop_loss_mid=-2.0,
            stop_loss_high=-1.5,
            trailing_stop_level1=TrailingStopLevel(trigger=10, stop_at=4),
            trailing_stop_level2=TrailingStopLevel(trigger=18, stop_at=10),
            trailing_stop_level3=TrailingStopLevel(trigger=30, stop_at=18),
            partial_take_profit_stage1=PartialTakeProfitStage(trigger=40, close_percent=50),
            partial_take_profit_stage2=PartialTakeProfitStage(trigger=50, close_percent=50),
            partial_take_profit_stage3=PartialTakeProfitStage(trigger=60, close_percent=100),
            peak_drawdown_protection=35,
            volatility_adjustment_high=VolatilityAdjustment(leverage_factor=0.8, position_factor=0.85),
            volatility_adjustment_normal=VolatilityAdjustment(leverage_factor=1.0, position_factor=1.0),
            volatility_adjustment_low=VolatilityAdjustment(leverage_factor=1.2, position_factor=1.1),
            entry_condition="至少2个关键时间框架信号一致即可入场",
            risk_tolerance="单笔交易风险可达25-32%，追求高收益",
            trading_style="积极进取，快速捕捉市场机会，追求最大化收益",
        ),
    }
    
    return strategy_configs[strategy]


def generate_trading_prompt(data: Dict[str, Any]) -> str:
    """
    生成交易提示词（参照1.md格式）
    
    Args:
        data: 包含以下字段的字典：
            - minutes_elapsed: 运行分钟数
            - iteration: 迭代次数
            - interval_minutes: 执行周期（分钟）
            - market_data: 市场数据字典
            - account_info: 账户信息字典
            - positions: 持仓列表
            - trade_history: 历史交易记录（可选）
            - recent_decisions: 最近的AI决策（可选）
            
    Returns:
        完整的交易提示词字符串
        
    对应TypeScript: generateTradingPrompt()
    """
    minutes_elapsed = data.get('minutes_elapsed', 0)
    iteration = data.get('iteration', 1)
    interval_minutes = data.get('interval_minutes', 5)
    market_data = data.get('market_data', {})
    account_info = data.get('account_info', {})
    positions = data.get('positions', [])
    trade_history = data.get('trade_history', [])
    recent_decisions = data.get('recent_decisions', [])
    
    current_time = format_china_time()
    
    # 获取当前策略参数
    strategy = get_trading_strategy()
    params = get_strategy_params(strategy)
    
    # 判断是否启用自动监控止损和移动止盈
    is_code_level_protection_enabled = (strategy == "swing-trend")
    
    prompt = f"""【交易周期 #{iteration}】{current_time}
已运行 {minutes_elapsed} 分钟，执行周期 {interval_minutes} 分钟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当前策略：{params.name}（{params.description}）
目标月回报：{'10-20%' if params.name == '稳健' else '20-40%' if params.name == '平衡' else '40%+'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【硬性风控底线 - 系统强制执行】
┌─────────────────────────────────────────┐
│ 单笔亏损 ≤ {RISK_PARAMS.EXTREME_STOP_LOSS_PERCENT}%：强制平仓               │
│ 持仓时间 ≥ {RISK_PARAMS.MAX_HOLDING_HOURS}小时：强制平仓             │
└─────────────────────────────────────────┘

【AI战术决策 - 强烈建议遵守】
┌─────────────────────────────────────────┐
│ 策略止损：{params.stop_loss_low}% ~ {params.stop_loss_high}%（根据杠杆）│
│ 分批止盈：                               │
│   • 盈利≥+{params.partial_take_profit_stage1.trigger}% → 平仓{params.partial_take_profit_stage1.close_percent}%  │
│   • 盈利≥+{params.partial_take_profit_stage2.trigger}% → 平仓{params.partial_take_profit_stage2.close_percent}%  │
│   • 盈利≥+{params.partial_take_profit_stage3.trigger}% → 平仓{params.partial_take_profit_stage3.close_percent}% │
│ 峰值回撤：≥{params.peak_drawdown_protection}% → 危险信号，立即平仓 │
└─────────────────────────────────────────┘

【决策流程 - 按优先级执行】
(1) 持仓管理（最优先）：
   检查每个持仓的止损/止盈/峰值回撤 → closePosition
   
(2) 新开仓评估：
   分析市场数据 → 识别双向机会（做多/做空） → openPosition
   
(3) 加仓评估：
   盈利>5%且趋势强化 → openPosition（≤50%原仓位，相同或更低杠杆）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【数据说明】
本提示词已预加载所有必需数据：
• 所有币种的市场数据和技术指标（多时间框架）
• 账户信息（余额、收益率、夏普比率）
• 当前持仓状态（盈亏、持仓时间、杠杆）
• 历史交易记录（最近10笔）

所有币种的当前市场状态
"""
    
    # 输出每个币种的市场数据
    for symbol, data_raw in market_data.items():
        prompt += f"\n所有 {symbol} 数据\n"
        prompt += f"当前价格 = {data_raw.get('price', 0):.1f}, "
        prompt += f"当前EMA20 = {data_raw.get('ema20', 0):.3f}, "
        prompt += f"当前MACD = {data_raw.get('macd', 0):.3f}, "
        prompt += f"当前RSI（7周期） = {data_raw.get('rsi7', 0):.3f}\n\n"
        
        # 资金费率
        if 'fundingRate' in data_raw:
            prompt += f"此外，这是 {symbol} 永续合约的最新资金费率：\n"
            prompt += f"资金费率: {data_raw['fundingRate']:.2e}\n\n"
        
        # 日内时序数据
        if 'intradaySeries' in data_raw and data_raw['intradaySeries'].get('midPrices'):
            series = data_raw['intradaySeries']
            prompt += "日内序列（按分钟，最旧 → 最新）：\n\n"
            
            # 中间价
            mid_prices = series.get('midPrices', [])
            if mid_prices:
                prompt += f"中间价: [{', '.join(f'{p:.1f}' for p in mid_prices)}]\n\n"
            
            # EMA20序列
            ema20_series = series.get('ema20Series', [])
            if ema20_series:
                prompt += f"EMA指标（20周期）: [{', '.join(f'{e:.3f}' for e in ema20_series)}]\n\n"
            
            # MACD序列
            macd_series = series.get('macdSeries', [])
            if macd_series:
                prompt += f"MACD指标: [{', '.join(f'{m:.3f}' for m in macd_series)}]\n\n"
            
            # RSI7序列
            rsi7_series = series.get('rsi7Series', [])
            if rsi7_series:
                prompt += f"RSI指标（7周期）: [{', '.join(f'{r:.3f}' for r in rsi7_series)}]\n\n"
            
            # RSI14序列
            rsi14_series = series.get('rsi14Series', [])
            if rsi14_series:
                prompt += f"RSI指标（14周期）: [{', '.join(f'{r:.3f}' for r in rsi14_series)}]\n\n"
        
        # 多时间框架指标
        if 'timeframes' in data_raw:
            prompt += "多时间框架指标：\n\n"
            
            tf_list = [
                ("1m", "1分钟"),
                ("3m", "3分钟"),
                ("5m", "5分钟"),
                ("15m", "15分钟"),
                ("30m", "30分钟"),
                ("1h", "1小时"),
            ]
            
            for tf_key, tf_name in tf_list:
                tf_data = data_raw['timeframes'].get(tf_key)
                if tf_data:
                    prompt += f"{tf_name}: "
                    prompt += f"价格={tf_data.get('currentPrice', 0):.2f}, "
                    prompt += f"EMA20={tf_data.get('ema20', 0):.3f}, "
                    prompt += f"EMA50={tf_data.get('ema50', 0):.3f}, "
                    prompt += f"MACD={tf_data.get('macd', 0):.3f}, "
                    prompt += f"RSI7={tf_data.get('rsi7', 0):.2f}, "
                    prompt += f"RSI14={tf_data.get('rsi14', 0):.2f}, "
                    prompt += f"成交量={tf_data.get('volume', 0):.2f}\n"
            prompt += "\n"
    
    # 账户信息
    prompt += "\n以下是您的账户信息和表现\n"
    
    # 账户回撤
    if 'initialBalance' in account_info and 'peakBalance' in account_info:
        initial = account_info['initialBalance']
        peak = account_info['peakBalance']
        total = account_info.get('totalBalance', 0)
        
        drawdown_from_peak = ((peak - total) / peak) * 100 if peak > 0 else 0
        drawdown_from_initial = ((initial - total) / initial) * 100 if initial > 0 else 0
        
        prompt += f"初始账户净值: {initial:.2f} USDT\n"
        prompt += f"峰值账户净值: {peak:.2f} USDT\n"
        prompt += f"当前账户价值: {total:.2f} USDT\n"
        prompt += f"账户回撤 (从峰值): {'' if drawdown_from_peak >= 0 else '+'}{-drawdown_from_peak:.2f}%\n"
        prompt += f"账户回撤 (从初始): {'' if drawdown_from_initial >= 0 else '+'}{-drawdown_from_initial:.2f}%\n\n"
        
        # 风控警告
        if drawdown_from_peak >= RISK_PARAMS.ACCOUNT_DRAWDOWN_WARNING_PERCENT:
            prompt += f"提醒: 账户回撤已达到 {drawdown_from_peak:.2f}%，请谨慎交易\n\n"
    else:
        prompt += f"当前账户价值: {account_info.get('totalBalance', 0):.2f} USDT\n\n"
    
    prompt += f"当前总收益率: {account_info.get('returnPercent', 0):.2f}%\n\n"
    
    # 未实现盈亏
    total_unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions)
    total_balance = account_info.get('totalBalance', 0)
    
    prompt += f"可用资金: {account_info.get('availableBalance', 0):.1f} USDT\n\n"
    prompt += f"未实现盈亏: {total_unrealized_pnl:.2f} USDT "
    prompt += f"({'+' if total_unrealized_pnl >= 0 else ''}{(total_unrealized_pnl / total_balance * 100):.2f}%)\n\n"
    
    # 当前持仓
    if positions:
        prompt += "以下是您当前的持仓信息。重要说明：\n"
        prompt += "- 所有\"盈亏百分比\"都是考虑杠杆后的值\n"
        prompt += "- 例如：10倍杠杆，价格上涨0.5%，则盈亏百分比 = +5%\n"
        prompt += "- 请直接使用系统提供的盈亏百分比\n\n"
        
        for pos in positions:
            # 计算盈亏百分比
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('current_price', 0)
            leverage = pos.get('leverage', 1)
            side = pos.get('side', 'long')
            
            if entry_price > 0:
                price_change_percent = ((current_price - entry_price) / entry_price * 100 * 
                                      (1 if side == 'long' else -1))
                pnl_percent = price_change_percent * leverage
            else:
                pnl_percent = 0
            
            # 计算持仓时长
            opened_at = pos.get('opened_at')
            if opened_at:
                if isinstance(opened_at, str):
                    opened_time = datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
                else:
                    opened_time = opened_at
                
                now = datetime.now(opened_time.tzinfo) if opened_time.tzinfo else datetime.now()
                holding_minutes = int((now - opened_time).total_seconds() / 60)
                holding_hours = holding_minutes / 60
                remaining_hours = max(0, 36 - holding_hours)
                holding_cycles = holding_minutes // interval_minutes
                max_cycles = (36 * 60) // interval_minutes
                remaining_cycles = max(0, max_cycles - holding_cycles)
            else:
                holding_hours = 0
                holding_minutes = 0
                remaining_hours = 36
                holding_cycles = 0
                remaining_cycles = max_cycles = (36 * 60) // interval_minutes
            
            prompt += f"当前活跃持仓: {pos.get('symbol', 'UNKNOWN')} "
            prompt += f"{'做多' if side == 'long' else '做空'}\n"
            prompt += f"  杠杆倍数: {leverage}x\n"
            prompt += f"  盈亏百分比: {'+' if pnl_percent >= 0 else ''}{pnl_percent:.2f}% (已考虑杠杆倍数)\n"
            prompt += f"  盈亏金额: {'+' if pos.get('unrealized_pnl', 0) >= 0 else ''}{pos.get('unrealized_pnl', 0):.2f} USDT\n"
            prompt += f"  开仓价: {entry_price:.2f}\n"
            prompt += f"  当前价: {current_price:.2f}\n"
            prompt += f"  开仓时间: {format_china_time(opened_at) if opened_at else 'N/A'}\n"
            prompt += f"  已持仓: {holding_hours:.1f} 小时 ({holding_minutes} 分钟, {holding_cycles} 个周期)\n"
            prompt += f"  距离36小时限制: {remaining_hours:.1f} 小时 ({remaining_cycles} 个周期)\n"
            
            # 警告
            if remaining_hours < 2:
                prompt += "  警告: 即将达到36小时持仓限制,必须立即平仓!\n"
            elif remaining_hours < 4:
                prompt += "  提醒: 距离36小时限制不足4小时,请准备平仓\n"
            
            prompt += "\n"
    
    # Sharpe Ratio
    if 'sharpeRatio' in account_info:
        prompt += f"夏普比率: {account_info['sharpeRatio']:.3f}\n\n"
    
    # 历史交易记录
    if trade_history:
        prompt += "\n最近交易历史（最近10笔交易，最旧 → 最新）：\n"
        prompt += "重要说明：以下仅为最近10条交易的统计，用于分析近期策略表现。\n\n"
        
        total_profit = 0
        profit_count = 0
        loss_count = 0
        
        for trade in trade_history[:10]:  # 只取最近10笔
            trade_time = format_china_time(trade.get('timestamp'))
            
            prompt += f"交易: {trade.get('symbol', 'UNKNOWN')} "
            prompt += f"{'开仓' if trade.get('type') == 'open' else '平仓'} "
            prompt += f"{trade.get('side', 'UNKNOWN').upper()}\n"
            prompt += f"  时间: {trade_time}\n"
            prompt += f"  价格: {trade.get('price', 0):.2f}, "
            prompt += f"数量: {trade.get('quantity', 0):.4f}, "
            prompt += f"杠杆: {trade.get('leverage', 1)}x\n"
            prompt += f"  手续费: {trade.get('fee', 0):.4f} USDT\n"
            
            if trade.get('type') == 'close' and 'pnl' in trade:
                pnl = trade['pnl']
                prompt += f"  盈亏: {'+' if pnl >= 0 else ''}{pnl:.2f} USDT\n"
                total_profit += pnl
                if pnl > 0:
                    profit_count += 1
                elif pnl < 0:
                    loss_count += 1
            
            prompt += "\n"
        
        if profit_count + loss_count > 0:
            win_rate = profit_count / (profit_count + loss_count) * 100
            prompt += "最近10条交易统计（仅供参考）:\n"
            prompt += f"  - 胜率: {win_rate:.1f}%\n"
            prompt += f"  - 盈利交易: {profit_count}笔\n"
            prompt += f"  - 亏损交易: {loss_count}笔\n"
            prompt += f"  - 最近10条净盈亏: {'+' if total_profit >= 0 else ''}{total_profit:.2f} USDT\n\n"
    
    # 最近的AI决策
    if recent_decisions:
        prompt += "\n您上一次的决策：\n"
        prompt += "使用此信息作为参考，并基于当前市场状况做出决策。\n\n"
        
        for decision in recent_decisions[:3]:  # 只显示最近3次
            decision_time = format_china_time(decision.get('timestamp'))
            
            prompt += f"决策 #{decision.get('iteration', 0)} ({decision_time}):\n"
            prompt += f"  账户价值: {decision.get('account_value', 0):.2f} USDT\n"
            prompt += f"  持仓数量: {decision.get('positions_count', 0)}\n"
            prompt += f"  决策: {decision.get('decision', 'N/A')}\n\n"
    
    return prompt


if __name__ == "__main__":
    # 测试函数
    print("\n" + "=" * 80)
    print("🧪 测试AI决策引擎")
    print("=" * 80 + "\n")
    
    # 测试策略参数
    print("📍 测试1：获取策略参数")
    for strategy in ["conservative", "balanced", "aggressive", "ultra-short", "swing-trend"]:
        params = get_strategy_params(strategy)  # type: ignore
        print(f"   {params.name}: 杠杆{params.leverage_min}-{params.leverage_max}x, "
              f"止损{params.stop_loss_low}%~{params.stop_loss_high}%")
    print("   ✅ 策略参数获取成功\n")
    
    # 测试提示词生成
    print("📍 测试2：生成交易提示词")
    test_data = {
        'minutes_elapsed': 60,
        'iteration': 12,
        'interval_minutes': 5,
        'market_data': {
            'BTC': {
                'price': 103000,
                'ema20': 102500,
                'macd': 150.5,
                'rsi7': 65.3,
                'fundingRate': 0.0001,
            }
        },
        'account_info': {
            'totalBalance': 10000,
            'availableBalance': 5000,
            'returnPercent': 15.5,
        },
        'positions': [],
    }
    
    prompt = generate_trading_prompt(test_data)
    print(f"   提示词长度: {len(prompt)} 字符")
    print(f"   包含BTC数据: {'BTC' in prompt}")
    print(f"   ✅ 提示词生成成功\n")
    
    print("=" * 80)
    print("🎉 所有测试通过！")
    print("=" * 80 + "\n")

