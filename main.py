from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from database import engine, Base
from routers import auth, image, payment
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
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory=settings.upload_dir), name="static")

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(image.router, prefix="/api")
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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
