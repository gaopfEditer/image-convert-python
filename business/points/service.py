"""
积分系统业务服务
"""
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta

from domain.entities.points import (
    PointRecord, CheckinRecord, PointExchange, UserPointsSummary,
    PointType, PointSource, ExchangeItemType, ExchangeStatus
)
from infra.database.repositories.points_repo import PointsRepository
from infra.database.repositories.user_repo import UserRepository
from types import User

class PointsService:
    """积分系统业务服务"""
    
    def __init__(
        self,
        points_repo: PointsRepository,
        user_repo: UserRepository
    ):
        self.points_repo = points_repo
        self.user_repo = user_repo
    
    async def add_points(
        self,
        user_id: int,
        points: int,
        source: PointSource,
        description: str,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None,
        expires_days: Optional[int] = None
    ) -> Tuple[bool, Optional[PointRecord], Optional[str]]:
        """添加积分"""
        
        try:
            # 计算过期时间
            expires_at = None
            if expires_days:
                expires_at = datetime.now() + timedelta(days=expires_days)
            
            # 创建积分记录
            point_record = PointRecord(
                user_id=user_id,
                points=points,
                type=PointType.EARN,
                source=source,
                description=description,
                related_id=related_id,
                related_type=related_type,
                expires_at=expires_at,
                created_at=datetime.now()
            )
            
            # 保存积分记录
            point_record = await self.points_repo.create_point_record(point_record)
            
            # 更新用户积分
            await self.user_repo.update_user_points(user_id, points)
            
            return True, point_record, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def spend_points(
        self,
        user_id: int,
        points: int,
        source: PointSource,
        description: str,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None
    ) -> Tuple[bool, Optional[PointRecord], Optional[str]]:
        """消费积分"""
        
        try:
            # 检查用户积分是否足够
            user = await self.user_repo.get_user_by_id(user_id)
            if not user or user.points < points:
                return False, None, "积分不足"
            
            # 创建积分记录
            point_record = PointRecord(
                user_id=user_id,
                points=-points,  # 负数表示消费
                type=PointType.SPEND,
                source=source,
                description=description,
                related_id=related_id,
                related_type=related_type,
                created_at=datetime.now()
            )
            
            # 保存积分记录
            point_record = await self.points_repo.create_point_record(point_record)
            
            # 更新用户积分
            await self.user_repo.update_user_points(user_id, -points)
            
            return True, point_record, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def process_checkin(
        self,
        user_id: int,
        checkin_date: Optional[date] = None
    ) -> Tuple[bool, Optional[CheckinRecord], Optional[str]]:
        """处理用户签到"""
        
        try:
            if checkin_date is None:
                checkin_date = date.today()
            
            # 检查是否已经签到
            existing_checkin = await self.points_repo.get_checkin_by_date(user_id, checkin_date)
            if existing_checkin:
                return False, None, "今天已经签到过了"
            
            # 获取用户信息
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                return False, None, "用户不存在"
            
            # 计算连续签到天数
            consecutive_days = 1
            if user.last_checkin_date:
                if user.last_checkin_date == checkin_date - timedelta(days=1):
                    consecutive_days = user.consecutive_checkin_days + 1
                elif user.last_checkin_date < checkin_date - timedelta(days=1):
                    consecutive_days = 1  # 重新开始计算
            
            # 计算签到奖励积分
            points_earned = await self._calculate_checkin_points(consecutive_days)
            
            # 创建签到记录
            checkin_record = CheckinRecord(
                user_id=user_id,
                checkin_date=checkin_date,
                points_earned=points_earned,
                consecutive_days=consecutive_days,
                created_at=datetime.now()
            )
            
            # 保存签到记录
            checkin_record = await self.points_repo.create_checkin_record(checkin_record)
            
            # 添加积分
            await self.add_points(
                user_id=user_id,
                points=points_earned,
                source=PointSource.CHECKIN,
                description=f"连续签到{consecutive_days}天",
                related_id=checkin_record.id,
                related_type="checkin"
            )
            
            # 更新用户签到信息
            await self.user_repo.update_user_checkin_info(
                user_id=user_id,
                checkin_date=checkin_date,
                consecutive_days=consecutive_days
            )
            
            return True, checkin_record, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def _calculate_checkin_points(self, consecutive_days: int) -> int:
        """计算签到奖励积分"""
        
        # 获取积分规则
        rules = await self.points_repo.get_point_rules_by_type("checkin")
        
        # 按连续天数排序，找到最匹配的规则
        best_rule = None
        for rule in rules:
            if rule.get("consecutive_days", 0) <= consecutive_days:
                if not best_rule or rule.get("consecutive_days", 0) > best_rule.get("consecutive_days", 0):
                    best_rule = rule
        
        if best_rule:
            return best_rule.get("points", 10)
        
        # 默认积分
        if consecutive_days >= 30:
            return 500
        elif consecutive_days >= 7:
            return 150
        elif consecutive_days >= 3:
            return 50
        else:
            return 10
    
    async def get_user_points_summary(self, user_id: int) -> Optional[UserPointsSummary]:
        """获取用户积分摘要"""
        
        return await self.points_repo.get_user_points_summary(user_id)
    
    async def get_user_point_records(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        point_type: Optional[PointType] = None,
        source: Optional[PointSource] = None
    ) -> List[PointRecord]:
        """获取用户积分记录"""
        
        return await self.points_repo.get_user_point_records(
            user_id=user_id,
            limit=limit,
            offset=offset,
            point_type=point_type,
            source=source
        )
    
    async def get_user_checkin_records(
        self,
        user_id: int,
        limit: int = 30,
        offset: int = 0
    ) -> List[CheckinRecord]:
        """获取用户签到记录"""
        
        return await self.points_repo.get_user_checkin_records(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
    
    async def create_point_exchange(
        self,
        user_id: int,
        item_name: str,
        item_type: ExchangeItemType,
        points_cost: int,
        item_value: Optional[str] = None
    ) -> Tuple[bool, Optional[PointExchange], Optional[str]]:
        """创建积分兑换"""
        
        try:
            # 检查用户积分是否足够
            user = await self.user_repo.get_user_by_id(user_id)
            if not user or user.points < points_cost:
                return False, None, "积分不足"
            
            # 创建兑换记录
            exchange = PointExchange(
                user_id=user_id,
                item_name=item_name,
                item_type=item_type,
                points_cost=points_cost,
                item_value=item_value,
                status=ExchangeStatus.PENDING,
                created_at=datetime.now()
            )
            
            # 保存兑换记录
            exchange = await self.points_repo.create_point_exchange(exchange)
            
            # 扣除积分
            await self.spend_points(
                user_id=user_id,
                points=points_cost,
                source=PointSource.EXCHANGE,
                description=f"兑换{item_name}",
                related_id=exchange.id,
                related_type="exchange"
            )
            
            return True, exchange, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def get_user_exchanges(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        status: Optional[ExchangeStatus] = None
    ) -> List[PointExchange]:
        """获取用户兑换记录"""
        
        return await self.points_repo.get_user_exchanges(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status=status
        )
    
    async def admin_approve_exchange(
        self,
        exchange_id: int,
        admin_user_id: int,
        approve: bool
    ) -> Tuple[bool, Optional[PointExchange], Optional[str]]:
        """管理员审批兑换"""
        
        try:
            # 获取兑换记录
            exchange = await self.points_repo.get_exchange_by_id(exchange_id)
            if not exchange:
                return False, None, "兑换记录不存在"
            
            if exchange.status != ExchangeStatus.PENDING:
                return False, None, "该兑换记录已处理"
            
            # 更新状态
            if approve:
                exchange.status = ExchangeStatus.COMPLETED
            else:
                exchange.status = ExchangeStatus.FAILED
                # 退还积分
                await self.add_points(
                    user_id=exchange.user_id,
                    points=exchange.points_cost,
                    source=PointSource.ADMIN,
                    description=f"兑换失败退还积分",
                    related_id=exchange.id,
                    related_type="exchange"
                )
            
            exchange.admin_approve_user_id = admin_user_id
            exchange.admin_approve_time = datetime.now()
            
            # 保存更新
            exchange = await self.points_repo.update_exchange(exchange)
            
            return True, exchange, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def expire_points(self, user_id: int) -> int:
        """处理过期积分"""
        
        try:
            # 获取过期的积分记录
            expired_records = await self.points_repo.get_expired_point_records(user_id)
            
            total_expired = 0
            for record in expired_records:
                if record.points > 0:  # 只处理获得的积分
                    # 创建过期记录
                    expire_record = PointRecord(
                        user_id=user_id,
                        points=-record.points,
                        type=PointType.EXPIRE,
                        source=PointSource.OTHER,
                        description=f"积分过期: {record.description}",
                        related_id=record.id,
                        related_type="point_expire",
                        created_at=datetime.now()
                    )
                    
                    await self.points_repo.create_point_record(expire_record)
                    total_expired += record.points
            
            # 更新用户积分
            if total_expired > 0:
                await self.user_repo.update_user_points(user_id, -total_expired)
            
            return total_expired
            
        except Exception as e:
            return 0
