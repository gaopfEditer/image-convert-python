"""
反馈留言实体
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class FeedbackCategory(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    SUGGESTION = "suggestion"
    COMPLAINT = "complaint"
    OTHER = "other"

class FeedbackStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"

class FeedbackPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Feedback:
    """反馈留言实体"""
    
    # 基本信息
    id: Optional[int] = None
    user_id: int = 0
    title: str = ""
    content: str = ""
    category: FeedbackCategory = FeedbackCategory.OTHER
    status: FeedbackStatus = FeedbackStatus.PENDING
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    
    # 管理员回复
    admin_reply: Optional[str] = None
    admin_reply_time: Optional[datetime] = None
    admin_user_id: Optional[int] = None
    
    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_replied(self) -> bool:
        """是否已回复"""
        return self.admin_reply is not None and self.admin_reply.strip() != ""
    
    def is_resolved(self) -> bool:
        """是否已解决"""
        return self.status == FeedbackStatus.RESOLVED
    
    def is_closed(self) -> bool:
        """是否已关闭"""
        return self.status == FeedbackStatus.CLOSED
    
    def can_reply(self) -> bool:
        """是否可以回复"""
        return self.status in [FeedbackStatus.PENDING, FeedbackStatus.PROCESSING]
    
    def get_reply_status(self) -> str:
        """获取回复状态"""
        if self.is_replied():
            return "replied"
        elif self.is_resolved():
            return "resolved"
        elif self.is_closed():
            return "closed"
        else:
            return "pending"
    
    def get_priority_level(self) -> int:
        """获取优先级等级（数字）"""
        priority_levels = {
            FeedbackPriority.LOW: 1,
            FeedbackPriority.MEDIUM: 2,
            FeedbackPriority.HIGH: 3,
            FeedbackPriority.URGENT: 4
        }
        return priority_levels.get(self.priority, 2)
    
    def get_category_display(self) -> str:
        """获取分类显示名称"""
        category_names = {
            FeedbackCategory.BUG: "Bug报告",
            FeedbackCategory.FEATURE: "功能建议",
            FeedbackCategory.SUGGESTION: "改进建议",
            FeedbackCategory.COMPLAINT: "投诉",
            FeedbackCategory.OTHER: "其他"
        }
        return category_names.get(self.category, "其他")
    
    def get_status_display(self) -> str:
        """获取状态显示名称"""
        status_names = {
            FeedbackStatus.PENDING: "待处理",
            FeedbackStatus.PROCESSING: "处理中",
            FeedbackStatus.RESOLVED: "已解决",
            FeedbackStatus.CLOSED: "已关闭"
        }
        return status_names.get(self.status, "待处理")
    
    def get_priority_display(self) -> str:
        """获取优先级显示名称"""
        priority_names = {
            FeedbackPriority.LOW: "低",
            FeedbackPriority.MEDIUM: "中",
            FeedbackPriority.HIGH: "高",
            FeedbackPriority.URGENT: "紧急"
        }
        return priority_names.get(self.priority, "中")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "category": self.category.value,
            "category_display": self.get_category_display(),
            "status": self.status.value,
            "status_display": self.get_status_display(),
            "priority": self.priority.value,
            "priority_display": self.get_priority_display(),
            "admin_reply": self.admin_reply,
            "admin_reply_time": self.admin_reply_time.isoformat() if self.admin_reply_time else None,
            "admin_user_id": self.admin_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_replied": self.is_replied(),
            "is_resolved": self.is_resolved(),
            "is_closed": self.is_closed(),
            "can_reply": self.can_reply(),
            "reply_status": self.get_reply_status()
        }
