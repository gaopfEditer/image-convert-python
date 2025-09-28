"""
通用响应Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import UserRole

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

# 通用响应Schema
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None
