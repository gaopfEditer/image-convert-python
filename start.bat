@echo off
chcp 65001 >nul
echo 🎯 图片转换服务 - 快速启动
echo ================================================
echo.

echo 📦 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 🗄️ 初始化数据库...
echo 使用远程MySQL: 1.94.137.69:3306
python init_db.py
if errorlevel 1 (
    echo ❌ 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo 🚀 启动服务...
echo 📚 API文档: http://localhost:8000/docs
echo 💡 按 Ctrl+C 停止服务
echo ================================================
echo.

python dev_start.py

pause
