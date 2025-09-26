import redis
from config import settings
from typing import Optional, Any
import json
import pickle

class RedisClient:
    """Redis客户端封装类"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_database,
            password=settings.redis_password,
            decode_responses=True,  # 自动解码响应
            socket_connect_timeout=5,  # 连接超时
            socket_timeout=5,  # 操作超时
            retry_on_timeout=True,  # 超时重试
            health_check_interval=30  # 健康检查间隔
        )
    
    def ping(self) -> bool:
        """检查Redis连接状态"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置键值对"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return self.redis_client.set(key, value, ex=ex)
        except Exception as e:
            print(f"Redis SET 错误: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取值"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Redis GET 错误: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除键"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis DELETE 错误: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Redis EXISTS 错误: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        try:
            return self.redis_client.expire(key, seconds)
        except Exception as e:
            print(f"Redis EXPIRE 错误: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"Redis TTL 错误: {e}")
            return -1
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """递增计数器"""
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Redis INCR 错误: {e}")
            return None
    
    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """递减计数器"""
        try:
            return self.redis_client.decrby(key, amount)
        except Exception as e:
            print(f"Redis DECR 错误: {e}")
            return None
    
    def hset(self, name: str, key: str, value: Any) -> bool:
        """设置哈希字段"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return bool(self.redis_client.hset(name, key, value))
        except Exception as e:
            print(f"Redis HSET 错误: {e}")
            return False
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        """获取哈希字段值"""
        try:
            value = self.redis_client.hget(name, key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Redis HGET 错误: {e}")
            return None
    
    def hgetall(self, name: str) -> dict:
        """获取所有哈希字段"""
        try:
            data = self.redis_client.hgetall(name)
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        except Exception as e:
            print(f"Redis HGETALL 错误: {e}")
            return {}
    
    def hdel(self, name: str, key: str) -> bool:
        """删除哈希字段"""
        try:
            return bool(self.redis_client.hdel(name, key))
        except Exception as e:
            print(f"Redis HDEL 错误: {e}")
            return False
    
    def lpush(self, name: str, *values) -> Optional[int]:
        """从左侧推入列表"""
        try:
            processed_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    processed_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    processed_values.append(value)
            return self.redis_client.lpush(name, *processed_values)
        except Exception as e:
            print(f"Redis LPUSH 错误: {e}")
            return None
    
    def rpop(self, name: str) -> Optional[Any]:
        """从右侧弹出列表元素"""
        try:
            value = self.redis_client.rpop(name)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Redis RPOP 错误: {e}")
            return None
    
    def llen(self, name: str) -> int:
        """获取列表长度"""
        try:
            return self.redis_client.llen(name)
        except Exception as e:
            print(f"Redis LLEN 错误: {e}")
            return 0
    
    def sadd(self, name: str, *values) -> Optional[int]:
        """添加集合成员"""
        try:
            return self.redis_client.sadd(name, *values)
        except Exception as e:
            print(f"Redis SADD 错误: {e}")
            return None
    
    def smembers(self, name: str) -> set:
        """获取集合所有成员"""
        try:
            return self.redis_client.smembers(name)
        except Exception as e:
            print(f"Redis SMEMBERS 错误: {e}")
            return set()
    
    def srem(self, name: str, *values) -> Optional[int]:
        """删除集合成员"""
        try:
            return self.redis_client.srem(name, *values)
        except Exception as e:
            print(f"Redis SREM 错误: {e}")
            return None
    
    def flushdb(self) -> bool:
        """清空当前数据库"""
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            print(f"Redis FLUSHDB 错误: {e}")
            return False

# 创建全局Redis客户端实例
redis_client = RedisClient()

def get_redis() -> RedisClient:
    """获取Redis客户端实例"""
    return redis_client
