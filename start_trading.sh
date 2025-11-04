#!/bin/bash

# Open NOF1.ai Python版 - 启动脚本

echo "========================================="
echo "Open NOF1.ai - AI加密货币自动交易系统"
echo "========================================="
echo ""

# 进入Python项目目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，请先运行 test_setup.sh 创建环境"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在，请复制.env.example并配置"
    exit 1
fi

# 显示配置信息
echo ""
echo "配置检查："
echo "  - 虚拟环境: ✅"
echo "  - 配置文件: ✅"
echo ""

# 启动交易系统
echo "启动交易系统..."
echo ""
python main.py

# 退出码
EXIT_CODE=$?

echo ""
echo "========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "系统已正常退出"
else
    echo "系统异常退出 (退出码: $EXIT_CODE)"
fi
echo "========================================="

exit $EXIT_CODE

