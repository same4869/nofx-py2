"""
AI决策示例脚本

演示如何使用OpenAI API进行交易决策

注意：需要配置有效的OPENAI_API_KEY才能运行
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from agents.trading_agent import generate_trading_prompt
from core.logger import logger

try:
    from openai import AsyncOpenAI
except ImportError:
    logger.warning("openai库未安装，请运行: pip install openai")
    AsyncOpenAI = None


async def get_ai_decision(prompt: str) -> str:
    """
    调用OpenAI API获取交易决策
    
    Args:
        prompt: 交易提示词
        
    Returns:
        AI的决策响应
    """
    if not AsyncOpenAI:
        return "❌ OpenAI库未安装"
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        return "❌ 请先配置OPENAI_API_KEY"
    
    # 创建OpenAI客户端
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
    )
    
    try:
        # 调用AI模型进行决策（支持OpenAI、DeepSeek等）
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL or "deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的加密货币交易助手，负责根据市场数据做出交易决策。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        
        # 提取决策内容
        decision = response.choices[0].message.content
        
        return decision
        
    except Exception as e:
        logger.error(f"OpenAI API调用失败: {e}")
        return f"❌ API调用失败: {str(e)}"


async def demo_ai_decision():
    """演示AI决策流程"""
    print("\n" + "=" * 80)
    print("🤖 AI交易决策示例")
    print("=" * 80 + "\n")
    
    # 创建模拟的市场数据
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
                'fundingRate': 0.01,
                'timeframes': {
                    '5m': {
                        'ema20': 64800,
                        'ema50': 64500,
                        'rsi14': 58,
                        'macd': 120,
                    },
                    '15m': {
                        'ema20': 64700,
                        'ema50': 64400,
                        'rsi14': 60,
                        'macd': 150,
                    },
                    '1h': {
                        'ema20': 64600,
                        'ema50': 64200,
                        'rsi14': 62,
                        'macd': 180,
                    }
                }
            }
        },
        'account_info': {
            'totalBalance': 10000,
            'availableBalance': 9000,
            'returnPercent': 5.2,
        },
        'positions': [],
    }
    
    # 生成提示词
    print("📍 步骤1：生成AI提示词")
    prompt = generate_trading_prompt(mock_data)
    print(f"   提示词长度: {len(prompt)} 字符\n")
    
    # 显示提示词片段
    print("📍 步骤2：提示词预览")
    print("-" * 80)
    print(prompt[:500] + "...")
    print("-" * 80 + "\n")
    
    # 调用AI获取决策
    print("📍 步骤3：调用OpenAI API获取决策")
    decision = await get_ai_decision(prompt)
    print("\nAI决策响应：")
    print("-" * 80)
    print(decision)
    print("-" * 80 + "\n")
    
    # 解析决策（实际使用中需要更复杂的解析逻辑）
    print("📍 步骤4：解析决策内容")
    if "开仓" in decision or "买入" in decision:
        print("   ✅ AI建议开仓")
    elif "平仓" in decision or "卖出" in decision:
        print("   ✅ AI建议平仓")
    elif "持有" in decision or "观望" in decision:
        print("   ✅ AI建议持有")
    else:
        print("   ℹ️  决策需要进一步解析")
    
    print("\n" + "=" * 80)
    print("✅ AI决策示例完成")
    print("=" * 80 + "\n")
    
    print("💡 提示：")
    print("   - 实际交易系统需要严格的决策解析和验证")
    print("   - 应该记录所有AI决策到数据库")
    print("   - 需要实现风险控制和异常处理")
    print("   - 建议使用结构化输出（JSON格式）\n")


async def main():
    """主函数"""
    await demo_ai_decision()


if __name__ == "__main__":
    asyncio.run(main())

