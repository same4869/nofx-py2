# Open NOF1.ai Python版 - 文档索引

> 快速导航，帮助你找到需要的文档

---

## 🚀 新手入门

| 文档 | 说明 | 推荐 |
|-----|------|-----|
| [README.md](README.md) | 项目完整说明 | ⭐⭐⭐ 必读 |
| [QUICK_START.md](QUICK_START.md) | 5分钟快速开始 | ⭐⭐⭐ 必读 |

---

## 📚 核心文档

### 项目说明
- [README.md](README.md) - 完整的项目介绍、功能说明和使用指南
- [QUICK_START.md](QUICK_START.md) - 快速安装和配置指南（新手推荐）

### 项目状态
- [FINAL_PROJECT_STATUS.md](FINAL_PROJECT_STATUS.md) - 最终项目状态和功能清单
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - 项目完成总结和技术详情
- [CHANGELOG.md](CHANGELOG.md) - 版本更新日志

---

## ⚙️ 配置文件

- `.env.example` - 环境变量配置模板
- `requirements.txt` - Python依赖列表
- `.gitignore` - Git忽略配置

---

## 📁 项目结构

```
python/
├── config/              # 配置模块
│   ├── settings.py     # 环境配置
│   └── risk_params.py  # 风险参数
├── core/               # 核心模块
│   ├── database.py     # 数据库
│   ├── logger.py       # 日志系统
│   └── models.py       # 数据模型
├── services/           # 业务服务
│   ├── exchange.py     # 交易所API
│   └── market_analysis.py  # 技术分析
├── agents/             # AI决策
│   └── trading_agent.py    # 交易策略
├── scheduler/          # 定时任务
│   ├── trading_loop.py     # 交易循环
│   ├── account_recorder.py # 账户记录
│   ├── stop_loss_monitor.py    # 止损监控
│   └── trailing_stop_monitor.py # 移动止盈
├── api/                # Web API
│   └── routes.py       # API路由
├── static/             # 静态文件
│   ├── index.html      # 监控界面
│   ├── css/            # 样式
│   └── js/             # 前端逻辑
├── tests/              # 测试文件
├── examples/           # 使用示例
├── utils/              # 工具函数
└── main.py             # 主程序
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
./run_tests.sh

# 或手动运行
python -m pytest tests/ -v
```

### 测试文件
- `tests/test_phase1.py` - 基础模块测试
- `tests/test_phase2.py` - API封装测试
- `tests/test_phase3.py` - 技术指标测试
- `tests/test_phase4.py` - AI决策测试
- `tests/test_phase5.py` - 集成测试
- `tests/test_phase6.py` - 系统测试
- `tests/test_phase7.py` - Web API测试

---

## 📖 使用示例

### 示例代码位置
- `examples/trading_example.py` - 市场分析完整示例
- `examples/ai_decision_example.py` - AI决策示例

### 运行示例
```bash
# 市场分析示例
python examples/trading_example.py

# AI决策示例
python examples/ai_decision_example.py
```

---

## 🔧 按功能查找

### 数据获取
- 实时价格：`services/exchange.py::get_futures_ticker()`
- K线数据：`services/exchange.py::get_futures_candles()`
- 账户信息：`services/exchange.py::get_account()`
- 持仓信息：`services/exchange.py::get_positions()`

### 技术分析
- EMA指标：`services/market_analysis.py::calc_ema()`
- MACD指标：`services/market_analysis.py::calc_macd()`
- RSI指标：`services/market_analysis.py::calc_rsi()`
- ATR指标：`services/market_analysis.py::calc_atr()`
- 综合分析：`services/market_analysis.py::calculate_indicators()`

### AI决策
- 策略配置：`agents/trading_agent.py::get_strategy_params()`
- 提示词生成：`agents/trading_agent.py::generate_trading_prompt()`
- 风险配置：`agents/trading_agent.py::get_account_risk_config()`

### Web监控
- 监控界面：`http://localhost:3100`
- API文档：`http://localhost:3100/docs`
- API端点：`api/routes.py`

---

## 📖 按学习路径

### 新手入门
1. 阅读 [README.md](README.md) 了解项目
2. 按照 [QUICK_START.md](QUICK_START.md) 安装配置
3. 运行示例 `examples/trading_example.py`
4. 查看 [FINAL_PROJECT_STATUS.md](FINAL_PROJECT_STATUS.md)

### 深入理解
1. 阅读源码：`services/`, `agents/`, `scheduler/`
2. 查看测试代码：`tests/`
3. 运行测试验证
4. 修改配置尝试不同策略

### 二次开发
1. 阅读 [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)
2. 研究核心模块源码
3. 参考 `examples/` 示例
4. 编写自己的策略

---

## 🔗 外部资源

- [ccxt文档](https://docs.ccxt.com/) - 交易所API库
- [pandas-ta文档](https://github.com/twopirllc/pandas-ta) - 技术指标库
- [FastAPI文档](https://fastapi.tiangolo.com/) - Web框架
- [SQLAlchemy文档](https://docs.sqlalchemy.org/) - ORM框架

---

## 💬 获取帮助

如果在使用过程中遇到问题：

1. **查阅文档** - 从 README.md 开始
2. **运行测试** - 使用测试定位问题
3. **查看日志** - `./logs/trading.log`
4. **提交Issue** - [GitHub Issues](https://github.com/195440/open-nof1.ai/issues)

---

## 📊 项目统计

- **代码行数**: 8000+ 行
- **测试用例**: 46 个
- **测试通过率**: 100%
- **文档数量**: 7 个核心文档
- **功能完成度**: 100%

---

**Happy Coding! 🚀**

_最后更新: 2025-11-04_
