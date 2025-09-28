from pydantic_settings import BaseSettings
from typing import List
import os

class DevSettings(BaseSettings):
    # 数据库配置
    database_url: str = "mysql+pymysql://root:123456@1.94.137.69:3306/image_convert_db"
    
    # Redis配置
    redis_host: str = "1.94.137.69"
    redis_port: int = 6379
    redis_database: int = 0
    redis_password: str = "foobared"
    redis_url: str = "redis://:foobared@1.94.137.69:6379/0"
    
    # JWT配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 开发模式
    debug: bool = True
    
    # 支付宝配置
    alipay_app_id: str = ""
    alipay_private_key: str = ""
    alipay_public_key: str = ""
    alipay_gateway: str = "https://openapi.alipay.com/gateway.do"
    
    # 微信支付配置（商户支付）
    wechat_app_id: str = ""
    wechat_mch_id: str = ""
    wechat_api_key: str = ""
    wechat_cert_path: str = ""
    wechat_key_path: str = ""
    wechat_notify_url: str = "http://localhost:8000/api/payment/wechat/callback"
    
    # 微信开放平台配置（扫码登录）
    wechat_open_app_id: str = ""
    wechat_open_app_secret: str = ""
    wechat_open_redirect_uri: str = "http://localhost:8000/api/auth/wechat/callback"
    wechat_open_scope: str = "snsapi_login"
    
    # Auth0配置（开发环境）
    auth0_domain: str = "gaopfediter.us.auth0.com"
    auth0_client_id: str = "5xzUKrmwx7bFlUb9nf7l3C0Xp0q8AqcN"
    auth0_client_secret: str = "5VbXSpLULWdqS7n4dLZOQjvJmkw73otJ8KsMzTPgJPIpfCM8CxAVfU-36OQkEGET"
    auth0_redirect_uri: str = "https://subpredicative-jerrica-subtepidly.ngrok-free.dev/google-login/success"  # 本地开发
    auth0_scope: str = "openid email profile"
    auth0_audience: str = ""
    
    # Google OAuth配置（备用方案）
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    google_scope: str = "openid email profile"
    
    # 文件存储配置
    upload_dir: str = "uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]
    
    # 会员配置
    free_user_daily_limit: int = 5
    vip_user_daily_limit: int = 100
    svip_user_daily_limit: int = 1000
    
    # 会员价格配置
    vip_price: float = 29.9
    svip_price: float = 99.9
    
    class Config:
        env_file = ".env"

settings = DevSettings()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)
