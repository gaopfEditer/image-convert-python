from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from tools.database.database import Base
import enum

class UserRole(str, enum.Enum):
    FREE = "free"
    VIP = "vip"
    SVIP = "svip"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(str, enum.Enum):
    ALIPAY = "alipay"
    WECHAT = "wechat"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # 微信用户可能没有密码
    role = Column(Enum(UserRole), default=UserRole.FREE, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 微信登录相关字段
    wechat_openid = Column(String(100), unique=True, index=True, nullable=True)
    wechat_unionid = Column(String(100), nullable=True)
    wechat_nickname = Column(String(100), nullable=True)
    wechat_avatar = Column(String(500), nullable=True)
    is_wechat_user = Column(Boolean, default=False)
    
    # Google登录相关字段已移除，使用Auth0替代
    
    
    # Auth0登录相关字段
    auth0_id = Column(String(100), unique=True, index=True, nullable=True)
    auth0_name = Column(String(100), nullable=True)
    auth0_picture = Column(String(500), nullable=True)
    is_auth0_user = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    conversion_records = relationship("ConversionRecord", back_populates="user")
    payment_records = relationship("PaymentRecord", back_populates="user")
    daily_usage = relationship("DailyUsage", back_populates="user")

class ConversionRecord(Base):
    __tablename__ = "conversion_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 允许为空，支持公开接口
    original_filename = Column(String(255), nullable=False)
    original_format = Column(String(10), nullable=False)
    target_format = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    conversion_time = Column(Float, nullable=False)  # 转换耗时（秒）
    status = Column(String(20), default="success")  # success, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="conversion_records")

class PaymentRecord(Base):
    __tablename__ = "payment_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(String(100), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String(100), nullable=True)  # 第三方支付平台交易ID
    target_role = Column(Enum(UserRole), nullable=False)  # 购买的目标会员等级
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="payment_records")

class DailyUsage(Base):
    __tablename__ = "daily_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    usage_date = Column(DateTime(timezone=True), nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="daily_usage")
