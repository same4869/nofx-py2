# DeepSeek AI 配置指南

> **推荐使用 DeepSeek**：性能优异、成本低廉（节省90%费用）、中文友好 🚀

---

## 📋 快速配置（3步）

### 1️⃣ 获取 DeepSeek API Key

访问 **[DeepSeek 平台](https://platform.deepseek.com/)** → 注册登录 → 创建 API Key

💰 **新用户福利**：注册即送免费额度！

### 2️⃣ 配置环境变量

在 `.env` 文件中添加：

```bash
# DeepSeek AI 配置
OPENAI_API_KEY=sk-your-deepseek-api-key-here
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

### 3️⃣ 测试运行

```bash
# 测试 AI 连接
python examples/ai_decision_example.py

# 启动系统
python main.py
```

---

## 🎯 完整配置示例

### 推荐配置（新手）

```bash
# ========== Gate.io 配置 ==========
GATE_API_KEY=your_gate_api_key
GATE_API_SECRET=your_gate_api_secret
GATE_USE_TESTNET=true

# ========== DeepSeek AI ==========
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat

# ========== 交易策略 ==========
TRADING_STRATEGY=balanced
MAX_LEVERAGE=10
MAX_POSITIONS=5
ACCOUNT_STOP_LOSS_USDT=50
```

---

## 🔄 切换其他 AI

### OpenAI

```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### OpenRouter（多模型）

```bash
OPENAI_API_KEY=sk-or-v1-your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=deepseek/deepseek-chat
```

---

## 💰 价格对比

| AI 提供商 | 输入价格 | 输出价格 | 相对成本 |
|-----------|---------|---------|----------|
| **DeepSeek** | ¥1/M | ¥2/M | **1x** ⭐ |
| GPT-4o-mini | $0.15/M | $0.6/M | ~10x |
| GPT-4o | $2.5/M | $10/M | ~100x |

**💡 每月可节省数百元 AI 费用！**

---

## ⚙️ 高级配置

### AI 参数调整

在 `examples/ai_decision_example.py` 中修改：

```python
response = await client.chat.completions.create(
    model=settings.OPENAI_MODEL,
    messages=[...],
    temperature=0.7,      # 0-2，越高越随机
    max_tokens=2000,      # 最大输出长度
)
```

**推荐参数**：
- **保守策略**：`temperature=0.3-0.5`
- **平衡策略**：`temperature=0.5-0.7`
- **激进策略**：`temperature=0.7-1.0`

---

## 🔧 故障排查

### API Key 无效

**检查清单**：
- ✅ API Key 完整（包含 `sk-` 前缀）
- ✅ 账户余额充足
- ✅ 没有多余空格

### 连接超时

```bash
# 增加超时时间
API_TIMEOUT=60
```

### 模型不存在

确认模型名称：
- DeepSeek 官方：`deepseek-chat`
- OpenRouter：`deepseek/deepseek-chat`

---

## 📊 性能对比

| 特性 | DeepSeek | OpenAI | Claude |
|------|----------|--------|--------|
| 💰 **成本** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 🇨🇳 **中文** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| ⚡ **速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 🎯 **准确性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 💡 最佳实践

### 成本控制
- 💰 合理设置 `max_tokens` 避免浪费
- 💰 监控每日消费，设置预算告警
- 💰 使用缓存减少重复计算

### 风险管理
- 🛡️ 不要完全依赖 AI，保留人工审核
- 🛡️ 设置严格止损，防止决策失误
- 🛡️ 小额测试，验证 AI 表现
- 🛡️ 持续监控，定期检查决策质量

---

## 🔗 相关资源

- 🌐 [DeepSeek 官网](https://www.deepseek.com/)
- 📘 [DeepSeek 平台](https://platform.deepseek.com/)
- 📚 [API 文档](https://platform.deepseek.com/docs)
- 💬 [GitHub Issues](https://github.com/195440/open-nof1.ai/issues)

---

---

## 🔗 相关文档

- [README](README.md) - 项目概览
- [快速开始](QUICK_START.md) - 5分钟部署
- [更新日志](CHANGELOG.md) - 版本记录

---

<div align="center">

**✨ 享受 DeepSeek 带来的智能交易体验！**

</div>
