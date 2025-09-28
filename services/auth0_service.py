import httpx
import json
import uuid
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode
from config import settings
from sqlalchemy.orm import Session
from models import User
from services.user_service import UserService

class Auth0Service:
    """Auth0登录服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        
        # Auth0 API地址
        self.auth0_domain = settings.auth0_domain
        self.auth0_auth_url = f"https://{self.auth0_domain}/authorize"
        self.auth0_token_url = f"https://{self.auth0_domain}/oauth/token"
        self.auth0_userinfo_url = f"https://{self.auth0_domain}/userinfo"
    
    def generate_auth_url(self, state: str = None) -> str:
        """生成Auth0登录URL"""
        if not state:
            state = str(uuid.uuid4())
        
        params = {
            "response_type": "code",
            "client_id": settings.auth0_client_id,
            "redirect_uri": settings.auth0_redirect_uri,
            "scope": settings.auth0_scope,
            "state": state
        }
        
        # 添加audience（如果配置了）
        if settings.auth0_audience:
            params["audience"] = settings.auth0_audience
        
        auth_url = f"{self.auth0_auth_url}?{urlencode(params)}"
        return auth_url, state
    
    async def get_access_token(self, code: str, redirect_uri: str = None) -> Optional[Dict[str, Any]]:
        """获取Auth0访问令牌"""
        try:
            # 使用传入的redirect_uri，如果没有则使用配置的
            if redirect_uri is None:
                redirect_uri = settings.auth0_redirect_uri
                
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "authorization_code",
                    "client_id": settings.auth0_client_id,
                    "client_secret": settings.auth0_client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri
                }
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    self.auth0_token_url,
                    json=data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ 获取Auth0 token成功!")
                    token_data = response.json()
                    print(f"Token数据: {token_data}")
                    return token_data
                else:
                    print(f"❌ 获取Auth0 token失败: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    print(f"请求数据: {data}")
                    print(f"Token URL: {self.auth0_token_url}")
                    print(f"重定向URI: {redirect_uri}")
                    return None
                    
        except Exception as e:
            print(f"获取Auth0 token异常: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """获取Auth0用户信息"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    self.auth0_userinfo_url,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ 获取用户信息成功: {user_data}")
                    return user_data
                else:
                    print(f"❌ 获取用户信息失败: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"获取Auth0用户信息异常: {e}")
            return None
    
    def get_or_create_user_by_auth0(self, user_info: Dict[str, Any]) -> Tuple[User, bool]:
        """根据Auth0用户信息获取或创建用户"""
        auth0_id = user_info.get("sub")  # Auth0用户ID
        email = user_info.get("email")
        name = user_info.get("name", "")
        nickname = user_info.get("nickname", "")
        picture = user_info.get("picture", "")
        
        if not auth0_id:
            raise ValueError("Auth0用户ID不能为空")
        
        # 查找现有用户
        user = self.db.query(User).filter(
            (User.email == email) | (User.auth0_id == auth0_id)
        ).first()
        
        is_new = False
        if not user:
            # 创建新用户
            from framework.schemas import UserCreate
            username = nickname or name or (email.split("@")[0] if email else f"auth0_{auth0_id}")
            user_data = UserCreate(
                username=username,
                email=email or f"{auth0_id}@auth0.local",
                password=""  # Auth0用户不需要密码
            )
            user = self.user_service.create_user(user_data)
            is_new = True
        
        # 更新Auth0信息
        user.auth0_id = auth0_id
        user.auth0_name = name or nickname
        user.auth0_picture = picture
        user.is_auth0_user = True
        
        # 如果用户没有设置用户名，使用Auth0用户名
        if not user.username or user.username.startswith("auth0_"):
            user.username = nickname or name or (email.split("@")[0] if email else f"auth0_{auth0_id}")
        
        # 更新邮箱（如果Auth0提供了邮箱）
        if email and email != f"{auth0_id}@auth0.local":
            user.email = email
        
        self.db.commit()
        return user, is_new
    
    async def handle_auth0_callback(self, code: str, state: str) -> Tuple[Optional[User], str]:
        """处理Auth0登录回调"""
        try:
            print(f"🔍 开始处理Auth0回调...")
            print(f"Code: {code}")
            print(f"State: {state}")
            
            # 获取access_token
            print(f"1️⃣ 获取access_token...")
            # 使用前端页面的redirect_uri，因为Auth0实际回调到了前端页面
            frontend_redirect_uri = "https://subpredicative-jerrica-subtepidly.ngrok-free.dev/google-login/success"
            token_info = await self.get_access_token(code, frontend_redirect_uri)
            if not token_info:
                print(f"❌ 获取access_token失败")
                return None, "获取access_token失败"
            
            access_token = token_info.get("access_token")
            if not access_token:
                print(f"❌ access_token为空")
                return None, "access_token为空"
            
            print(f"✅ access_token获取成功: {access_token[:20]}...")
            
            # 获取用户信息
            print(f"2️⃣ 获取用户信息...")
            user_info = await self.get_user_info(access_token)
            if not user_info:
                print(f"❌ 获取用户信息失败")
                return None, "获取用户信息失败"
            
            print(f"✅ 用户信息获取成功: {user_info}")
            
            # 获取或创建用户
            print(f"3️⃣ 获取或创建用户...")
            user, is_new = self.get_or_create_user_by_auth0(user_info)
            print(f"✅ 用户处理完成: ID={user.id}, 用户名={user.username}, 是否新用户={is_new}")
            
            return user, "success"
            
        except Exception as e:
            print(f"处理Auth0回调异常: {e}")
            return None, f"处理异常: {str(e)}"
    
    def get_auth0_login_status(self, state: str) -> Dict[str, Any]:
        """获取Auth0登录状态"""
        # 这里可以从Redis或数据库获取登录状态
        # 简化实现
        return {
            "status": "pending",
            "message": "等待授权"
        }
    
    def set_auth0_login_status(self, state: str, status: str, user_id: int = None, message: str = ""):
        """设置Auth0登录状态"""
        # 这里可以存储到Redis或数据库
        # 简化实现
        pass
