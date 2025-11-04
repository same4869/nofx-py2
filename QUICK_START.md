# 🚀 快速开始指南

> 5分钟快速部署Open NOF1.ai Python版

---

## 📋 准备工作

### 必需条件
- ✅ Python 3.9或更高版本
- ✅ Gate.io账户和API密钥
- ✅ 10分钟时间

### 可选条件
- OpenAI API密钥（用于AI决策，可选）

---

## 🎯 三步启动

### 第一步：安装

```bash
# 1. 进入项目目录
cd python

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# 4. 安装依赖（约2-3分钟）
pip install -r requirements.txt
```

### 第二步：配置

```bash
# 1. 复制配置文件
cp .env.example .env

# 2. 编辑.env文件
vi .env  # 或使用你喜欢的编辑器

# 3. 必须配置的项：
GATE_API_KEY=your_gate_api_key_here
GATE_API_SECRET=your_gate_api_secret_here
GATE_USE_TESTNET=true  # 建议先用测试网

# 4. 可选配置的项：
OPENAI_API_KEY=your_openai_key_here  # 用于AI决策
TRADING_STRATEGY=balanced  # 交易策略
```

### 第三步：运行

```bash
# 1. 初始化数据库
python -c "from core.database import init_database; import asyncio; asyncio.run(init_database())"

# 2. 启动系统
python main.py

# 3. 访问监控界面
# 打开浏览器：http://localhost:3100
```

---

## 🎨 配置选项

### 交易策略选择

在`.env`中设置`TRADING_STRATEGY`：

```bash
# 保守策略 - 低风险，稳定收益
TRADING_STRATEGY=conservative

# 平衡策略 - 风险收益均衡（推荐）
TRADING_STRATEGY=balanced

# 激进策略 - 高风险高收益
TRADING_STRATEGY=aggressive

# 超短线 - 快进快出
TRADING_STRATEGY=ultra-short

# 波段趋势 - 趋势跟踪
TRADING_STRATEGY=swing-trend
```

### 风险控制

```bash
# 最大持仓数量
MAX_POSITIONS=5

# 最大杠杆倍数
MAX_LEVERAGE=10

# 账户止损线（USDT）
ACCOUNT_STOP_LOSS_USDT=50

# 账户止盈线（USDT）
ACCOUNT_TAKE_PROFIT_USDT=200

# 交易循环间隔（分钟）
TRADING_INTERVAL_MINUTES=5
```

---

## 🧪 测试系统

### 运行测试确保一切正常

```bash
# 测试基础模块
./test_setup.sh

# 测试交易所API
./test_phase2.sh

# 测试技术指标
./test_phase3.sh

# 测试AI决策
./test_phase4.sh

# 测试集成功能
./test_phase5.sh

# 测试完整系统
./test_phase6.sh

# 测试Web API
./test_phase7.sh
```

---

## 📊 监控界面

启动系统后，访问 **http://localhost:3100** 查看：

### 主要功能
- 📊 **账户总览** - 总资产、可用余额、收益率
- 💼 **当前持仓** - 实时持仓和盈亏
- 📈 **交易统计** - 胜率、盈亏统计
- 📜 **交易历史** - 最近交易记录
- 💰 **实时价格** - 主流币种价格

### API文档
访问 **http://localhost:3100/docs** 查看完整API文档

---

## ⚙️ 常用命令

### 启动和停止

```bash
# 启动系统
python main.py

# 停止系统
Ctrl + C

# 后台运行（使用nohup）
nohup python main.py > output.log 2>&1 &

# 查看日志
tail -f ./logs/trading.log
```

### 仅运行示例

```bash
# 市场分析示例
python examples/trading_example.py

# AI决策示例
python examples/ai_decision_example.py
```

---

## 🔒 安全建议

### ⚠️ 重要提示

1. **使用测试网测试**
   ```bash
   GATE_USE_TESTNET=true
   ```

2. **小额资金测试**
   - 实盘前先用小额资金测试
   - 建议初始资金不超过100 USDT

3. **设置止损保护**
   ```bash
   ACCOUNT_STOP_LOSS_USDT=50  # 账户总亏损50 USDT自动停止
   ```

4. **定期检查**
   - 每天检查账户状态
   - 查看日志文件
   - 监控持仓情况

5. **不要泄露密钥**
   - 不要提交`.env`文件到git
   - 不要在公开场合分享API密钥

---

## 🐛 常见问题

### Q1: 依赖安装失败？
```bash
# 尝试升级pip
pip install --upgrade pip

# 重新安装
pip install -r requirements.txt
```

### Q2: API调用失败？
- 检查API密钥是否正确
- 检查网络连接
- 查看日志：`./logs/trading.log`

### Q3: 测试网地址？
Gate.io测试网：https://fx-testnet.gateio.ws/

### Q4: 如何停止自动交易？
```bash
# 方法1：在.env中设置
ENABLE_AUTO_TRADING=false

# 方法2：只启动Web监控
# 删除或注释掉main.py中的自动交易代码
```

### Q5: 如何修改端口？
```bash
# 在.env中修改
PORT=3100  # 改为你想要的端口
```

---

## 📚 进一步学习

### 文档资源
- [完整README](README.md) - 项目完整介绍
- [文档索引](INDEX.md) - 所有文档导航
- [项目完成总结](PROJECT_COMPLETE.md) - 详细技术说明

### 阶段文档
- [阶段1-7完成报告](PHASE1_COMPLETE.md) - 各阶段详细文档

---

## 🎯 下一步

### 初学者路线
1. ✅ 完成快速开始
2. ✅ 运行测试验证
3. ✅ 测试网测试
4. ✅ 小额实盘测试
5. ✅ 调整策略参数

### 进阶路线
1. 阅读[完整文档](README.md)
2. 查看[源代码](./services/)
3. 自定义交易策略
4. 开发新功能
5. 贡献代码

---

## 💬 获取帮助

遇到问题？

1. 📖 查看[文档](README.md)
2. 🔍 搜索[Issues](https://github.com/195440/open-nof1.ai/issues)
3. 💬 提问[讨论区](https://github.com/195440/open-nof1.ai/discussions)
4. 🐛 报告[Bug](https://github.com/195440/open-nof1.ai/issues/new)

---

<div align="center">

**🚀 开始你的AI交易之旅！**

</div>

