"""
反馈留言API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from infra.database.connection import get_db
from business.feedback.service import FeedbackService
from infra.database.repositories.feedback_repo import FeedbackRepository
from business.points.service import PointsService
from infra.database.repositories.points_repo import PointsRepository
from infra.database.repositories.user_repo import UserRepository
from framework.schemas.feedback import (
    FeedbackCreateRequest, FeedbackUpdateRequest, FeedbackResponse,
    FeedbackListResponse, FeedbackStatisticsResponse
)
from framework.middleware.auth import get_current_user
from domain.entities.feedback import FeedbackCategory, FeedbackPriority, FeedbackStatus
from types import User

router = APIRouter(prefix="/feedback", tags=["反馈留言"])

# 依赖注入
def get_feedback_service(db: Session = Depends(get_db)) -> FeedbackService:
    """获取反馈服务"""
    feedback_repo = FeedbackRepository(db)
    points_repo = PointsRepository(db)
    user_repo = UserRepository(db)
    points_service = PointsService(points_repo, user_repo)
    
    return FeedbackService(feedback_repo, points_service)

@router.post("/create", response_model=FeedbackResponse, summary="创建反馈留言")
async def create_feedback(
    request: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """创建反馈留言"""
    
    success, feedback, error_message = await feedback_service.create_feedback(
        user=current_user,
        title=request.title,
        content=request.content,
        category=request.category,
        priority=request.priority
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return FeedbackResponse.from_entity(feedback)

@router.get("/list", response_model=FeedbackListResponse, summary="获取反馈列表")
async def get_feedback_list(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[FeedbackStatus] = Query(None),
    category_filter: Optional[FeedbackCategory] = Query(None),
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """获取用户的反馈列表"""
    
    feedbacks = await feedback_service.get_user_feedbacks(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        category_filter=category_filter
    )
    
    return FeedbackListResponse(
        feedbacks=[FeedbackResponse.from_entity(f) for f in feedbacks],
        total=len(feedbacks),
        limit=limit,
        offset=offset
    )

@router.get("/{feedback_id}", response_model=FeedbackResponse, summary="获取反馈详情")
async def get_feedback_detail(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """获取反馈详情"""
    
    feedback = await feedback_service.get_feedback_detail(feedback_id, current_user.id)
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="反馈不存在"
        )
    
    return FeedbackResponse.from_entity(feedback)

@router.put("/{feedback_id}", response_model=FeedbackResponse, summary="更新反馈")
async def update_feedback(
    feedback_id: int,
    request: FeedbackUpdateRequest,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """更新反馈（仅限待处理状态）"""
    
    success, feedback, error_message = await feedback_service.update_feedback(
        feedback_id=feedback_id,
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        category=request.category,
        priority=request.priority
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return FeedbackResponse.from_entity(feedback)

@router.delete("/{feedback_id}", summary="删除反馈")
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """删除反馈（仅限待处理状态）"""
    
    success = await feedback_service.delete_feedback(feedback_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除该反馈"
        )
    
    return {"message": "删除成功", "success": True}

@router.get("/statistics/summary", response_model=FeedbackStatisticsResponse, summary="获取反馈统计")
async def get_feedback_statistics(
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """获取反馈统计信息"""
    
    stats = await feedback_service.get_feedback_statistics(current_user.id)
    
    return FeedbackStatisticsResponse(**stats)

@router.get("/search", response_model=FeedbackListResponse, summary="搜索反馈")
async def search_feedbacks(
    keyword: str = Query(..., min_length=1),
    category: Optional[FeedbackCategory] = Query(None),
    status: Optional[FeedbackStatus] = Query(None),
    priority: Optional[FeedbackPriority] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """搜索反馈"""
    
    feedbacks = await feedback_service.search_feedbacks(
        keyword=keyword,
        category=category,
        status=status,
        priority=priority,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return FeedbackListResponse(
        feedbacks=[FeedbackResponse.from_entity(f) for f in feedbacks],
        total=len(feedbacks),
        limit=limit,
        offset=offset
    )

# 管理员接口
@router.post("/{feedback_id}/reply", response_model=FeedbackResponse, summary="管理员回复反馈")
async def admin_reply_feedback(
    feedback_id: int,
    reply_content: str = Form(...),
    new_status: Optional[FeedbackStatus] = Form(None),
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """管理员回复反馈"""
    
    # 这里需要检查用户是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="权限不足"
    #     )
    
    success, feedback, error_message = await feedback_service.admin_reply_feedback(
        feedback_id=feedback_id,
        admin_user_id=current_user.id,
        reply_content=reply_content,
        new_status=new_status
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return FeedbackResponse.from_entity(feedback)

@router.get("/admin/list", response_model=FeedbackListResponse, summary="管理员获取反馈列表")
async def admin_get_feedback_list(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[FeedbackStatus] = Query(None),
    category_filter: Optional[FeedbackCategory] = Query(None),
    priority_filter: Optional[FeedbackPriority] = Query(None),
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """管理员获取所有反馈列表"""
    
    # 这里需要检查用户是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="权限不足"
    #     )
    
    feedbacks = await feedback_service.get_user_feedbacks(
        user_id=None,  # 获取所有用户的反馈
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        category_filter=category_filter
    )
    
    return FeedbackListResponse(
        feedbacks=[FeedbackResponse.from_entity(f) for f in feedbacks],
        total=len(feedbacks),
        limit=limit,
        offset=offset
    )
