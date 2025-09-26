from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
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
    debug: bool = False
    
    # 支付宝配置
    alipay_app_id: str = ""
    alipay_private_key: str = ""
    alipay_public_key: str = ""
    alipay_gateway: str = "https://openapi.alipay.com/gateway.do"
    
    # 微信支付配置（商户支付）
    wechat_app_id: str = ""  # 微信开放平台应用ID
    wechat_mch_id: str = ""  # 微信商户号
    wechat_api_key: str = ""  # 商户API密钥
    wechat_cert_path: str = ""  # 商户证书路径
    wechat_key_path: str = ""  # 商户私钥路径
    wechat_notify_url: str = "http://your-domain.com/api/payment/wechat/callback"  # 支付回调地址
    
    # 微信开放平台配置（扫码登录）
    wechat_open_app_id: str = ""
    wechat_open_app_secret: str = ""
    wechat_open_redirect_uri: str = "http://localhost:8000/api/auth/wechat/callback"
    wechat_open_scope: str = "snsapi_login"
    
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

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)
