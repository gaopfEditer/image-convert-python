#!/usr/bin/env python3
"""
简化启动脚本 - 使用原有的路由结构
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from tools.database.database import engine, Base
from routers import payment
from routers.auth_simple import router as auth_router
from routers.image_optimized import router as image_router
from config import settings

# 创建数据库表
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 确保必要的目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "converted"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "temp"), exist_ok=True)
    
    yield
    
    # 关闭时的清理工作
    pass

# 创建FastAPI应用
app = FastAPI(
    title="图片转换服务API",
    description="支持多种格式的图片转换服务，包含会员系统和支付功能",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React开发服务器
        "http://localhost:8080",  # Vue开发服务器
        "http://localhost:5173",  # Vite开发服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080", 
        "http://127.0.0.1:5173",
        "http://localhost:8000",  # 同域
        "http://127.0.0.1:8000",
        "*"  # 开发环境允许所有来源
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=3600,  # 预检请求缓存时间
)

# 静态文件服务
app.mount("/static", StaticFiles(directory=settings.upload_dir), name="static")

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(image_router, prefix="/api")
app.include_router(payment.router, prefix="/api")

# 导入微信登录路由
from routers import wechat_auth
app.include_router(wechat_auth.router, prefix="/api")

@app.get("/", summary="API根路径")
async def root():
    """API根路径"""
    return {
        "message": "图片转换服务API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "服务运行正常"}

# 全局异常处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"message": "接口不存在", "success": False}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"message": "服务器内部错误", "success": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_start:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
