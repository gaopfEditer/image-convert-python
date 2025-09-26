from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import WeChatLoginRequest, WeChatLoginResponse, WeChatLoginStatusResponse, Token, UserResponse
from services.wechat_auth_service import WeChatAuthService
from auth import create_access_token
from config import settings
import qrcode
import io
import base64

router = APIRouter(prefix="/auth/wechat", tags=["微信登录"])

@router.post("/login", response_model=WeChatLoginResponse, summary="发起微信扫码登录")
async def wechat_login(
    request: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """发起微信扫码登录，返回登录URL和二维码"""
    wechat_service = WeChatAuthService(db)
    
    try:
        # 生成微信登录URL
        auth_url, state = wechat_service.generate_auth_url(request.state)
        
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(auth_url)
        qr.make(fit=True)
        
        # 创建二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return WeChatLoginResponse(
            auth_url=auth_url,
            state=state,
            qr_code=f"data:image/png;base64,{img_str}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成微信登录失败: {str(e)}"
        )

@router.get("/login", response_model=WeChatLoginResponse, summary="获取微信登录二维码")
async def get_wechat_qr(
    state: str = Query(None, description="状态参数"),
    db: Session = Depends(get_db)
):
    """获取微信登录二维码"""
    wechat_service = WeChatAuthService(db)
    
    try:
        # 生成微信登录URL
        auth_url, state = wechat_service.generate_auth_url(state)
        
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(auth_url)
        qr.make(fit=True)
        
        # 创建二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return WeChatLoginResponse(
            auth_url=auth_url,
            state=state,
            qr_code=f"data:image/png;base64,{img_str}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成微信登录失败: {str(e)}"
        )

@router.get("/callback", summary="微信登录回调")
async def wechat_callback(
    code: str = Query(..., description="授权码"),
    state: str = Query(..., description="状态参数"),
    db: Session = Depends(get_db)
):
    """微信登录回调处理"""
    wechat_service = WeChatAuthService(db)
    
    try:
        # 处理微信回调
        user, message = await wechat_service.handle_wechat_callback(code, state)
        
        if not user:
            # 登录失败，重定向到错误页面
            return RedirectResponse(
                url=f"/login?error={message}",
                status_code=302
            )
        
        # 生成JWT token
        access_token = create_access_token(data={"sub": user.username})
        
        # 重定向到前端页面，携带token
        return RedirectResponse(
            url=f"/login/success?token={access_token}&user_id={user.id}",
            status_code=302
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"/login?error=登录失败: {str(e)}",
            status_code=302
        )

@router.get("/status/{state}", response_model=WeChatLoginStatusResponse, summary="查询微信登录状态")
async def get_wechat_login_status(
    state: str,
    db: Session = Depends(get_db)
):
    """查询微信登录状态"""
    wechat_service = WeChatAuthService(db)
    
    try:
        status_info = wechat_service.get_wechat_login_status(state)
        return WeChatLoginStatusResponse(**status_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询登录状态失败: {str(e)}"
        )

@router.get("/login-page", response_class=HTMLResponse, summary="微信登录页面")
async def wechat_login_page():
    """微信登录页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>微信扫码登录</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }
            .login-container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }
            .qr-code {
                margin: 20px 0;
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
            .refresh-btn {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>微信扫码登录</h2>
            <div class="qr-code" id="qrCode">
                <p>正在生成二维码...</p>
            </div>
            <div class="status" id="status"></div>
            <button class="refresh-btn" onclick="refreshQR()">刷新二维码</button>
        </div>
        
        <script>
            let currentState = null;
            let checkInterval = null;
            
            async function loadQRCode() {
                try {
                    const response = await fetch('/api/auth/wechat/login');
                    const data = await response.json();
                    
                    currentState = data.state;
                    document.getElementById('qrCode').innerHTML = 
                        `<img src="${data.qr_code}" alt="微信登录二维码" style="max-width: 200px;">`;
                    
                    // 开始轮询登录状态
                    startStatusCheck();
                } catch (error) {
                    showStatus('加载二维码失败: ' + error.message, 'error');
                }
            }
            
            function startStatusCheck() {
                if (checkInterval) clearInterval(checkInterval);
                
                checkInterval = setInterval(async () => {
                    try {
                        const response = await fetch(`/api/auth/wechat/status/${currentState}`);
                        const data = await response.json();
                        
                        if (data.status === 'success') {
                            showStatus('登录成功！正在跳转...', 'success');
                            clearInterval(checkInterval);
                            
                            // 跳转到成功页面
                            setTimeout(() => {
                                window.location.href = '/login/success?user_id=' + data.user.id;
                            }, 2000);
                        } else if (data.status === 'failed') {
                            showStatus(data.message, 'error');
                            clearInterval(checkInterval);
                        }
                    } catch (error) {
                        console.error('检查登录状态失败:', error);
                    }
                }, 2000);
            }
            
            function showStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = 'status ' + type;
                statusDiv.style.display = 'block';
            }
            
            function refreshQR() {
                loadQRCode();
            }
            
            // 页面加载时生成二维码
            loadQRCode();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/success", response_class=HTMLResponse, summary="登录成功页面")
async def login_success(
    token: str = Query(..., description="访问令牌"),
    user_id: int = Query(..., description="用户ID")
):
    """登录成功页面"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>登录成功</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }}
            .success-container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }}
            .success-icon {{
                font-size: 48px;
                color: #28a745;
                margin-bottom: 20px;
            }}
            .token-info {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                word-break: break-all;
                font-family: monospace;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="success-container">
            <div class="success-icon">✓</div>
            <h2>登录成功！</h2>
            <p>欢迎使用图片转换服务</p>
            <div class="token-info">
                <strong>访问令牌:</strong><br>
                {token}
            </div>
            <p>请保存此令牌用于API调用</p>
            <button onclick="window.close()">关闭窗口</button>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
