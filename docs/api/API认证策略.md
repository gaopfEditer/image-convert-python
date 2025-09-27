# 🔐 API认证策略说明

## 📋 认证策略概述

我们的API采用分层认证策略，将接口分为**公开接口**和**需要认证的接口**两类：

### 🌐 公开接口（不需要token）
这些接口可以直接访问，无需提供认证信息：

#### 图片处理相关
- `GET /api/image/formats` - 获取支持的图片格式
- `GET /api/image/info` - 获取图片信息
- `GET /api/image/preview/{filename}` - 预览图片
- `GET /api/image/download/{filename}` - 下载图片

#### 系统相关
- `GET /` - API根路径
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /redoc` - ReDoc文档

### 🔒 需要认证的接口（需要token）
这些接口需要提供有效的JWT token：

#### 用户认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取当前用户信息

#### 图片处理（需要用户身份）
- `POST /api/image/convert` - 转换图片格式
- `GET /api/image/usage` - 获取使用统计
- `GET /api/image/records` - 获取转换记录
- `DELETE /api/image/records/{id}` - 删除转换记录

#### 支付相关
- `POST /api/payment/create` - 创建支付订单
- `POST /api/payment/callback` - 支付回调
- `GET /api/payment/orders` - 获取支付订单

#### 微信登录
- `GET /api/auth/wechat/qrcode` - 获取微信登录二维码
- `GET /api/auth/wechat/callback` - 微信登录回调

## 🔑 如何获取和使用Token

### 1. 获取Token
```bash
# 登录获取token
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin666"}'

# 响应示例
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "SVIP"
    }
}
```

### 2. 使用Token
在需要认证的请求中添加Authorization头：

```bash
# 使用token访问需要认证的接口
curl -X POST "http://localhost:8000/api/image/convert" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -F "file=@image.jpg" \
     -F "target_format=PNG"
```

## 🎯 设计优势

### 1. 用户体验优化
- **公开接口**：用户可以直接获取格式列表、预览图片等，无需注册
- **认证接口**：需要用户身份的功能（如转换、记录管理）才需要登录

### 2. 安全性
- **分层保护**：敏感操作需要认证
- **权限控制**：不同用户角色有不同的使用限制
- **Token过期**：Token有30分钟过期时间，提高安全性

### 3. 开发友好
- **清晰分离**：公开和私有接口明确区分
- **灵活使用**：前端可以灵活选择哪些功能需要登录
- **易于测试**：公开接口可以直接测试

## 📱 前端集成建议

### 1. 公开功能
```javascript
// 获取支持的格式（无需token）
const formats = await fetch('/api/image/formats').then(r => r.json());

// 预览图片（无需token）
const imageUrl = `/api/image/preview/${filename}`;
```

### 2. 需要认证的功能
```javascript
// 登录获取token
const loginResponse = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});
const { access_token } = await loginResponse.json();

// 使用token进行图片转换
const formData = new FormData();
formData.append('file', file);
formData.append('target_format', 'PNG');

const convertResponse = await fetch('/api/image/convert', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${access_token}` },
    body: formData
});
```

## 🔧 配置说明

### Token配置
在 `config.py` 中可以调整token相关配置：

```python
# JWT配置
secret_key: str = "your-secret-key-here-change-in-production"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30  # Token过期时间（分钟）
```

### 权限配置
不同用户角色的使用限制：

```python
# 会员配置
free_user_daily_limit: int = 5      # 免费用户每日限制
vip_user_daily_limit: int = 100     # VIP用户每日限制
svip_user_daily_limit: int = 1000   # SVIP用户每日限制
```

## 🚀 使用示例

### 完整的图片处理流程

1. **获取支持格式**（无需登录）
```bash
curl -X GET "http://localhost:8000/api/image/formats"
```

2. **登录获取token**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin666"}'
```

3. **转换图片**（需要token）
```bash
curl -X POST "http://localhost:8000/api/image/convert" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@image.jpg" \
     -F "target_format=PNG"
```

4. **查看转换记录**（需要token）
```bash
curl -X GET "http://localhost:8000/api/image/records" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

这样的设计既保证了安全性，又提供了良好的用户体验！
