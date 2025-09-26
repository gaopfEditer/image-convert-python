import httpx
import json
import hashlib
import hmac
import time
import uuid
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, parse_qs
from config import settings
from sqlalchemy.orm import Session
from models import User
from services.user_service import UserService

class WeChatAuthService:
    """微信扫码登录服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        
        # 微信开放平台API地址
        self.wechat_auth_url = "https://open.weixin.qq.com/connect/qrconnect"
        self.wechat_token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        self.wechat_userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
        self.wechat_refresh_token_url = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
    
    def generate_auth_url(self, state: str = None) -> str:
        """生成微信扫码登录URL"""
        if not state:
            state = str(uuid.uuid4())
        
        params = {
            "appid": settings.wechat_open_app_id,
            "redirect_uri": settings.wechat_open_redirect_uri,
            "response_type": "code",
            "scope": settings.wechat_open_scope,
            "state": state
        }
        
        # 添加#wechat_redirect后缀
        auth_url = f"{self.wechat_auth_url}?{urlencode(params)}#wechat_redirect"
        
        return auth_url, state
    
    async def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """通过授权码获取access_token"""
        params = {
            "appid": settings.wechat_open_app_id,
            "secret": settings.wechat_open_app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.wechat_token_url, params=params)
                result = response.json()
                
                if "access_token" in result:
                    return result
                else:
                    print(f"获取access_token失败: {result}")
                    return None
                    
        except Exception as e:
            print(f"请求access_token异常: {e}")
            return None
    
    async def get_user_info(self, access_token: str, openid: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        params = {
            "access_token": access_token,
            "openid": openid
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.wechat_userinfo_url, params=params)
                result = response.json()
                
                if "openid" in result:
                    return result
                else:
                    print(f"获取用户信息失败: {result}")
                    return None
                    
        except Exception as e:
            print(f"请求用户信息异常: {e}")
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """刷新access_token"""
        params = {
            "appid": settings.wechat_open_app_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.wechat_refresh_token_url, params=params)
                result = response.json()
                
                if "access_token" in result:
                    return result
                else:
                    print(f"刷新access_token失败: {result}")
                    return None
                    
        except Exception as e:
            print(f"刷新access_token异常: {e}")
            return None
    
    def get_or_create_user_by_wechat(self, wechat_info: Dict[str, Any]) -> Tuple[User, bool]:
        """根据微信信息获取或创建用户"""
        openid = wechat_info.get("openid")
        if not openid:
            raise ValueError("微信信息中缺少openid")
        
        # 查找是否已存在该微信用户
        existing_user = self.db.query(User).filter(
            User.wechat_openid == openid
        ).first()
        
        if existing_user:
            return existing_user, False
        
        # 创建新用户
        nickname = wechat_info.get("nickname", "微信用户")
        # 生成唯一用户名
        username = f"wx_{openid[:8]}"
        
        # 确保用户名唯一
        counter = 1
        original_username = username
        while self.user_service.get_user_by_username(username):
            username = f"{original_username}_{counter}"
            counter += 1
        
        # 创建用户
        user_data = {
            "username": username,
            "email": f"{openid}@wechat.local",  # 虚拟邮箱
            "password": str(uuid.uuid4()),  # 随机密码
            "wechat_openid": openid,
            "wechat_nickname": nickname,
            "wechat_avatar": wechat_info.get("headimgurl", ""),
            "wechat_unionid": wechat_info.get("unionid", ""),
            "is_wechat_user": True
        }
        
        new_user = self.user_service.create_user_from_wechat(user_data)
        return new_user, True
    
    def validate_wechat_signature(self, signature: str, timestamp: str, nonce: str, token: str = None) -> bool:
        """验证微信签名"""
        if not token:
            token = settings.wechat_open_app_secret
        
        # 将token、timestamp、nonce三个参数进行字典序排序
        tmp_arr = [token, timestamp, nonce]
        tmp_arr.sort()
        
        # 将三个参数字符串拼接成一个字符串进行sha1加密
        tmp_str = "".join(tmp_arr)
        tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        
        # 将sha1加密后的字符串与signature对比
        return tmp_str == signature
    
    def generate_jsapi_signature(self, url: str, timestamp: str, nonce: str) -> str:
        """生成JSAPI签名"""
        jsapi_ticket = self.get_jsapi_ticket()
        if not jsapi_ticket:
            return ""
        
        # 对所有待签名参数按照字段名的ASCII码从小到大排序
        string1 = f"jsapi_ticket={jsapi_ticket}&noncestr={nonce}&timestamp={timestamp}&url={url}"
        
        # 对string1作sha1加密
        signature = hashlib.sha1(string1.encode('utf-8')).hexdigest()
        return signature
    
    def get_jsapi_ticket(self) -> Optional[str]:
        """获取JSAPI ticket"""
        # 这里应该从缓存或数据库获取ticket
        # 简化实现，实际应该调用微信API获取
        return "jsapi_ticket_placeholder"
    
    async def handle_wechat_callback(self, code: str, state: str) -> Tuple[Optional[User], str]:
        """处理微信登录回调"""
        try:
            # 获取access_token
            token_info = await self.get_access_token(code)
            if not token_info:
                return None, "获取access_token失败"
            
            access_token = token_info.get("access_token")
            openid = token_info.get("openid")
            
            if not access_token or not openid:
                return None, "access_token或openid为空"
            
            # 获取用户信息
            user_info = await self.get_user_info(access_token, openid)
            if not user_info:
                return None, "获取用户信息失败"
            
            # 获取或创建用户
            user, is_new = self.get_or_create_user_by_wechat(user_info)
            
            # 更新微信信息
            user.wechat_nickname = user_info.get("nickname", "")
            user.wechat_avatar = user_info.get("headimgurl", "")
            user.wechat_unionid = user_info.get("unionid", "")
            self.db.commit()
            
            return user, "success"
            
        except Exception as e:
            print(f"处理微信回调异常: {e}")
            return None, f"处理异常: {str(e)}"
    
    def get_wechat_login_status(self, state: str) -> Dict[str, Any]:
        """获取微信登录状态"""
        # 这里可以从Redis或数据库获取登录状态
        # 简化实现
        return {
            "status": "pending",
            "message": "等待扫码"
        }
    
    def set_wechat_login_status(self, state: str, status: str, user_id: int = None, message: str = ""):
        """设置微信登录状态"""
        # 这里可以存储到Redis或数据库
        # 简化实现
        pass
