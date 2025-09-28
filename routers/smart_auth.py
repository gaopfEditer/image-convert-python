from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from tools.database.database import get_db
from framework.schemas import SmartLoginResponse, WeChatLoginResponse, Auth0LoginResponse
from services.wechat_auth_service import WeChatAuthService
from services.auth0_service import Auth0Service
# GoogleAuthService已移除，使用Auth0Service替代
import httpx
import uuid

router = APIRouter(prefix="/auth/smart", tags=["智能登录"])

async def detect_ip_location(ip_address: str) -> dict:
    """检测IP地址的地理位置"""
    if not ip_address or ip_address == "无法获取":
        return {
            "country": "未知",
            "country_code": "XX",
            "region": "未知",
            "city": "未知",
            "is_china": False,
            "login_method": "auth0"
        }
    
    try:
        # 使用免费的IP地理位置API
        async with httpx.AsyncClient() as client:
            # 尝试使用ip-api.com (免费，无需API key)
            response = await client.get(
                f"http://ip-api.com/json/{ip_address}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否在中国
                is_china = data.get("countryCode") == "CN"
                
                return {
                    "country": data.get("country", "未知"),
                    "country_code": data.get("countryCode", "XX"),
                    "region": data.get("regionName", "未知"),
                    "city": data.get("city", "未知"),
                    "is_china": is_china,
                    "login_method": "wechat" if is_china else "auth0",
                    "timezone": data.get("timezone", ""),
                    "isp": data.get("isp", "")
                }
            else:
                # 如果API失败，使用备用方法
                return await detect_ip_location_fallback(ip_address)
                
    except Exception as e:
        print(f"IP地理位置检测失败: {e}")
        return await detect_ip_location_fallback(ip_address)

async def detect_ip_location_fallback(ip_address: str) -> dict:
    """备用IP地理位置检测方法"""
    try:
        # 使用ipinfo.io作为备用
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://ipinfo.io/{ip_address}/json",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                country_code = data.get("country", "XX")
                is_china = country_code == "CN"
                
                return {
                    "country": data.get("country", "未知"),
                    "country_code": country_code,
                    "region": data.get("region", "未知"),
                    "city": data.get("city", "未知"),
                    "is_china": is_china,
                    "login_method": "wechat" if is_china else "auth0",
                    "timezone": data.get("timezone", ""),
                    "org": data.get("org", "")
                }
    except Exception as e:
        print(f"备用IP检测也失败: {e}")
    
    # 如果所有方法都失败，返回默认值
    return {
        "country": "未知",
        "country_code": "XX",
        "region": "未知",
        "city": "未知",
        "is_china": False,
        "login_method": "auth0"
    }

@router.get("/login", response_model=SmartLoginResponse, summary="智能登录推荐")
async def smart_login(
    client_ip: str = Query(..., description="客户端IP地址"),
    host_id: str = Query(None, description="主机ID"),
    db: Session = Depends(get_db)
):
    """根据IP地址智能推荐登录方式"""
    try:
        # 检测IP地理位置
        location_info = await detect_ip_location(client_ip)
        
        # 生成登录URL
        wechat_login_url = None
        auth0_login_url = None
        
        if location_info["is_china"]:
            # 国内用户推荐微信登录
            wechat_service = WeChatAuthService(db)
            wechat_auth_url, wechat_state = wechat_service.generate_auth_url()
            wechat_login_url = wechat_auth_url
        else:
            # 国外用户推荐Auth0登录（支持Google等）
            auth0_service = Auth0Service(db)
            auth0_auth_url, auth0_state = auth0_service.generate_auth_url()
            auth0_login_url = auth0_auth_url
        
        # 生成所有登录方式的URL（让用户可以选择）
        if not wechat_login_url:
            wechat_service = WeChatAuthService(db)
            wechat_auth_url, wechat_state = wechat_service.generate_auth_url()
            wechat_login_url = wechat_auth_url
            
        if not auth0_login_url:
            auth0_service = Auth0Service(db)
            auth0_auth_url, auth0_state = auth0_service.generate_auth_url()
            auth0_login_url = auth0_auth_url
        
        # 更新推荐方法
        recommended_method = "wechat" if location_info["is_china"] else "auth0"
        location_info["login_method"] = recommended_method
        
        return SmartLoginResponse(
            recommended_method=recommended_method,
            location_info=location_info,
            wechat_login_url=wechat_login_url,
            auth0_login_url=auth0_login_url,
            message=f"检测到您来自{location_info['country']}，推荐使用{'微信' if location_info['is_china'] else 'Auth0(Google)'}登录"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能登录推荐失败: {str(e)}"
        )

@router.get("/login-page", response_class=HTMLResponse, summary="智能登录页面")
async def smart_login_page(
    client_ip: str = Query(..., description="客户端IP地址"),
    host_id: str = Query(None, description="主机ID")
):
    """智能登录页面"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能登录</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .login-container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
                width: 90%;
            }}
            .location-info {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #007bff;
            }}
            .login-options {{
                display: flex;
                gap: 20px;
                justify-content: center;
                margin: 30px 0;
                flex-wrap: wrap;
            }}
            .login-btn {{
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
                min-width: 150px;
            }}
            .wechat-btn {{
                background-color: #07c160;
                color: white;
            }}
            .wechat-btn:hover {{
                background-color: #06ad56;
                transform: translateY(-2px);
            }}
            .google-btn {{
                background-color: #4285f4;
                color: white;
            }}
            .google-btn:hover {{
                background-color: #357ae8;
                transform: translateY(-2px);
            }}
            .auth0-btn {{
                background-color: #eb5424;
                color: white;
            }}
            .auth0-btn:hover {{
                background-color: #d4441f;
                transform: translateY(-2px);
            }}
            .recommended {{
                border: 3px solid #ffc107;
                position: relative;
            }}
            .recommended::after {{
                content: "推荐";
                position: absolute;
                top: -10px;
                right: -10px;
                background-color: #ffc107;
                color: #000;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            .status {{
                margin-top: 20px;
                padding: 10px;
                border-radius: 5px;
                display: none;
            }}
            .status.success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .status.error {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .loading {{
                display: none;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🔐 智能登录</h2>
            <p>根据您的地理位置，我们为您推荐最适合的登录方式</p>
            
            <div class="loading" id="loading">
                <p>正在检测您的位置...</p>
            </div>
            
            <div id="loginContent" style="display: none;">
                <div class="location-info" id="locationInfo">
                    <p><strong>检测到您来自：</strong><span id="location"></span></p>
                    <p><strong>推荐登录方式：</strong><span id="recommendedMethod"></span></p>
                </div>
                
                <div class="login-options">
                    <a href="#" class="login-btn wechat-btn" id="wechatBtn">
                        <span>💬</span> 微信扫码登录
                    </a>
                    <a href="#" class="login-btn auth0-btn" id="auth0Btn">
                        <span>🔐</span> Auth0登录
                    </a>
                </div>
            </div>
            
            <div class="status" id="status"></div>
        </div>
        
        <script>
            let loginData = null;
            
            async function loadSmartLogin() {{
                try {{
                    document.getElementById('loading').style.display = 'block';
                    
                    const response = await fetch(`/api/auth/smart/login?client_ip={client_ip}&host_id={host_id}`);
                    const data = await response.json();
                    
                    loginData = data;
                    
                    // 显示位置信息
                    document.getElementById('location').textContent = 
                        `${data.location_info.country} ${data.location_info.region} ${data.location_info.city}`;
                    
                    let recommendedText = '微信扫码登录';
                    if (data.recommended_method === 'auth0') {{
                        recommendedText = 'Auth0登录';
                    }}
                    document.getElementById('recommendedMethod').textContent = recommendedText;
                    
                    // 设置登录按钮
                    document.getElementById('wechatBtn').href = data.wechat_login_url;
                    document.getElementById('auth0Btn').href = data.auth0_login_url;
                    
                    // 标记推荐方式
                    if (data.recommended_method === 'wechat') {{
                        document.getElementById('wechatBtn').classList.add('recommended');
                    }} else if (data.recommended_method === 'auth0') {{
                        document.getElementById('auth0Btn').classList.add('recommended');
                    }}
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('loginContent').style.display = 'block';
                    
                }} catch (error) {{
                    showStatus('加载登录选项失败: ' + error.message, 'error');
                    document.getElementById('loading').style.display = 'none';
                }}
            }}
            
            function showStatus(message, type) {{
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = 'status ' + type;
                statusDiv.style.display = 'block';
            }}
            
            // 页面加载时获取登录选项
            loadSmartLogin();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
