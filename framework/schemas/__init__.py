"""
Schema模块统一入口
"""
# 用户和认证相关
from .user import (
    UserBase, UserCreate, UserLogin, UserResponse, UserUpdate,
    Token, LoginResponse, TokenData
)

# 图片处理相关
from .image import (
    ImageInfo, ImageConversionResponse, ImageConvertRequest,
    ConversionRecordBase, ConversionRecordCreate, ConversionRecordResponse
)

# 认证相关（微信、Auth0等）
from .auth import (
    WeChatLoginRequest, WeChatLoginResponse, WeChatCallbackRequest, WeChatLoginStatusResponse,
    Auth0LoginRequest, Auth0LoginResponse, Auth0CallbackRequest, Auth0LoginStatusResponse,
    SmartLoginResponse
)

# 支付相关
from .payment import (
    PaymentCreate, PaymentResponse, PaymentCallback
)

# 通用响应
from .common import (
    DailyUsageResponse, UsageStatsResponse, MessageResponse, ErrorResponse
)

# 反馈和积分相关（已存在）
from .feedback import *
from .points import *

__all__ = [
    # 用户相关
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "UserUpdate",
    "Token", "LoginResponse", "TokenData",
    
    # 图片处理相关
    "ImageInfo", "ImageConversionResponse", "ImageConvertRequest",
    "ConversionRecordBase", "ConversionRecordCreate", "ConversionRecordResponse",
    
    # 认证相关
    "WeChatLoginRequest", "WeChatLoginResponse", "WeChatCallbackRequest", "WeChatLoginStatusResponse",
    "Auth0LoginRequest", "Auth0LoginResponse", "Auth0CallbackRequest", "Auth0LoginStatusResponse",
    "SmartLoginResponse",
    
    # 支付相关
    "PaymentCreate", "PaymentResponse", "PaymentCallback",
    
    # 通用响应
    "DailyUsageResponse", "UsageStatsResponse", "MessageResponse", "ErrorResponse",
]
