# 更新日志

本项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.1.0] - 2025-11-05

### ✨ 新增 - DeepSeek AI 支持

- ✅ 完整支持 DeepSeek 官方 API
- ✅ 设置 DeepSeek 为默认 AI 引擎（成本降低 90%）
- ✅ 创建精简的 [DeepSeek 配置指南](DEEPSEEK_SETUP.md)
- ✅ 支持多 AI 提供商切换（DeepSeek/OpenAI/OpenRouter）

### 🔧 修复

- 🐛 修复配置字段名不一致（`AI_MODEL_NAME` → `OPENAI_MODEL`）
- 🐛 更新默认配置为 DeepSeek API
- 🐛 统一所有 AI 模型引用

### 📚 文档

- 📝 更新 README 和 QUICK_START，添加 DeepSeek 配置
- 📝 整合并精简文档，删除冗余内容
- 📝 添加详细的配置示例和故障排查

### 💡 优化

- 💰 AI 成本降低 90%（DeepSeek vs OpenAI）
- 🚀 中文交易决策质量提升
- ⚡ AI 响应速度更快

---

## [1.0.0] - 2025-11-04

### 🎉 首次发布

完整的Python版本，功能与TypeScript版本完全对等。

### ✨ 新增功能

#### 阶段1：项目基础搭建
- 配置管理系统（pydantic-settings）
- 日志系统（loguru）
- 数据库连接（SQLAlchemy + aiosqlite）
- 数据模型定义
- 时间工具函数

#### 阶段2：交易所API封装
- Gate.io API完整封装
- 基于ccxt的统一接口
- 自动重试机制
- 测试网/正式网切换
- 完整的错误处理

#### 阶段3：技术指标计算
- EMA（指数移动平均）
- MACD（移动平均收敛散度）
- RSI（相对强弱指标）
- ATR（平均真实波幅）
- 多时间周期分析
- 日内时序数据处理

#### 阶段4：AI决策引擎
- OpenAI API集成
- 5种交易策略配置
  - conservative（保守）
  - balanced（平衡）
  - aggressive（激进）
  - ultra-short（超短线）
  - swing-trend（波段趋势）
- 智能提示词生成
- 策略参数动态计算

#### 阶段5：集成测试与示例
- 市场分析示例
- AI决策示例
- 完整流水线测试
- 错误处理测试
- 使用文档

#### 阶段6：完整交易系统
- 自动交易循环
- 账户状态记录器
- 止损监控
- 移动止盈监控
- 优雅启动和关闭
- 主程序入口

#### 阶段7：Web API和监控界面
- 8个RESTful API端点
- 实时监控界面
- 深色主题设计
- 响应式布局
- 自动数据刷新
- FastAPI Swagger文档

### 📊 项目统计

- **代码行数**: 8000+
- **文件数量**: 50+
- **测试用例**: 46个
- **测试通过率**: 100%
- **文档数量**: 20+

### 🔧 技术栈

- Python 3.9+
- FastAPI 0.121+
- SQLAlchemy 2.0+
- ccxt 4.2+
- pandas 2.0+
- pandas-ta 0.3.14b+
- OpenAI 1.0+
- Loguru 0.7+

### 📚 文档

- 完整README
- 快速开始指南
- 7个阶段完成报告
- 项目完成总结
- 文档索引
- API使用指南

### ✅ 测试

- 阶段1：7个测试（基础模块）
- 阶段2：8个测试（交易所API）
- 阶段3：9个测试（技术指标）
- 阶段4：6个测试（AI决策）
- 阶段5：5个测试（集成测试）
- 阶段6：6个测试（系统测试）
- 阶段7：5个测试（Web API）

---

## 版本说明

### 版本号规则

版本号格式：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API变更
- **次版本号**：向下兼容的功能新增
- **修订号**：向下兼容的问题修正

### 更新类型

- `Added` - 新增功能
- `Changed` - 功能变更
- `Deprecated` - 即将废弃的功能
- `Removed` - 已移除的功能
- `Fixed` - 问题修复
- `Security` - 安全相关

---

## 路线图

### v1.1.0（计划中）
- [ ] 更多技术指标支持
- [ ] WebSocket实时数据推送
- [ ] 回测引擎
- [ ] 多账户管理

### v1.2.0（考虑中）
- [ ] Telegram通知
- [ ] 移动端优化
- [ ] 更多交易所支持
- [ ] 社区策略市场

---

## 贡献者

感谢所有为本项目做出贡献的人！

- [@195440](https://github.com/195440) - 项目创始人
- TypeScript版本贡献者
- Python版本迁移团队

---

**完整发布说明**: https://github.com/195440/open-nof1.ai/releases/tag/v1.0.0

