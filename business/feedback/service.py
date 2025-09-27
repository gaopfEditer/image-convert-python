"""
反馈留言业务服务
"""
from typing import List, Optional, Tuple
from datetime import datetime

from domain.entities.feedback import Feedback, FeedbackCategory, FeedbackStatus, FeedbackPriority
from infra.database.repositories.feedback_repo import FeedbackRepository
from business.points.service import PointsService
from types import User

class FeedbackService:
    """反馈留言业务服务"""
    
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        points_service: PointsService
    ):
        self.feedback_repo = feedback_repo
        self.points_service = points_service
    
    async def create_feedback(
        self,
        user: User,
        title: str,
        content: str,
        category: FeedbackCategory,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM
    ) -> Tuple[bool, Optional[Feedback], Optional[str]]:
        """创建反馈留言"""
        
        try:
            # 创建反馈实体
            feedback = Feedback(
                user_id=user.id,
                title=title,
                content=content,
                category=category,
                priority=priority,
                status=FeedbackStatus.PENDING,
                created_at=datetime.now()
            )
            
            # 保存到数据库
            feedback = await self.feedback_repo.create_feedback(feedback)
            
            # 给用户奖励积分
            await self.points_service.add_points(
                user_id=user.id,
                points=20,
                source="feedback",
                description="提交反馈留言",
                related_id=feedback.id,
                related_type="feedback"
            )
            
            return True, feedback, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def get_user_feedbacks(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        status_filter: Optional[FeedbackStatus] = None,
        category_filter: Optional[FeedbackCategory] = None
    ) -> List[Feedback]:
        """获取用户的反馈列表"""
        
        return await self.feedback_repo.get_user_feedbacks(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status_filter=status_filter,
            category_filter=category_filter
        )
    
    async def get_feedback_detail(
        self,
        feedback_id: int,
        user_id: int
    ) -> Optional[Feedback]:
        """获取反馈详情"""
        
        return await self.feedback_repo.get_feedback_by_id(feedback_id, user_id)
    
    async def update_feedback(
        self,
        feedback_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[FeedbackCategory] = None,
        priority: Optional[FeedbackPriority] = None
    ) -> Tuple[bool, Optional[Feedback], Optional[str]]:
        """更新反馈（仅限待处理状态）"""
        
        try:
            # 获取反馈
            feedback = await self.feedback_repo.get_feedback_by_id(feedback_id, user_id)
            if not feedback:
                return False, None, "反馈不存在"
            
            # 检查是否可以修改
            if not feedback.can_reply():
                return False, None, "该反馈已处理，无法修改"
            
            # 更新字段
            if title is not None:
                feedback.title = title
            if content is not None:
                feedback.content = content
            if category is not None:
                feedback.category = category
            if priority is not None:
                feedback.priority = priority
            
            feedback.updated_at = datetime.now()
            
            # 保存更新
            feedback = await self.feedback_repo.update_feedback(feedback)
            
            return True, feedback, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def delete_feedback(
        self,
        feedback_id: int,
        user_id: int
    ) -> bool:
        """删除反馈（仅限待处理状态）"""
        
        try:
            # 获取反馈
            feedback = await self.feedback_repo.get_feedback_by_id(feedback_id, user_id)
            if not feedback:
                return False
            
            # 检查是否可以删除
            if not feedback.can_reply():
                return False
            
            # 删除反馈
            await self.feedback_repo.delete_feedback(feedback_id, user_id)
            
            return True
            
        except Exception as e:
            return False
    
    async def admin_reply_feedback(
        self,
        feedback_id: int,
        admin_user_id: int,
        reply_content: str,
        new_status: Optional[FeedbackStatus] = None
    ) -> Tuple[bool, Optional[Feedback], Optional[str]]:
        """管理员回复反馈"""
        
        try:
            # 获取反馈
            feedback = await self.feedback_repo.get_feedback_by_id(feedback_id)
            if not feedback:
                return False, None, "反馈不存在"
            
            # 更新回复信息
            feedback.admin_reply = reply_content
            feedback.admin_reply_time = datetime.now()
            feedback.admin_user_id = admin_user_id
            
            if new_status:
                feedback.status = new_status
            
            feedback.updated_at = datetime.now()
            
            # 保存更新
            feedback = await self.feedback_repo.update_feedback(feedback)
            
            # 如果状态变为已解决，给用户奖励积分
            if new_status == FeedbackStatus.RESOLVED:
                await self.points_service.add_points(
                    user_id=feedback.user_id,
                    points=100,
                    source="feedback",
                    description="反馈被采纳",
                    related_id=feedback.id,
                    related_type="feedback"
                )
            
            return True, feedback, None
            
        except Exception as e:
            return False, None, str(e)
    
    async def get_feedback_statistics(
        self,
        user_id: Optional[int] = None
    ) -> dict:
        """获取反馈统计信息"""
        
        stats = await self.feedback_repo.get_feedback_statistics(user_id)
        
        return {
            "total_feedbacks": stats.get("total", 0),
            "pending_feedbacks": stats.get("pending", 0),
            "processing_feedbacks": stats.get("processing", 0),
            "resolved_feedbacks": stats.get("resolved", 0),
            "closed_feedbacks": stats.get("closed", 0),
            "by_category": stats.get("by_category", {}),
            "by_priority": stats.get("by_priority", {})
        }
    
    async def search_feedbacks(
        self,
        keyword: str,
        category: Optional[FeedbackCategory] = None,
        status: Optional[FeedbackStatus] = None,
        priority: Optional[FeedbackPriority] = None,
        user_id: Optional[int] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Feedback]:
        """搜索反馈"""
        
        return await self.feedback_repo.search_feedbacks(
            keyword=keyword,
            category=category,
            status=status,
            priority=priority,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
