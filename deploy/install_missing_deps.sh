#!/bin/bash
# 安装缺失的依赖包

echo "🔧 安装缺失的Python依赖包..."

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 检测到虚拟环境: $VIRTUAL_ENV"
    pip install -r requirements.txt
else
    echo "⚠️ 未检测到虚拟环境，使用系统Python"
    pip3 install -r requirements.txt
fi

echo "📦 安装特定缺失的包..."
pip install requests>=2.31.0
pip install schedule>=1.2.0

echo "✅ 依赖安装完成！"

# 验证安装
echo "🔍 验证关键模块..."
python3 -c "
try:
    import requests
    print('✅ requests 模块正常')
except ImportError as e:
    print(f'❌ requests 模块缺失: {e}')

try:
    import schedule
    print('✅ schedule 模块正常')
except ImportError as e:
    print(f'❌ schedule 模块缺失: {e}')

try:
    import fastapi
    print('✅ fastapi 模块正常')
except ImportError as e:
    print(f'❌ fastapi 模块缺失: {e}')
"
