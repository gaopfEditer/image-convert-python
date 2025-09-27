@echo off
REM Windows部署脚本

echo 🚀 开始Windows部署图片转换服务...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查pip是否安装
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip未安装，请先安装pip
    pause
    exit /b 1
)

REM 创建虚拟环境
echo 🐍 创建Python虚拟环境...
python -m venv venv

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📦 安装Python依赖...
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

REM 创建上传目录
echo 📂 创建上传目录...
if not exist "uploads\converted" mkdir uploads\converted
if not exist "uploads\temp" mkdir uploads\temp
if not exist "uploads\uploads" mkdir uploads\uploads

REM 创建日志目录
echo 📝 创建日志目录...
if not exist "logs" mkdir logs

REM 创建启动脚本
echo 🔧 创建启动脚本...
echo @echo off > start.bat
echo echo 🚀 启动图片转换服务... >> start.bat
echo call venv\Scripts\activate.bat >> start.bat
echo python simple_start.py >> start.bat
echo pause >> start.bat

REM 创建停止脚本
echo 🔧 创建停止脚本...
echo @echo off > stop.bat
echo echo 🛑 停止图片转换服务... >> stop.bat
echo taskkill /f /im python.exe >> stop.bat
echo pause >> stop.bat

REM 创建重启脚本
echo 🔧 创建重启脚本...
echo @echo off > restart.bat
echo echo 🔄 重启图片转换服务... >> restart.bat
echo call stop.bat >> restart.bat
echo timeout /t 3 /nobreak >> restart.bat
echo call start.bat >> restart.bat

echo.
echo 🎉 Windows部署完成！
echo ================================
echo 📋 使用方法:
echo   启动服务: start.bat
echo   停止服务: stop.bat
echo   重启服务: restart.bat
echo.
echo 📋 访问地址:
echo   本地访问: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo   健康检查: http://localhost:8000/health
echo.
echo 📋 注意事项:
echo   1. 确保端口8000未被占用
echo   2. 确保MySQL和Redis服务正在运行
echo   3. 首次运行前请先初始化数据库
echo ================================
pause
