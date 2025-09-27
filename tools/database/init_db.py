#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from tools.database.database import Base
from config import settings

def init_database():
    """初始化数据库"""
    print("🗄️ 初始化数据库...")
    
    try:
        # 创建数据库引擎
        engine = create_engine(settings.database_url)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("✅ 数据库表创建成功")
        
        # 插入测试数据
        with engine.connect() as conn:
            # 检查是否已有数据
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            
            if count == 0:
                print("📝 插入测试数据...")
                
                # 插入测试用户
                conn.execute(text("""
                    INSERT INTO users (username, email, hashed_password, role) VALUES 
                    ('admin', 'admin@example.com', '$2b$12$gindbyUFbD4QixtPA7ywOu3mmjGPqJ4YRCtklyRtft4CODAN9wpK2', 'SVIP'),
                    ('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2', 'FREE')
                """))
                
                conn.commit()
                print("✅ 测试数据插入成功")
            else:
                print("ℹ️ 数据库已有数据，跳过测试数据插入")
        
        print("🎉 数据库初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("请检查MySQL服务是否启动，以及连接参数是否正确")
        return False

def main():
    """主函数"""
    print("🚀 图片转换服务 - 数据库初始化")
    print("=" * 50)
    
    # 检查数据库连接
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置和连接")
        return
    
    # 初始化数据库
    if init_database():
        print("\n🎯 下一步:")
        print("1. 运行: python dev_start.py")
        print("2. 访问: http://localhost:8000/docs")
        print("3. 测试API接口")
    else:
        print("\n❌ 初始化失败，请检查错误信息")

if __name__ == "__main__":
    main()
