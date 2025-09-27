"""
认证装饰器 - 用于标记不需要验证的接口
"""
from functools import wraps
from typing import Callable, Any

def public_endpoint(func: Callable) -> Callable:
    """
    标记接口为公开接口，不需要认证
    
    使用方法:
    @public_endpoint
    @router.post("/login")
    async def login():
        pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # 在函数对象上添加标记，表示这是公开接口
        func._is_public = True
        return await func(*args, **kwargs)
    
    # 确保装饰器属性被正确设置
    wrapper._is_public = True
    return wrapper

def check_is_public(func: Callable) -> bool:
    """
    检查函数是否为公开接口
    """
    return getattr(func, '_is_public', False)
