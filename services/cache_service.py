from typing import Optional, Any, Union
from datetime import datetime, timedelta
from redis_client import get_redis
import json

class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        self.redis = get_redis()
        self.default_expire = 3600  # 默认过期时间1小时
    
    def cache_user_usage(self, user_id: int, usage_count: int, expire_seconds: int = 86400) -> bool:
        """缓存用户使用次数"""
        key = f"user_usage:{user_id}"
        data = {
            "user_id": user_id,
            "usage_count": usage_count,
            "cached_at": datetime.now().isoformat(),
            "expire_at": (datetime.now() + timedelta(seconds=expire_seconds)).isoformat()
        }
        return self.redis.set(key, data, ex=expire_seconds)
    
    def get_user_usage(self, user_id: int) -> Optional[dict]:
        """获取用户使用次数缓存"""
        key = f"user_usage:{user_id}"
        return self.redis.get(key)
    
    def increment_user_usage(self, user_id: int) -> Optional[int]:
        """增加用户使用次数"""
        key = f"user_usage_count:{user_id}"
        return self.redis.incr(key)
    
    def get_user_usage_count(self, user_id: int) -> int:
        """获取用户使用次数"""
        key = f"user_usage_count:{user_id}"
        count = self.redis.get(key)
        return int(count) if count else 0
    
    def reset_daily_usage(self, user_id: int) -> bool:
        """重置每日使用次数"""
        key = f"user_usage_count:{user_id}"
        return self.redis.delete(key)
    
    def cache_conversion_result(self, task_id: str, result: dict, expire_seconds: int = 3600) -> bool:
        """缓存转换结果"""
        key = f"conversion_result:{task_id}"
        data = {
            "task_id": task_id,
            "result": result,
            "cached_at": datetime.now().isoformat()
        }
        return self.redis.set(key, data, ex=expire_seconds)
    
    def get_conversion_result(self, task_id: str) -> Optional[dict]:
        """获取转换结果缓存"""
        key = f"conversion_result:{task_id}"
        return self.redis.get(key)
    
    def cache_user_session(self, user_id: int, session_data: dict, expire_seconds: int = 1800) -> bool:
        """缓存用户会话"""
        key = f"user_session:{user_id}"
        data = {
            "user_id": user_id,
            "session_data": session_data,
            "cached_at": datetime.now().isoformat()
        }
        return self.redis.set(key, data, ex=expire_seconds)
    
    def get_user_session(self, user_id: int) -> Optional[dict]:
        """获取用户会话缓存"""
        key = f"user_session:{user_id}"
        return self.redis.get(key)
    
    def invalidate_user_session(self, user_id: int) -> bool:
        """使用户会话失效"""
        key = f"user_session:{user_id}"
        return self.redis.delete(key)
    
    def cache_api_rate_limit(self, ip: str, endpoint: str, limit: int = 100, window: int = 3600) -> tuple[bool, int]:
        """API限流缓存"""
        key = f"rate_limit:{ip}:{endpoint}"
        
        # 获取当前计数
        current_count = self.redis.get(key)
        if current_count is None:
            # 第一次访问，设置计数和过期时间
            self.redis.set(key, 1, ex=window)
            return True, 1
        
        current_count = int(current_count)
        if current_count >= limit:
            return False, current_count
        
        # 增加计数
        new_count = self.redis.incr(key)
        return True, new_count
    
    def cache_payment_status(self, order_id: str, status: str, expire_seconds: int = 1800) -> bool:
        """缓存支付状态"""
        key = f"payment_status:{order_id}"
        data = {
            "order_id": order_id,
            "status": status,
            "cached_at": datetime.now().isoformat()
        }
        return self.redis.set(key, data, ex=expire_seconds)
    
    def get_payment_status(self, order_id: str) -> Optional[dict]:
        """获取支付状态缓存"""
        key = f"payment_status:{order_id}"
        return self.redis.get(key)
    
    def cache_image_info(self, file_hash: str, image_info: dict, expire_seconds: int = 3600) -> bool:
        """缓存图片信息"""
        key = f"image_info:{file_hash}"
        data = {
            "file_hash": file_hash,
            "image_info": image_info,
            "cached_at": datetime.now().isoformat()
        }
        return self.redis.set(key, data, ex=expire_seconds)
    
    def get_image_info(self, file_hash: str) -> Optional[dict]:
        """获取图片信息缓存"""
        key = f"image_info:{file_hash}"
        return self.redis.get(key)
    
    def add_to_queue(self, queue_name: str, task_data: dict) -> Optional[int]:
        """添加任务到队列"""
        return self.redis.lpush(queue_name, task_data)
    
    def get_from_queue(self, queue_name: str) -> Optional[dict]:
        """从队列获取任务"""
        return self.redis.rpop(queue_name)
    
    def get_queue_length(self, queue_name: str) -> int:
        """获取队列长度"""
        return self.redis.llen(queue_name)
    
    def cache_system_stats(self, stats: dict, expire_seconds: int = 300) -> bool:
        """缓存系统统计信息"""
        key = "system_stats"
        data = {
            "stats": stats,
            "cached_at": datetime.now().isoformat()
        }
        return self.redis.set(key, data, ex=expire_seconds)
    
    def get_system_stats(self) -> Optional[dict]:
        """获取系统统计信息缓存"""
        key = "system_stats"
        return self.redis.get(key)
    
    def clear_user_cache(self, user_id: int) -> bool:
        """清除用户相关缓存"""
        patterns = [
            f"user_usage:{user_id}",
            f"user_usage_count:{user_id}",
            f"user_session:{user_id}",
            f"conversion_result:*:{user_id}"
        ]
        
        success = True
        for pattern in patterns:
            if not self.redis.delete(pattern):
                success = False
        
        return success
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        try:
            info = self.redis.redis_client.info()
            return {
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """计算缓存命中率"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# 创建全局缓存服务实例
cache_service = CacheService()

def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    return cache_service
