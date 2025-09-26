#!/usr/bin/env python3
"""
远程数据库快速启动脚本
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
        import pymysql
        import redis
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def test_connections():
    """测试数据库和Redis连接"""
    print("🔍 测试远程连接...")
    try:
        # 测试MySQL连接
        from sqlalchemy import create_engine, text
        from config import settings
        
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ MySQL连接成功")
        
        # 测试Redis连接
        from redis_client import get_redis
        redis_client = get_redis()
        if redis_client.ping():
            print("✅ Redis连接成功")
        else:
            print("❌ Redis连接失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        print("请检查网络连接和服务器状态")
        return False

def init_database():
    """初始化数据库"""
    print("🗄️ 初始化数据库...")
    try:
        subprocess.run([sys.executable, "init_db.py"], check=True)
        print("✅ 数据库初始化成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

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
        subprocess.run([sys.executable, "dev_start.py"])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎯 图片转换服务 - 远程数据库版本")
    print("=" * 60)
    print("📊 服务器配置:")
    print("   MySQL: 1.94.137.69:3306")
    print("   Redis: 1.94.137.69:6379")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 测试连接
    if not test_connections():
        print("\n❌ 连接测试失败，请检查：")
        print("1. 网络连接是否正常")
        print("2. 服务器是否运行")
        print("3. 防火墙设置")
        print("4. 用户名密码是否正确")
        return
    
    # 初始化数据库
    if not init_database():
        return
    
    # 启动服务
    start_server()

if __name__ == "__main__":
    main()
