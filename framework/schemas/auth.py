"""
认证相关Schema（微信、Auth0等）
"""
from pydantic import BaseModel
from typing import Optional
from .user import UserResponse

# 微信登录相关Schema
class WeChatLoginRequest(BaseModel):
    state: Optional[str] = None

class WeChatLoginResponse(BaseModel):
    auth_url: str
    state: str
    qr_code: str  # 二维码内容

class WeChatCallbackRequest(BaseModel):
    code: str
    state: str

class WeChatLoginStatusResponse(BaseModel):
    status: str  # pending, success, failed
    message: str
    user: Optional[UserResponse] = None

# Auth0登录相关Schema
class Auth0LoginRequest(BaseModel):
    state: Optional[str] = None

class Auth0LoginResponse(BaseModel):
    auth_url: str = ""
    state: str = ""
    access_token: str = ""
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
    message: str = ""

class Auth0CallbackRequest(BaseModel):
    code: str
    state: str

class Auth0LoginStatusResponse(BaseModel):
    status: str  # pending, success, failed
    message: str
    user: Optional[UserResponse] = None

# 智能登录相关Schema
class SmartLoginResponse(BaseModel):
    recommended_method: str  # wechat, auth0
    location_info: dict
    wechat_login_url: Optional[str] = None
    auth0_login_url: Optional[str] = None
    # google_login_url已移除，使用auth0_login_url替代
    message: str
