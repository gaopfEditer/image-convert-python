from sqlalchemy.orm import Session
from models import User, UserRole
from services.user_service import UserService
from config import settings

class PermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def check_conversion_permission(self, user_id: int) -> tuple[bool, str]:
        """
        检查用户是否有权限进行图片转换
        返回: (是否有权限, 错误信息)
        """
        # 检查用户是否存在且活跃
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        if not user.is_active:
            return False, "用户账户已被禁用"
        
        # 检查每日使用限制
        if not self.user_service.can_use_service(user_id):
            stats = self.user_service.get_usage_stats(user_id)
            return False, f"今日使用次数已达上限({stats.daily_limit}次)，请升级会员或明天再试"
        
        return True, ""
    
    def get_user_limits(self, user_id: int) -> dict:
        """获取用户使用限制信息"""
        stats = self.user_service.get_usage_stats(user_id)
        
        return {
            "role": stats.role.value,
            "today_usage": stats.today_usage,
            "daily_limit": stats.daily_limit,
            "remaining_usage": stats.remaining_usage,
            "can_use": stats.remaining_usage > 0
        }
    
    def get_role_benefits(self, role: UserRole) -> dict:
        """获取角色权益信息"""
        benefits = {
            UserRole.FREE: {
                "daily_limit": settings.free_user_daily_limit,
                "features": [
                    "基础图片格式转换",
                    "标准转换质量",
                    "每日5次免费转换"
                ],
                "restrictions": [
                    "无法使用批量转换",
                    "无法去除水印",
                    "转换速度较慢"
                ]
            },
            UserRole.VIP: {
                "daily_limit": settings.vip_user_daily_limit,
                "features": [
                    "高质量图片转换",
                    "批量转换功能",
                    "每日100次转换",
                    "优先处理队列",
                    "去除水印"
                ],
                "restrictions": [
                    "无法使用API接口"
                ]
            },
            UserRole.SVIP: {
                "daily_limit": settings.svip_user_daily_limit,
                "features": [
                    "最高质量图片转换",
                    "无限制批量转换",
                    "每日1000次转换",
                    "最高优先级处理",
                    "API接口访问",
                    "自定义水印",
                    "24/7技术支持"
                ],
                "restrictions": []
            }
        }
        
        return benefits.get(role, benefits[UserRole.FREE])
    
    def can_access_feature(self, user_id: int, feature: str) -> bool:
        """检查用户是否可以访问特定功能"""
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return False
        
        # 功能权限映射
        feature_permissions = {
            "batch_convert": [UserRole.VIP, UserRole.SVIP],
            "remove_watermark": [UserRole.VIP, UserRole.SVIP],
            "api_access": [UserRole.SVIP],
            "priority_processing": [UserRole.VIP, UserRole.SVIP],
            "custom_watermark": [UserRole.SVIP],
            "high_quality": [UserRole.VIP, UserRole.SVIP]
        }
        
        required_roles = feature_permissions.get(feature, [])
        return user.role in required_roles
    
    def get_upgrade_options(self, current_role: UserRole) -> list:
        """获取升级选项"""
        upgrade_options = []
        
        if current_role == UserRole.FREE:
            upgrade_options.extend([
                {
                    "target_role": UserRole.VIP.value,
                    "price": settings.vip_price,
                    "benefits": self.get_role_benefits(UserRole.VIP)["features"],
                    "daily_limit": settings.vip_user_daily_limit
                },
                {
                    "target_role": UserRole.SVIP.value,
                    "price": settings.svip_price,
                    "benefits": self.get_role_benefits(UserRole.SVIP)["features"],
                    "daily_limit": settings.svip_user_daily_limit
                }
            ])
        elif current_role == UserRole.VIP:
            upgrade_options.append({
                "target_role": UserRole.SVIP.value,
                "price": settings.svip_price,
                "benefits": self.get_role_benefits(UserRole.SVIP)["features"],
                "daily_limit": settings.svip_user_daily_limit
            })
        
        return upgrade_options
    
    def log_usage(self, user_id: int, action: str, details: dict = None) -> bool:
        """记录用户使用日志"""
        try:
            # 增加每日使用次数
            self.user_service.increment_daily_usage(user_id)
            
            # 这里可以添加更详细的日志记录
            # 比如记录具体的操作类型、时间等
            
            return True
        except Exception:
            return False
