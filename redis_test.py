#!/usr/bin/env python3
"""
Redis连接测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from redis_client import get_redis
from config import settings

def test_redis_connection():
    """测试Redis连接"""
    print("🔍 测试Redis连接...")
    print(f"Redis配置: {settings.redis_host}:{settings.redis_port}")
    print(f"数据库: {settings.redis_database}")
    print(f"密码: {'*' * len(settings.redis_password) if settings.redis_password else '无'}")
    print("-" * 50)
    
    redis_client = get_redis()
    
    # 测试连接
    if redis_client.ping():
        print("✅ Redis连接成功")
    else:
        print("❌ Redis连接失败")
        return False
    
    # 测试基本操作
    print("\n🧪 测试基本操作...")
    
    # 测试字符串操作
    test_key = "test:connection"
    test_value = {"message": "Hello Redis!", "timestamp": "2024-01-01"}
    
    if redis_client.set(test_key, test_value, ex=60):
        print("✅ SET操作成功")
    else:
        print("❌ SET操作失败")
        return False
    
    retrieved_value = redis_client.get(test_key)
    if retrieved_value == test_value:
        print("✅ GET操作成功")
    else:
        print("❌ GET操作失败")
        return False
    
    # 测试计数器
    counter_key = "test:counter"
    redis_client.set(counter_key, 0)
    
    for i in range(5):
        redis_client.incr(counter_key)
    
    counter_value = redis_client.get(counter_key)
    if counter_value == 5:
        print("✅ 计数器操作成功")
    else:
        print("❌ 计数器操作失败")
        return False
    
    # 测试哈希操作
    hash_key = "test:user"
    user_data = {
        "id": 1,
        "name": "测试用户",
        "email": "test@example.com",
        "role": "admin"
    }
    
    for field, value in user_data.items():
        redis_client.hset(hash_key, field, value)
    
    retrieved_user = redis_client.hgetall(hash_key)
    if retrieved_user == user_data:
        print("✅ 哈希操作成功")
    else:
        print("❌ 哈希操作失败")
        return False
    
    # 测试列表操作
    list_key = "test:queue"
    items = ["任务1", "任务2", "任务3"]
    
    for item in items:
        redis_client.lpush(list_key, item)
    
    list_length = redis_client.llen(list_key)
    if list_length == len(items):
        print("✅ 列表操作成功")
    else:
        print("❌ 列表操作失败")
        return False
    
    # 测试集合操作
    set_key = "test:tags"
    tags = ["python", "redis", "fastapi", "mysql"]
    
    redis_client.sadd(set_key, *tags)
    retrieved_tags = redis_client.smembers(set_key)
    if set(retrieved_tags) == set(tags):
        print("✅ 集合操作成功")
    else:
        print("❌ 集合操作失败")
        return False
    
    # 清理测试数据
    redis_client.delete(test_key)
    redis_client.delete(counter_key)
    redis_client.delete(hash_key)
    redis_client.delete(list_key)
    redis_client.delete(set_key)
    
    print("\n🎉 所有Redis操作测试通过！")
    return True

def show_redis_info():
    """显示Redis信息"""
    print("\n📊 Redis服务器信息:")
    print("-" * 50)
    
    redis_client = get_redis()
    
    try:
        info = redis_client.redis_client.info()
        print(f"Redis版本: {info.get('redis_version', '未知')}")
        print(f"运行时间: {info.get('uptime_in_seconds', 0)} 秒")
        print(f"已用内存: {info.get('used_memory_human', '未知')}")
        print(f"连接数: {info.get('connected_clients', 0)}")
        print(f"数据库大小: {info.get('db0', {}).get('keys', 0)} 个键")
    except Exception as e:
        print(f"获取Redis信息失败: {e}")

def main():
    """主函数"""
    print("🎯 Redis连接测试工具")
    print("=" * 60)
    
    # 测试连接
    if test_redis_connection():
        show_redis_info()
        print("\n✅ Redis配置正确，可以正常使用！")
    else:
        print("\n❌ Redis配置有问题，请检查：")
        print("1. Redis服务是否启动")
        print("2. 网络连接是否正常")
        print("3. 配置参数是否正确")
        print("4. 防火墙设置")

if __name__ == "__main__":
    main()
