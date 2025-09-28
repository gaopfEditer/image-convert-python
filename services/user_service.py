from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date
from typing import Optional
from models import User, DailyUsage, UserRole
from framework.schemas import UserCreate, UserUpdate, UsageStatsResponse
from auth import get_password_hash, verify_password
from config import settings

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建新用户"""
        # 检查用户名和邮箱是否已存在
        if self.get_user_by_username(user_data.username):
            raise ValueError("用户名已存在")
        
        if self.get_user_by_email(user_data.email):
            raise ValueError("邮箱已存在")
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole.FREE
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def create_user_from_wechat(self, user_data: dict) -> User:
        """从微信信息创建用户"""
        # 检查微信openid是否已存在
        if user_data.get("wechat_openid") and self.get_user_by_wechat_openid(user_data["wechat_openid"]):
            raise ValueError("该微信账号已绑定其他用户")
        
        # 创建用户
        db_user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=user_data.get("password") and get_password_hash(user_data["password"]) or None,
            role=UserRole.FREE,
            wechat_openid=user_data.get("wechat_openid"),
            wechat_unionid=user_data.get("wechat_unionid"),
            wechat_nickname=user_data.get("wechat_nickname"),
            wechat_avatar=user_data.get("wechat_avatar"),
            is_wechat_user=user_data.get("is_wechat_user", False)
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_wechat_openid(self, openid: str) -> Optional[User]:
        """根据微信openid获取用户"""
        return self.db.query(User).filter(User.wechat_openid == openid).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        # 如果更新密码，需要加密
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user_role(self, user_id: int, new_role: UserRole) -> bool:
        """更新用户会员等级"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.role = new_role
        self.db.commit()
        return True
    
    def get_daily_usage(self, user_id: int, usage_date: date = None) -> DailyUsage:
        """获取用户每日使用情况"""
        if usage_date is None:
            usage_date = date.today()
        
        daily_usage = self.db.query(DailyUsage).filter(
            and_(
                DailyUsage.user_id == user_id,
                func.date(DailyUsage.usage_date) == usage_date
            )
        ).first()
        
        if not daily_usage:
            # 创建新的每日使用记录
            daily_usage = DailyUsage(
                user_id=user_id,
                usage_date=datetime.combine(usage_date, datetime.min.time()),
                usage_count=0
            )
            self.db.add(daily_usage)
            self.db.commit()
            self.db.refresh(daily_usage)
        
        return daily_usage
    
    def increment_daily_usage(self, user_id: int) -> bool:
        """增加每日使用次数"""
        daily_usage = self.get_daily_usage(user_id)
        daily_usage.usage_count += 1
        self.db.commit()
        return True
    
    def get_usage_stats(self, user_id: int) -> UsageStatsResponse:
        """获取用户使用统计"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        daily_usage = self.get_daily_usage(user_id)
        
        # 根据用户角色获取每日限制
        daily_limits = {
            UserRole.FREE: settings.free_user_daily_limit,
            UserRole.VIP: settings.vip_user_daily_limit,
            UserRole.SVIP: settings.svip_user_daily_limit
        }
        
        daily_limit = daily_limits.get(user.role, settings.free_user_daily_limit)
        remaining_usage = max(0, daily_limit - daily_usage.usage_count)
        
        return UsageStatsResponse(
            today_usage=daily_usage.usage_count,
            daily_limit=daily_limit,
            remaining_usage=remaining_usage,
            role=user.role
        )
    
    def can_use_service(self, user_id: int) -> bool:
        """检查用户是否可以使用服务"""
        stats = self.get_usage_stats(user_id)
        return stats.remaining_usage > 0
