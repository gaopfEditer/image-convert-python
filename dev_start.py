#!/usr/bin/env python3
"""
简化启动脚本 - 使用原有的路由结构
包含定时任务调度器，用于清理数据库记录
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from tools.database.database import engine, Base
from routers import payment
from routers.auth_simple import router as auth_router
from routers.image_optimized import router as image_router
from tools.scheduler import run_scheduler_in_background
from config import settings
import httpx

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

# 导入Auth0登录路由（推荐方案）
from routers import auth0_auth
app.include_router(auth0_auth.router, prefix="/api")

# Google登录已移除，使用Auth0替代


# 导入智能登录路由
from routers import smart_auth
app.include_router(smart_auth.router, prefix="/api")

async def detect_ip_location(ip_address: str) -> dict:
    """检测IP地址的地理位置"""
    if not ip_address or ip_address == "无法获取":
        return {
            "country": "未知",
            "country_code": "XX",
            "region": "未知",
            "city": "未知",
            "is_china": False,
            "login_method": "google"  # 默认使用Google登录
        }
    
    try:
        # 使用免费的IP地理位置API
        async with httpx.AsyncClient() as client:
            # 尝试使用ip-api.com (免费，无需API key)
            response = await client.get(
                f"http://ip-api.com/json/{ip_address}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否在中国
                is_china = data.get("countryCode") == "CN"
                
                return {
                    "country": data.get("country", "未知"),
                    "country_code": data.get("countryCode", "XX"),
                    "region": data.get("regionName", "未知"),
                    "city": data.get("city", "未知"),
                    "is_china": is_china,
                    "login_method": "wechat" if is_china else "google",
                    "timezone": data.get("timezone", ""),
                    "isp": data.get("isp", "")
                }
            else:
                # 如果API失败，使用备用方法
                return await detect_ip_location_fallback(ip_address)
                
    except Exception as e:
        print(f"IP地理位置检测失败: {e}")
        return await detect_ip_location_fallback(ip_address)

async def detect_ip_location_fallback(ip_address: str) -> dict:
    """备用IP地理位置检测方法"""
    try:
        # 使用ipinfo.io作为备用
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://ipinfo.io/{ip_address}/json",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                country_code = data.get("country", "XX")
                is_china = country_code == "CN"
                
                return {
                    "country": data.get("country", "未知"),
                    "country_code": country_code,
                    "region": data.get("region", "未知"),
                    "city": data.get("city", "未知"),
                    "is_china": is_china,
                    "login_method": "wechat" if is_china else "google",
                    "timezone": data.get("timezone", ""),
                    "org": data.get("org", "")
                }
    except Exception as e:
        print(f"备用IP检测也失败: {e}")
    
    # 如果所有方法都失败，返回默认值
    return {
        "country": "未知",
        "country_code": "XX",
        "region": "未知",
        "city": "未知",
        "is_china": False,
        "login_method": "google"
    }

@app.get("/", summary="API根路径")
async def root():
    """API根路径"""
    return {
        "message": "图片转换服务API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/login", response_class=HTMLResponse, summary="登录页面")
async def login_page():
    """登录页面"""
    try:
        with open("templates/login.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>登录页面未找到</h1>", status_code=404)

@app.get("/login/success", response_class=HTMLResponse, summary="登录成功页面")
async def login_success_page(
    token: str = None,
    user_id: int = None,
    username: str = None,
    email: str = None,
    login_method: str = None
):
    """登录成功页面"""
    try:
        with open("templates/login_success.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>登录成功页面未找到</h1>", status_code=404)

@app.get("/demo", response_class=HTMLResponse, summary="认证演示页面")
async def demo_page():
    """认证演示页面"""
    try:
        with open("templates/demo.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>演示页面未找到</h1>", status_code=404)

@app.get("/google-login/success", response_class=HTMLResponse, summary="Google登录成功页面")
async def google_login_success():
    """Google登录成功页面"""
    try:
        with open("templates/google_login_success.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Google登录成功页面未找到</h1>", status_code=404)

@app.get("/google-login", response_class=HTMLResponse, summary="Google登录页面")
async def google_login_page():
    """Google登录页面"""
    try:
        with open("templates/google_login.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Google登录页面未找到</h1>", status_code=404)

@app.get("/health", summary="健康检查")
async def health_check(
    client_ip: str = None,
    host_id: str = None
):
    """健康检查接口 - 支持IP地址和主机ID检测"""
    import socket
    import platform
    from datetime import datetime
    
    try:
        # 获取本机IP地址
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # 获取外网IP（如果可能）
        try:
            import requests
            external_ip = requests.get('https://api.ipify.org', timeout=3).text
        except:
            external_ip = "无法获取"
            
    except Exception as e:
        local_ip = "无法获取"
        external_ip = "无法获取"
    
    # 检测IP地理位置
    location_info = await detect_ip_location(client_ip or external_ip)
    
    return {
        "status": "healthy", 
        "message": "服务运行正常",
        "client_info": {
            "client_ip": client_ip,
            "host_id": host_id,
            "location": location_info
        },
        "server_info": {
            "hostname": hostname,
            "local_ip": local_ip,
            "external_ip": external_ip,
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "timestamp": datetime.now().isoformat()
        }
    }

# 全局异常处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"message": "接口不存在", "success": False}

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    """处理422验证错误"""
    print(f"422错误详情: {exc}")
    if hasattr(exc, 'errors'):
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        return {
            "message": "请求参数验证失败",
            "success": False,
            "errors": error_details
        }
    return {"message": "请求参数验证失败", "success": False, "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"message": "服务器内部错误", "success": False}

if __name__ == "__main__":
    import uvicorn
    
    # 启动定时任务调度器
    scheduler_thread = run_scheduler_in_background()
    
    print("🚀 启动图片转换服务（简化版 + 定时任务）...")
    print("📅 定时任务：每天凌晨清理匿名记录，每周清理旧记录")
    print("📱 登录页面: http://localhost:8000/login")
    print("🔐 Google登录: http://localhost:8000/google-login")
    print("🧪 演示页面: http://localhost:8000/demo")
    print("📚 API文档: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_start:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
