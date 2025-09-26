from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole, PaymentStatus, PaymentMethod

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
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# 转换记录Schema
class ConversionRecordBase(BaseModel):
    original_filename: str
    original_format: str
    target_format: str
    file_size: int
    conversion_time: float
    status: str = "success"
    error_message: Optional[str] = None

class ConversionRecordCreate(ConversionRecordBase):
    pass

class ConversionRecordResponse(ConversionRecordBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 支付相关Schema
class PaymentCreate(BaseModel):
    target_role: UserRole
    payment_method: PaymentMethod

class PaymentResponse(BaseModel):
    id: int
    order_id: str
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus
    target_role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentCallback(BaseModel):
    order_id: str
    transaction_id: str
    status: str
    amount: float

# 使用统计Schema
class DailyUsageResponse(BaseModel):
    id: int
    user_id: int
    usage_date: datetime
    usage_count: int
    
    class Config:
        from_attributes = True

class UsageStatsResponse(BaseModel):
    today_usage: int
    daily_limit: int
    remaining_usage: int
    role: UserRole

# 图片转换请求Schema
class ImageConvertRequest(BaseModel):
    target_format: str
    quality: Optional[int] = 95  # 图片质量 1-100
    resize: Optional[dict] = None  # {"width": 800, "height": 600}
    watermark: Optional[bool] = False

# Token相关Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 通用响应Schema
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None

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
