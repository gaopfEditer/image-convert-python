from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from tools.database.database import get_db
from schemas import UserCreate, UserResponse, LoginResponse, MessageResponse
from services.user_service import UserService
from auth import authenticate_user, create_access_token, get_current_active_user
from models import User
from datetime import timedelta
from config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["认证"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册接口"""
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录接口 - 支持JSON格式，支持用户名或邮箱登录"""
    # 先查找用户 - 支持用户名或邮箱登录
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "USER_NOT_FOUND",
                "message": "用户不存在",
                "field": "username"
            }
        )
    
    # 验证密码
    from auth import verify_password
    password_valid = verify_password(login_data.password, user.hashed_password)
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PASSWORD",
                "message": "密码错误",
                "field": "password"
            }
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "is_active": user.is_active,
            "wechat_nickname": user.wechat_nickname,
            "wechat_avatar": user.wechat_avatar,
            "is_wechat_user": user.is_wechat_user,
            "google_name": user.google_name,
            "google_picture": user.google_picture,
            "is_google_user": user.is_google_user,
            "auth0_name": user.auth0_name,
            "auth0_picture": user.auth0_picture,
            "is_auth0_user": user.is_auth0_user,
            "created_at": user.created_at
        }
    }

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user

@router.post("/logout", response_model=MessageResponse, summary="用户登出")
async def logout():
    """用户登出接口"""
    return {"message": "登出成功", "success": True}
