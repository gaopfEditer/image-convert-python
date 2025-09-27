"""
积分系统API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from infra.database.connection import get_db
from business.points.service import PointsService
from infra.database.repositories.points_repo import PointsRepository
from infra.database.repositories.user_repo import UserRepository
from framework.schemas.points import (
    CheckinResponse, PointsSummaryResponse, PointRecordResponse,
    PointExchangeRequest, PointExchangeResponse, ExchangeListResponse
)
from framework.middleware.auth import get_current_user
from domain.entities.points import PointType, PointSource, ExchangeItemType, ExchangeStatus
from types import User

router = APIRouter(prefix="/points", tags=["积分系统"])

# 依赖注入
def get_points_service(db: Session = Depends(get_db)) -> PointsService:
    """获取积分服务"""
    points_repo = PointsRepository(db)
    user_repo = UserRepository(db)
    
    return PointsService(points_repo, user_repo)

@router.post("/checkin", response_model=CheckinResponse, summary="用户签到")
async def user_checkin(
    checkin_date: Optional[date] = Form(None),
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """用户签到获取积分"""
    
    success, checkin_record, error_message = await points_service.process_checkin(
        user_id=current_user.id,
        checkin_date=checkin_date
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return CheckinResponse.from_entity(checkin_record)

@router.get("/summary", response_model=PointsSummaryResponse, summary="获取积分摘要")
async def get_points_summary(
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """获取用户积分摘要信息"""
    
    summary = await points_service.get_user_points_summary(current_user.id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户积分信息不存在"
        )
    
    return PointsSummaryResponse.from_entity(summary)

@router.get("/records", response_model=List[PointRecordResponse], summary="获取积分记录")
async def get_point_records(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    point_type: Optional[PointType] = Query(None),
    source: Optional[PointSource] = Query(None),
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """获取用户积分记录列表"""
    
    records = await points_service.get_user_point_records(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        point_type=point_type,
        source=source
    )
    
    return [PointRecordResponse.from_entity(record) for record in records]

@router.get("/checkin/records", response_model=List[CheckinResponse], summary="获取签到记录")
async def get_checkin_records(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """获取用户签到记录列表"""
    
    records = await points_service.get_user_checkin_records(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return [CheckinResponse.from_entity(record) for record in records]

@router.post("/exchange", response_model=PointExchangeResponse, summary="积分兑换")
async def create_point_exchange(
    request: PointExchangeRequest,
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """创建积分兑换申请"""
    
    success, exchange, error_message = await points_service.create_point_exchange(
        user_id=current_user.id,
        item_name=request.item_name,
        item_type=request.item_type,
        points_cost=request.points_cost,
        item_value=request.item_value
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return PointExchangeResponse.from_entity(exchange)

@router.get("/exchange/list", response_model=ExchangeListResponse, summary="获取兑换记录")
async def get_exchange_list(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[ExchangeStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """获取用户兑换记录列表"""
    
    exchanges = await points_service.get_user_exchanges(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        status=status
    )
    
    return ExchangeListResponse(
        exchanges=[PointExchangeResponse.from_entity(e) for e in exchanges],
        total=len(exchanges),
        limit=limit,
        offset=offset
    )

@router.get("/exchange/{exchange_id}", response_model=PointExchangeResponse, summary="获取兑换详情")
async def get_exchange_detail(
    exchange_id: int,
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """获取兑换记录详情"""
    
    # 这里需要从服务层获取单个兑换记录的方法
    # exchange = await points_service.get_exchange_by_id(exchange_id, current_user.id)
    
    # if not exchange:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="兑换记录不存在"
    #     )
    
    # return PointExchangeResponse.from_entity(exchange)
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )

@router.post("/exchange/{exchange_id}/cancel", summary="取消兑换")
async def cancel_exchange(
    exchange_id: int,
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """取消兑换申请"""
    
    # 这里需要实现取消兑换的逻辑
    # success = await points_service.cancel_exchange(exchange_id, current_user.id)
    
    # if not success:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="无法取消该兑换"
    #     )
    
    # return {"message": "取消成功", "success": True}
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )

# 管理员接口
@router.post("/exchange/{exchange_id}/approve", response_model=PointExchangeResponse, summary="管理员审批兑换")
async def admin_approve_exchange(
    exchange_id: int,
    approve: bool = Form(True),
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """管理员审批兑换申请"""
    
    # 这里需要检查用户是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="权限不足"
    #     )
    
    success, exchange, error_message = await points_service.admin_approve_exchange(
        exchange_id=exchange_id,
        admin_user_id=current_user.id,
        approve=approve
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return PointExchangeResponse.from_entity(exchange)

@router.post("/admin/adjust", summary="管理员调整积分")
async def admin_adjust_points(
    user_id: int = Form(...),
    points: int = Form(...),
    description: str = Form(...),
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """管理员调整用户积分"""
    
    # 这里需要检查用户是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="权限不足"
    #     )
    
    success, point_record, error_message = await points_service.add_points(
        user_id=user_id,
        points=points,
        source=PointSource.ADMIN,
        description=description,
        related_id=None,
        related_type="admin_adjust"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return {
        "message": "积分调整成功",
        "success": True,
        "point_record": PointRecordResponse.from_entity(point_record)
    }

@router.get("/admin/statistics", summary="获取积分统计")
async def get_points_statistics(
    current_user: User = Depends(get_current_user),
    points_service: PointsService = Depends(get_points_service)
):
    """获取积分系统统计信息"""
    
    # 这里需要检查用户是否为管理员
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="权限不足"
    #     )
    
    # 这里需要实现积分统计的逻辑
    # stats = await points_service.get_points_statistics()
    
    # return stats
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )
