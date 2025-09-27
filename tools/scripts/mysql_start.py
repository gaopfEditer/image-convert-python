#!/usr/bin/env python3
"""
MySQL数据库快速启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def check_mysql():
    """检查MySQL服务状态"""
    print("🔍 检查MySQL服务...")
    try:
        # 尝试连接MySQL
        result = subprocess.run([
            "mysql", "-u", "root", "-p", "-e", "SELECT 1"
        ], capture_output=True, text=True, input="\n")
        
        if result.returncode == 0:
            print("✅ MySQL服务正常")
            return True
        else:
            print("❌ MySQL连接失败")
            return False
    except FileNotFoundError:
        print("❌ MySQL未安装或未添加到PATH")
        print("请先安装MySQL：https://dev.mysql.com/downloads/mysql/")
        return False
    except Exception as e:
        print(f"❌ MySQL检查失败: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
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
        subprocess.run([
            sys.executable, "dev_start.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🎯 图片转换服务 - MySQL版本")
    print("=" * 60)
    
    # 检查MySQL
    if not check_mysql():
        print("\n请先启动MySQL服务：")
        print("Windows: 服务管理器 -> MySQL -> 启动")
        print("macOS: brew services start mysql")
        print("Linux: sudo systemctl start mysql")
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 初始化数据库
    if not init_database():
        return
    
    # 启动服务
    start_server()

if __name__ == "__main__":
    main()
