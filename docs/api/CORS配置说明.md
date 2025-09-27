# 🌐 CORS配置说明

## 📋 什么是CORS

CORS（Cross-Origin Resource Sharing，跨域资源共享）是一种安全机制，用于控制浏览器是否允许一个域名的网页访问另一个域名的资源。

## 🔧 当前CORS配置

### 允许的源（Origins）
```python
allow_origins=[
    "http://localhost:3000",  # React开发服务器
    "http://localhost:8080",  # Vue开发服务器
    "http://localhost:5173",  # Vite开发服务器
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080", 
    "http://127.0.0.1:5173",
    "http://localhost:8000",  # 同域
    "http://127.0.0.1:8000",
    "*"  # 开发环境允许所有来源
]
```

### 允许的HTTP方法
```python
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
```

### 允许的请求头
```python
allow_headers=[
    "Accept",
    "Accept-Language", 
    "Content-Language",
    "Content-Type",
    "Authorization",  # 重要：用于JWT token
    "X-Requested-With",
    "Origin",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
]
```

### 其他配置
- `allow_credentials=True` - 允许发送Cookie和认证信息
- `expose_headers=["*"]` - 暴露所有响应头给前端
- `max_age=3600` - 预检请求缓存1小时

## 🚀 前端使用示例

### 1. JavaScript Fetch API
```javascript
// 基础请求
const response = await fetch('http://localhost:8000/api/image/formats', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    }
});

// 带认证的请求
const response = await fetch('http://localhost:8000/api/image/convert', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data)
});
```

### 2. Axios
```javascript
import axios from 'axios';

// 创建axios实例
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    }
});

// 添加请求拦截器（自动添加token）
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 使用示例
const formats = await api.get('/image/formats');
const result = await api.post('/image/convert', formData);
```

### 3. React示例
```jsx
import React, { useState, useEffect } from 'react';

function ImageConverter() {
    const [formats, setFormats] = useState([]);
    const [token, setToken] = useState(null);

    // 登录
    const login = async (username, password) => {
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            localStorage.setItem('token', data.access_token);
        }
    };

    // 获取格式列表（无需认证）
    const loadFormats = async () => {
        const response = await fetch('http://localhost:8000/api/image/formats');
        const data = await response.json();
        setFormats(data);
    };

    // 转换图片（需要认证）
    const convertImage = async (file, targetFormat) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_format', targetFormat);

        const response = await fetch('http://localhost:8000/api/image/convert', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            // 处理转换后的图片
        }
    };

    useEffect(() => {
        loadFormats();
    }, []);

    return (
        <div>
            <h1>图片转换器</h1>
            <div>支持的格式: {formats.map(f => f.format).join(', ')}</div>
            {/* 其他UI组件 */}
        </div>
    );
}
```

## 🔧 常见问题解决

### 1. CORS错误
```
Access to fetch at 'http://localhost:8000/api/auth/login' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**解决方案**：
- 检查后端CORS配置
- 确保前端域名在 `allow_origins` 列表中
- 检查请求头是否包含在 `allow_headers` 中

### 2. 预检请求失败
```
Access to fetch at 'http://localhost:8000/api/image/convert' from origin 'http://localhost:3000' has been blocked by CORS policy: Response to preflight request doesn't pass access control check
```

**解决方案**：
- 确保 `OPTIONS` 方法在 `allow_methods` 中
- 检查 `max_age` 设置
- 确保服务器正确处理OPTIONS请求

### 3. 认证头被阻止
```
Request header field authorization is not allowed by Access-Control-Allow-Headers in preflight response
```

**解决方案**：
- 确保 `Authorization` 在 `allow_headers` 中
- 检查请求头格式：`Bearer <token>`

## 🛡️ 生产环境安全配置

### 开发环境（当前配置）
```python
allow_origins=["*"]  # 允许所有来源
```

### 生产环境（推荐）
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com"
]
```

## 📝 配置检查清单

- [ ] 前端域名在 `allow_origins` 中
- [ ] 使用的HTTP方法在 `allow_methods` 中
- [ ] 请求头在 `allow_headers` 中
- [ ] `allow_credentials=True` 如果发送Cookie
- [ ] 预检请求缓存时间合理
- [ ] 生产环境限制特定域名

## 🚀 测试CORS配置

### 使用浏览器开发者工具
1. 打开浏览器开发者工具
2. 切换到 Network 标签
3. 发送跨域请求
4. 查看请求和响应头

### 使用curl测试
```bash
# 测试预检请求
curl -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  http://localhost:8000/api/auth/login

# 测试实际请求
curl -X POST \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin666"}' \
  http://localhost:8000/api/auth/login
```

现在你的前端应该可以正常访问后端API了！🎉
