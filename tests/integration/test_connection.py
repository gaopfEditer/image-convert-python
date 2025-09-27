#!/usr/bin/env python3
"""
数据库和Redis连接测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from tools.cache.redis_client import get_redis
from config import settings

def test_mysql_connection():
    """测试MySQL连接"""
    print("🔍 测试MySQL连接...")
    print(f"MySQL地址: {settings.database_url}")
    print("-" * 50)
    
    try:
        # 创建数据库引擎
        engine = create_engine(settings.database_url)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"✅ MySQL连接成功")
            print(f"MySQL版本: {version}")
            
            # 检查数据库是否存在
            result = conn.execute(text("SHOW DATABASES LIKE 'image_convert_db'"))
            db_exists = result.fetchone()
            
            if db_exists:
                print("✅ 数据库 'image_convert_db' 存在")
                
                # 检查表是否存在
                conn.execute(text("USE image_convert_db"))
                result = conn.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                
                if tables:
                    print(f"✅ 数据库表: {', '.join(tables)}")
                else:
                    print("⚠️ 数据库为空，需要初始化")
            else:
                print("⚠️ 数据库 'image_convert_db' 不存在，需要创建")
            
            return True
            
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("\n请检查：")
        print("1. MySQL服务是否运行")
        print("2. 网络连接是否正常")
        print("3. 用户名密码是否正确")
        print("4. 防火墙设置")
        return False

def test_redis_connection():
    """测试Redis连接"""
    print("\n🔍 测试Redis连接...")
    print(f"Redis地址: {settings.redis_host}:{settings.redis_port}")
    print(f"数据库: {settings.redis_database}")
    print("-" * 50)
    
    try:
        redis_client = get_redis()
        
        # 测试连接
        if redis_client.ping():
            print("✅ Redis连接成功")
            
            # 获取Redis信息
            info = redis_client.redis_client.info()
            print(f"Redis版本: {info.get('redis_version', '未知')}")
            print(f"已用内存: {info.get('used_memory_human', '未知')}")
            print(f"连接数: {info.get('connected_clients', 0)}")
            
            return True
        else:
            print("❌ Redis连接失败")
            return False
            
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("\n请检查：")
        print("1. Redis服务是否运行")
        print("2. 网络连接是否正常")
        print("3. 密码是否正确")
        print("4. 防火墙设置")
        return False

def test_database_operations():
    """测试数据库操作"""
    print("\n🧪 测试数据库操作...")
    print("-" * 50)
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # 切换到目标数据库
            conn.execute(text("USE image_convert_db"))
            
            # 测试创建表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ 创建表成功")
            
            # 测试插入数据
            conn.execute(text("""
                INSERT INTO test_table (name) VALUES ('测试数据')
            """))
            print("✅ 插入数据成功")
            
            # 测试查询数据
            result = conn.execute(text("SELECT * FROM test_table WHERE name = '测试数据'"))
            row = result.fetchone()
            if row:
                print("✅ 查询数据成功")
                print(f"查询结果: ID={row[0]}, Name={row[1]}")
            
            # 测试更新数据
            conn.execute(text("""
                UPDATE test_table SET name = '更新后的数据' WHERE name = '测试数据'
            """))
            print("✅ 更新数据成功")
            
            # 测试删除数据
            conn.execute(text("""
                DELETE FROM test_table WHERE name = '更新后的数据'
            """))
            print("✅ 删除数据成功")
            
            # 删除测试表
            conn.execute(text("DROP TABLE test_table"))
            print("✅ 删除测试表成功")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return False

def test_redis_operations():
    """测试Redis操作"""
    print("\n🧪 测试Redis操作...")
    print("-" * 50)
    
    try:
        redis_client = get_redis()
        
        # 测试字符串操作
        test_key = "test:connection"
        test_value = {"message": "Hello Redis!", "timestamp": "2024-01-01"}
        
        if redis_client.set(test_key, test_value, ex=60):
            print("✅ Redis SET操作成功")
        else:
            print("❌ Redis SET操作失败")
            return False
        
        retrieved_value = redis_client.get(test_key)
        if retrieved_value == test_value:
            print("✅ Redis GET操作成功")
        else:
            print("❌ Redis GET操作失败")
            return False
        
        # 测试计数器
        counter_key = "test:counter"
        redis_client.set(counter_key, 0)
        
        for i in range(3):
            redis_client.incr(counter_key)
        
        counter_value = redis_client.get(counter_key)
        if counter_value == 3:
            print("✅ Redis计数器操作成功")
        else:
            print("❌ Redis计数器操作失败")
            return False
        
        # 清理测试数据
        redis_client.delete(test_key)
        redis_client.delete(counter_key)
        print("✅ Redis清理测试数据成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis操作失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 数据库和Redis连接测试")
    print("=" * 60)
    
    # 测试MySQL连接
    mysql_ok = test_mysql_connection()
    
    # 测试Redis连接
    redis_ok = test_redis_connection()
    
    if mysql_ok and redis_ok:
        print("\n🎉 所有连接测试通过！")
        
        # 测试数据库操作
        if test_database_operations():
            print("✅ 数据库操作正常")
        else:
            print("❌ 数据库操作异常")
        
        # 测试Redis操作
        if test_redis_operations():
            print("✅ Redis操作正常")
        else:
            print("❌ Redis操作异常")
        
        print("\n🚀 可以启动服务了！")
        print("运行命令: python dev_start.py")
        
    else:
        print("\n❌ 连接测试失败，请检查配置")
        
        if not mysql_ok:
            print("MySQL连接失败")
        if not redis_ok:
            print("Redis连接失败")

if __name__ == "__main__":
    main()
