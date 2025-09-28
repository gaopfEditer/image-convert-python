from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from tools.database.database import get_db
from schemas import Auth0LoginRequest, Auth0LoginResponse, Auth0LoginStatusResponse, Token, UserResponse, Auth0CallbackRequest
from services.auth0_service import Auth0Service
from auth import create_access_token
from config import settings

router = APIRouter(prefix="/auth/auth0", tags=["Auth0登录"])

@router.post("/login", response_model=Auth0LoginResponse, summary="发起Auth0登录")
async def auth0_login(
    request: Auth0LoginRequest,
    db: Session = Depends(get_db)
):
    """发起Auth0登录，返回登录URL"""
    auth0_service = Auth0Service(db)
    
    try:
        # 生成Auth0登录URL
        auth_url, state = auth0_service.generate_auth_url(request.state)
        
        return Auth0LoginResponse(
            auth_url=auth_url,
            state=state
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Auth0登录失败: {str(e)}"
        )

@router.get("/login", response_model=Auth0LoginResponse, summary="获取Auth0登录URL")
async def get_auth0_login_url(
    state: str = Query(None, description="状态参数"),
    db: Session = Depends(get_db)
):
    """获取Auth0登录URL"""
    auth0_service = Auth0Service(db)
    
    try:
        # 生成Auth0登录URL
        auth_url, state = auth0_service.generate_auth_url(state)
        
        return Auth0LoginResponse(
            auth_url=auth_url,
            state=state
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Auth0登录失败: {str(e)}"
        )

# 新增：前端调用此接口完成登录
@router.post("/complete-login", response_model=Auth0LoginResponse, summary="完成Auth0登录")
async def complete_auth0_login(
    request: Auth0CallbackRequest,
    db: Session = Depends(get_db)
):
    """前端调用此接口完成Auth0登录"""
    try:
        auth0_service = Auth0Service(db)
        
        # 处理Auth0回调
        user, message = await auth0_service.handle_auth0_callback(
            request.code, 
            request.state
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"登录失败: {message}"
            )
        
        # 生成JWT token
        access_token = create_access_token(data={"sub": user.username})
        
        # 构建响应
        return Auth0LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_auth0_user=user.is_auth0_user,
                auth0_name=user.auth0_name,
                auth0_picture=user.auth0_picture,
                created_at=user.created_at
            ),
            message="登录成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录处理失败: {str(e)}"
        )

@router.get("/callback", summary="Auth0登录回调")
async def auth0_callback(
    code: str = Query(..., description="授权码"),
    state: str = Query(..., description="状态参数"),
    db: Session = Depends(get_db)
):
    """Auth0登录回调处理"""
    auth0_service = Auth0Service(db)
    
    try:
        # 处理Auth0回调
        user, message = await auth0_service.handle_auth0_callback(code, state)
        
        if not user:
            # 登录失败，重定向到错误页面
            return RedirectResponse(
                url=f"/login?error={message}",
                status_code=302
            )
        
        # 生成JWT token
        access_token = create_access_token(data={"sub": user.username})
        
        # 重定向到前端页面，携带token和用户信息
        return RedirectResponse(
            url=f"/google-login/success?token={access_token}&user_id={user.id}&username={user.username}&email={user.email}&login_method=Auth0",
            status_code=302
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"/login?error=登录失败: {str(e)}",
            status_code=302
        )

@router.get("/status/{state}", response_model=Auth0LoginStatusResponse, summary="查询Auth0登录状态")
async def get_auth0_login_status(
    state: str,
    db: Session = Depends(get_db)
):
    """查询Auth0登录状态"""
    auth0_service = Auth0Service(db)
    
    try:
        status_info = auth0_service.get_auth0_login_status(state)
        return Auth0LoginStatusResponse(**status_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询登录状态失败: {str(e)}"
        )

@router.get("/login-page", response_class=HTMLResponse, summary="Auth0登录页面")
async def auth0_login_page():
    """Auth0登录页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>快速登录</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .login-container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 400px;
            }
            .auth0-btn {
                background-color: #eb5424;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin: 20px 0;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .auth0-btn:hover {
                background-color: #d4441f;
                transform: translateY(-2px);
            }
            .status {
                margin-top: 20px;
                padding: 10px;
                border-radius: 5px;
                display: none;
            }
            .status.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .features {
                text-align: left;
                margin: 20px 0;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            .features h3 {
                margin-top: 0;
                color: #333;
            }
            .features ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            .features li {
                margin: 5px 0;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🚀 快速登录</h2>
            <p>使用您的Google账号快速登录图片转换服务</p>
            
            <div class="features">
                <h3>✨ 登录优势</h3>
                <ul>
                    <li>支持Google账号登录</li>
                    <li>无需注册，一键登录</li>
                    <li>安全可靠，数据加密</li>
                    <li>全球通用，无地域限制</li>
                </ul>
            </div>
            
            <a href="#" class="auth0-btn" id="auth0LoginBtn">
                <span>🔐</span> 使用Google账号登录
            </a>
            <div class="status" id="status"></div>
        </div>
        
        <script>
            let currentState = null;
            
            async function loadAuth0Login() {
                try {
                    const response = await fetch('/api/auth/auth0/login');
                    const data = await response.json();
                    
                    currentState = data.state;
                    document.getElementById('auth0LoginBtn').href = data.auth_url;
                } catch (error) {
                    showStatus('加载登录失败: ' + error.message, 'error');
                }
            }
            
            function showStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = 'status ' + type;
                statusDiv.style.display = 'block';
            }
            
            // 页面加载时获取登录URL
            loadAuth0Login();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
