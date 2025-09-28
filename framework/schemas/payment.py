"""
支付相关Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import UserRole, PaymentStatus, PaymentMethod

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
