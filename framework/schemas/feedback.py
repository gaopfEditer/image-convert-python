"""
反馈留言API模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from domain.entities.feedback import FeedbackCategory, FeedbackPriority, FeedbackStatus

class FeedbackCreateRequest(BaseModel):
    """创建反馈请求"""
    title: str = Field(..., min_length=1, max_length=200, description="反馈标题")
    content: str = Field(..., min_length=1, max_length=5000, description="反馈内容")
    category: FeedbackCategory = Field(..., description="反馈分类")
    priority: FeedbackPriority = Field(FeedbackPriority.MEDIUM, description="优先级")

class FeedbackUpdateRequest(BaseModel):
    """更新反馈请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="反馈标题")
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="反馈内容")
    category: Optional[FeedbackCategory] = Field(None, description="反馈分类")
    priority: Optional[FeedbackPriority] = Field(None, description="优先级")

class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    user_id: int
    title: str
    content: str
    category: str
    category_display: str
    status: str
    status_display: str
    priority: str
    priority_display: str
    admin_reply: Optional[str] = None
    admin_reply_time: Optional[datetime] = None
    admin_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_replied: bool
    is_resolved: bool
    is_closed: bool
    can_reply: bool
    reply_status: str

    @classmethod
    def from_entity(cls, feedback) -> "FeedbackResponse":
        """从实体转换为响应模型"""
        return cls(
            id=feedback.id,
            user_id=feedback.user_id,
            title=feedback.title,
            content=feedback.content,
            category=feedback.category.value,
            category_display=feedback.get_category_display(),
            status=feedback.status.value,
            status_display=feedback.get_status_display(),
            priority=feedback.priority.value,
            priority_display=feedback.get_priority_display(),
            admin_reply=feedback.admin_reply,
            admin_reply_time=feedback.admin_reply_time,
            admin_user_id=feedback.admin_user_id,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            is_replied=feedback.is_replied(),
            is_resolved=feedback.is_resolved(),
            is_closed=feedback.is_closed(),
            can_reply=feedback.can_reply(),
            reply_status=feedback.get_reply_status()
        )

class FeedbackListResponse(BaseModel):
    """反馈列表响应"""
    feedbacks: List[FeedbackResponse]
    total: int
    limit: int
    offset: int

class FeedbackStatisticsResponse(BaseModel):
    """反馈统计响应"""
    total_feedbacks: int
    pending_feedbacks: int
    processing_feedbacks: int
    resolved_feedbacks: int
    closed_feedbacks: int
    by_category: dict
    by_priority: dict

class FeedbackSearchRequest(BaseModel):
    """反馈搜索请求"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    category: Optional[FeedbackCategory] = Field(None, description="分类筛选")
    status: Optional[FeedbackStatus] = Field(None, description="状态筛选")
    priority: Optional[FeedbackPriority] = Field(None, description="优先级筛选")
    limit: int = Field(10, ge=1, le=100, description="每页数量")
    offset: int = Field(0, ge=0, description="偏移量")

class AdminReplyRequest(BaseModel):
    """管理员回复请求"""
    reply_content: str = Field(..., min_length=1, max_length=5000, description="回复内容")
    new_status: Optional[FeedbackStatus] = Field(None, description="新状态")
