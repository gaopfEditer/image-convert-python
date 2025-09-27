"""
积分系统实体
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class PointType(str, Enum):
    EARN = "earn"
    SPEND = "spend"
    EXPIRE = "expire"
    ADMIN_ADJUST = "admin_adjust"

class PointSource(str, Enum):
    CHECKIN = "checkin"
    CONVERSION = "conversion"
    FEEDBACK = "feedback"
    ADMIN = "admin"
    EXCHANGE = "exchange"
    OTHER = "other"

class ExchangeItemType(str, Enum):
    VIP_UPGRADE = "vip_upgrade"
    CONVERSION_QUOTA = "conversion_quota"
    FEATURE_UNLOCK = "feature_unlock"
    OTHER = "other"

class ExchangeStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PointRecord:
    """积分记录实体"""
    
    id: Optional[int] = None
    user_id: int = 0
    points: int = 0
    type: PointType = PointType.EARN
    source: PointSource = PointSource.OTHER
    description: str = ""
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def is_earned(self) -> bool:
        """是否为获得积分"""
        return self.type == PointType.EARN
    
    def is_spent(self) -> bool:
        """是否为消费积分"""
        return self.type == PointType.SPEND
    
    def is_expired(self) -> bool:
        """是否为过期积分"""
        return self.type == PointType.EXPIRE
    
    def is_admin_adjust(self) -> bool:
        """是否为管理员调整"""
        return self.type == PointType.ADMIN_ADJUST
    
    def get_absolute_points(self) -> int:
        """获取绝对积分值"""
        return abs(self.points)
    
    def is_expired_now(self) -> bool:
        """是否已过期"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "points": self.points,
            "absolute_points": self.get_absolute_points(),
            "type": self.type.value,
            "source": self.source.value,
            "description": self.description,
            "related_id": self.related_id,
            "related_type": self.related_type,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_earned": self.is_earned(),
            "is_spent": self.is_spent(),
            "is_expired": self.is_expired(),
            "is_admin_adjust": self.is_admin_adjust(),
            "is_expired_now": self.is_expired_now()
        }

@dataclass
class CheckinRecord:
    """签到记录实体"""
    
    id: Optional[int] = None
    user_id: int = 0
    checkin_date: date = None
    points_earned: int = 0
    consecutive_days: int = 0
    created_at: Optional[datetime] = None
    
    def is_today(self) -> bool:
        """是否为今天签到"""
        return self.checkin_date == date.today()
    
    def is_consecutive(self) -> bool:
        """是否为连续签到"""
        return self.consecutive_days > 1
    
    def get_consecutive_bonus(self) -> int:
        """获取连续签到奖励积分"""
        if self.consecutive_days >= 30:
            return 500
        elif self.consecutive_days >= 7:
            return 150
        elif self.consecutive_days >= 3:
            return 50
        else:
            return 10
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "checkin_date": self.checkin_date.isoformat() if self.checkin_date else None,
            "points_earned": self.points_earned,
            "consecutive_days": self.consecutive_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_today": self.is_today(),
            "is_consecutive": self.is_consecutive(),
            "consecutive_bonus": self.get_consecutive_bonus()
        }

@dataclass
class PointExchange:
    """积分兑换实体"""
    
    id: Optional[int] = None
    user_id: int = 0
    item_name: str = ""
    item_type: ExchangeItemType = ExchangeItemType.OTHER
    points_cost: int = 0
    item_value: Optional[str] = None
    status: ExchangeStatus = ExchangeStatus.PENDING
    admin_approve_user_id: Optional[int] = None
    admin_approve_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def is_pending(self) -> bool:
        """是否为待处理"""
        return self.status == ExchangeStatus.PENDING
    
    def is_completed(self) -> bool:
        """是否为已完成"""
        return self.status == ExchangeStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """是否为失败"""
        return self.status == ExchangeStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """是否为已取消"""
        return self.status == ExchangeStatus.CANCELLED
    
    def can_cancel(self) -> bool:
        """是否可以取消"""
        return self.status == ExchangeStatus.PENDING
    
    def get_status_display(self) -> str:
        """获取状态显示名称"""
        status_names = {
            ExchangeStatus.PENDING: "待处理",
            ExchangeStatus.COMPLETED: "已完成",
            ExchangeStatus.FAILED: "失败",
            ExchangeStatus.CANCELLED: "已取消"
        }
        return status_names.get(self.status, "待处理")
    
    def get_item_type_display(self) -> str:
        """获取物品类型显示名称"""
        type_names = {
            ExchangeItemType.VIP_UPGRADE: "VIP升级",
            ExchangeItemType.CONVERSION_QUOTA: "转换额度",
            ExchangeItemType.FEATURE_UNLOCK: "功能解锁",
            ExchangeItemType.OTHER: "其他"
        }
        return type_names.get(self.item_type, "其他")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "item_type": self.item_type.value,
            "item_type_display": self.get_item_type_display(),
            "points_cost": self.points_cost,
            "item_value": self.item_value,
            "status": self.status.value,
            "status_display": self.get_status_display(),
            "admin_approve_user_id": self.admin_approve_user_id,
            "admin_approve_time": self.admin_approve_time.isoformat() if self.admin_approve_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_pending": self.is_pending(),
            "is_completed": self.is_completed(),
            "is_failed": self.is_failed(),
            "is_cancelled": self.is_cancelled(),
            "can_cancel": self.can_cancel()
        }

@dataclass
class UserPointsSummary:
    """用户积分摘要"""
    
    user_id: int
    username: str
    current_points: int
    consecutive_checkin_days: int
    total_checkin_days: int
    last_checkin_date: Optional[date]
    total_earned_points: int
    total_spent_points: int
    total_expired_points: int
    
    def get_net_points(self) -> int:
        """获取净积分"""
        return self.total_earned_points - self.total_spent_points - self.total_expired_points
    
    def get_checkin_streak(self) -> int:
        """获取签到连续天数"""
        return self.consecutive_checkin_days
    
    def is_checkin_today(self) -> bool:
        """今天是否已签到"""
        return self.last_checkin_date == date.today()
    
    def get_next_checkin_bonus(self) -> int:
        """获取下次签到奖励积分"""
        next_days = self.consecutive_checkin_days + 1
        if next_days >= 30:
            return 500
        elif next_days >= 7:
            return 150
        elif next_days >= 3:
            return 50
        else:
            return 10
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "current_points": self.current_points,
            "consecutive_checkin_days": self.consecutive_checkin_days,
            "total_checkin_days": self.total_checkin_days,
            "last_checkin_date": self.last_checkin_date.isoformat() if self.last_checkin_date else None,
            "total_earned_points": self.total_earned_points,
            "total_spent_points": self.total_spent_points,
            "total_expired_points": self.total_expired_points,
            "net_points": self.get_net_points(),
            "checkin_streak": self.get_checkin_streak(),
            "is_checkin_today": self.is_checkin_today(),
            "next_checkin_bonus": self.get_next_checkin_bonus()
        }
