#!/bin/bash

# 统一测试脚本 - Open NOF1.ai Python版

echo "========================================="
echo "Open NOF1.ai - 运行所有测试"
echo "========================================="
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在"
    echo "请先运行: python -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 运行所有测试
echo ""
echo "========================================="
echo "运行所有测试..."
echo "========================================="
echo ""

python -m pytest tests/ -v --tb=short

# 保存退出码
EXIT_CODE=$?

echo ""
echo "========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 所有测试通过！"
else
    echo "❌ 部分测试失败"
fi
echo "========================================="

exit $EXIT_CODE

