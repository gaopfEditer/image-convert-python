"""
认证中间件 - 自动处理需要验证的接口
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证中间件 - 自动为需要验证的接口添加认证检查
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # 定义不需要验证的路径
        self.public_paths = {
            "/api/auth/login",
            "/api/auth/register", 
            "/api/image/convert",  # 图片转换接口
            "/api/image/compress", # 图片压缩接口
            "/api/image/resize",   # 图片调整大小接口
            "/api/image/watermark", # 图片水印接口
            "/api/image/formats",  # 获取支持的格式
            "/api/image/info",     # 获取图片信息
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        }
        logger.info(f"🔧 认证中间件初始化完成，公开路径: {self.public_paths}")
        
        # 定义不需要验证的路径前缀
        self.public_prefixes = [
            "/static/",
            "/uploads/",
            "/docs/",
            "/redoc/"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        处理请求，检查是否需要认证
        """
        # 获取请求路径
        path = request.url.path
        print(f"🔍 中间件处理请求: {path}")  # 使用print确保输出
        
        # 检查是否为公开路径
        if self._is_public_path(path):
            print(f"✅ 公开路径，跳过认证: {path}")
            return await call_next(request)
        
        # 检查是否为公开路径前缀
        if self._is_public_prefix(path):
            print(f"✅ 公开路径前缀，跳过认证: {path}")
            return await call_next(request)
        
        # 需要认证的路径 - 暂时先通过，让路由自己处理
        print(f"🔒 需要认证的路径: {path}")
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """检查是否为公开路径"""
        return path in self.public_paths
    
    def _is_public_prefix(self, path: str) -> bool:
        """检查是否为公开路径前缀"""
        return any(path.startswith(prefix) for prefix in self.public_prefixes)
