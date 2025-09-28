"""
用户和认证相关Schema
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import UserRole

# 用户相关Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    wechat_nickname: Optional[str] = None
    wechat_avatar: Optional[str] = None
    is_wechat_user: bool = False
    # Google字段已移除，使用Auth0替代
    auth0_name: Optional[str] = None
    auth0_picture: Optional[str] = None
    is_auth0_user: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Token相关Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None
