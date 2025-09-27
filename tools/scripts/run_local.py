#!/usr/bin/env python3
"""
本地运行脚本 - 快速启动图片转换服务
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pillow
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def create_directories():
    """创建必要的目录"""
    print("📁 创建目录...")
    directories = [
        "uploads",
        "uploads/uploads", 
        "uploads/converted",
        "uploads/temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")

def update_config():
    """更新配置文件"""
    print("⚙️ 更新配置...")
    
    # 检查是否有本地配置文件
    if not os.path.exists("config_local.py"):
        print("📝 创建本地配置文件...")
        with open("config_local.py", "w", encoding="utf-8") as f:
            f.write('''from config import settings

# 本地开发配置
settings.database_url = "postgresql://postgres:password@localhost:5432/image_convert_db"
settings.secret_key = "your-secret-key-for-development-only"
settings.alipay_app_id = ""
settings.alipay_private_key = ""
settings.alipay_public_key = ""
settings.wechat_app_id = ""
settings.wechat_mch_id = ""
settings.wechat_api_key = ""

# 开发环境设置
settings.debug = True
''')
        print("  ✅ 已创建 config_local.py")
    else:
        print("  ✅ 配置文件已存在")

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    print("=" * 60)
    print("📚 API文档地址:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc:      http://localhost:8000/redoc")
    print("=" * 60)
    print("💡 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        # 启动服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎯 图片转换服务 - 本地运行")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建目录
    create_directories()
    
    # 更新配置
    update_config()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
