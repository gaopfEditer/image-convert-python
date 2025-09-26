#!/bin/bash

echo "🎯 图片转换服务 - 快速启动"
echo "================================================"
echo

# 检查Python环境
echo "📦 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    echo "请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python环境正常"

# 检查依赖
echo "🔍 检查依赖..."
if ! python3 -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
    echo "❌ 缺少必要依赖"
    echo "请运行: pip install -r requirements.txt"
    exit 1
fi

echo "✅ 依赖检查通过"

# 初始化数据库
echo
echo "🗄️ 初始化数据库..."
echo "使用远程MySQL: 1.94.137.69:3306"
python3 init_db.py
if [ $? -ne 0 ]; then
    echo "❌ 数据库初始化失败"
    exit 1
fi

# 启动服务
echo
echo "🚀 启动服务..."
echo "📚 API文档: http://localhost:8000/docs"
echo "💡 按 Ctrl+C 停止服务"
echo "================================================"
echo

python3 dev_start.py
