"""
积分系统API模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from domain.entities.points import PointType, PointSource, ExchangeItemType, ExchangeStatus

class CheckinResponse(BaseModel):
    """签到响应"""
    id: int
    user_id: int
    checkin_date: date
    points_earned: int
    consecutive_days: int
    created_at: datetime
    is_today: bool
    is_consecutive: bool
    consecutive_bonus: int

    @classmethod
    def from_entity(cls, checkin_record) -> "CheckinResponse":
        """从实体转换为响应模型"""
        return cls(
            id=checkin_record.id,
            user_id=checkin_record.user_id,
            checkin_date=checkin_record.checkin_date,
            points_earned=checkin_record.points_earned,
            consecutive_days=checkin_record.consecutive_days,
            created_at=checkin_record.created_at,
            is_today=checkin_record.is_today(),
            is_consecutive=checkin_record.is_consecutive(),
            consecutive_bonus=checkin_record.get_consecutive_bonus()
        )

class PointsSummaryResponse(BaseModel):
    """积分摘要响应"""
    user_id: int
    username: str
    current_points: int
    consecutive_checkin_days: int
    total_checkin_days: int
    last_checkin_date: Optional[date]
    total_earned_points: int
    total_spent_points: int
    total_expired_points: int
    net_points: int
    checkin_streak: int
    is_checkin_today: bool
    next_checkin_bonus: int

    @classmethod
    def from_entity(cls, summary) -> "PointsSummaryResponse":
        """从实体转换为响应模型"""
        return cls(
            user_id=summary.user_id,
            username=summary.username,
            current_points=summary.current_points,
            consecutive_checkin_days=summary.consecutive_checkin_days,
            total_checkin_days=summary.total_checkin_days,
            last_checkin_date=summary.last_checkin_date,
            total_earned_points=summary.total_earned_points,
            total_spent_points=summary.total_spent_points,
            total_expired_points=summary.total_expired_points,
            net_points=summary.get_net_points(),
            checkin_streak=summary.get_checkin_streak(),
            is_checkin_today=summary.is_checkin_today(),
            next_checkin_bonus=summary.get_next_checkin_bonus()
        )

class PointRecordResponse(BaseModel):
    """积分记录响应"""
    id: int
    user_id: int
    points: int
    absolute_points: int
    type: str
    source: str
    description: str
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    is_earned: bool
    is_spent: bool
    is_expired: bool
    is_admin_adjust: bool
    is_expired_now: bool

    @classmethod
    def from_entity(cls, point_record) -> "PointRecordResponse":
        """从实体转换为响应模型"""
        return cls(
            id=point_record.id,
            user_id=point_record.user_id,
            points=point_record.points,
            absolute_points=point_record.get_absolute_points(),
            type=point_record.type.value,
            source=point_record.source.value,
            description=point_record.description,
            related_id=point_record.related_id,
            related_type=point_record.related_type,
            expires_at=point_record.expires_at,
            created_at=point_record.created_at,
            is_earned=point_record.is_earned(),
            is_spent=point_record.is_spent(),
            is_expired=point_record.is_expired(),
            is_admin_adjust=point_record.is_admin_adjust(),
            is_expired_now=point_record.is_expired_now()
        )

class PointExchangeRequest(BaseModel):
    """积分兑换请求"""
    item_name: str = Field(..., min_length=1, max_length=200, description="兑换物品名称")
    item_type: ExchangeItemType = Field(..., description="物品类型")
    points_cost: int = Field(..., gt=0, description="消耗积分")
    item_value: Optional[str] = Field(None, max_length=500, description="物品值")

class PointExchangeResponse(BaseModel):
    """积分兑换响应"""
    id: int
    user_id: int
    item_name: str
    item_type: str
    item_type_display: str
    points_cost: int
    item_value: Optional[str] = None
    status: str
    status_display: str
    admin_approve_user_id: Optional[int] = None
    admin_approve_time: Optional[datetime] = None
    created_at: datetime
    is_pending: bool
    is_completed: bool
    is_failed: bool
    is_cancelled: bool
    can_cancel: bool

    @classmethod
    def from_entity(cls, exchange) -> "PointExchangeResponse":
        """从实体转换为响应模型"""
        return cls(
            id=exchange.id,
            user_id=exchange.user_id,
            item_name=exchange.item_name,
            item_type=exchange.item_type.value,
            item_type_display=exchange.get_item_type_display(),
            points_cost=exchange.points_cost,
            item_value=exchange.item_value,
            status=exchange.status.value,
            status_display=exchange.get_status_display(),
            admin_approve_user_id=exchange.admin_approve_user_id,
            admin_approve_time=exchange.admin_approve_time,
            created_at=exchange.created_at,
            is_pending=exchange.is_pending(),
            is_completed=exchange.is_completed(),
            is_failed=exchange.is_failed(),
            is_cancelled=exchange.is_cancelled(),
            can_cancel=exchange.can_cancel()
        )

class ExchangeListResponse(BaseModel):
    """兑换列表响应"""
    exchanges: List[PointExchangeResponse]
    total: int
    limit: int
    offset: int

class PointsStatisticsResponse(BaseModel):
    """积分统计响应"""
    total_users: int
    total_points_earned: int
    total_points_spent: int
    total_checkins: int
    active_users_today: int
    top_users: List[dict]

class AdminAdjustPointsRequest(BaseModel):
    """管理员调整积分请求"""
    user_id: int = Field(..., description="用户ID")
    points: int = Field(..., description="调整积分（正数为增加，负数为减少）")
    description: str = Field(..., min_length=1, max_length=500, description="调整说明")

class ExchangeApprovalRequest(BaseModel):
    """兑换审批请求"""
    approve: bool = Field(..., description="是否批准")
    reason: Optional[str] = Field(None, max_length=500, description="审批理由")
