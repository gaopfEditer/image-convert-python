# 🔧 Auth0回调URL配置指南

## 📋 问题说明

当您看到 "Callback URL mismatch" 错误时，说明Auth0的回调URL配置不正确。需要配置两个URL：

1. **前端登录页面URL** - 用户点击登录按钮的页面
2. **后端回调API地址** - Auth0登录成功后重定向的地址

## 🛠️ 解决步骤

### 1. 登录Auth0控制台

1. 访问：https://manage.auth0.com/
2. 选择您的应用：图片转换服务
3. 进入 "Settings" 页面

### 2. 配置Allowed Callback URLs

在 "Allowed Callback URLs" 字段中添加以下URL：

```
https://bz.e.gaopf.top/api/auth/auth0/callback
```

**注意**：
- 确保URL完全匹配，包括协议（https）和路径
- 如果有多个环境，可以添加多个URL，用逗号分隔

### 3. 配置Allowed Web Origins（可选）

在 "Allowed Web Origins" 字段中添加：

```
https://bz.e.gaopf.top
```

### 4. 配置Allowed Logout URLs（可选）

在 "Allowed Logout URLs" 字段中添加：

```
https://bz.e.gaopf.top/login
```

## 🔗 URL说明

### 前端登录页面URL

| 页面 | URL | 用途 |
|------|-----|------|
| 智能登录页面 | `https://bz.e.gaopf.top/login` | 根据IP推荐登录方式 |
| Google登录页面 | `https://bz.e.gaopf.top/google-login` | 专门的Google登录页面 |
| 演示页面 | `https://bz.e.gaopf.top/demo` | 认证功能演示 |

### 后端回调API地址

| API | URL | 用途 |
|-----|-----|------|
| Auth0回调 | `https://bz.e.gaopf.top/api/auth/auth0/callback` | Auth0登录成功后回调 |
| Google回调 | `https://bz.e.gaopf.top/api/auth/google/callback` | Google直接登录回调 |
| 微信回调 | `https://bz.e.gaopf.top/api/auth/wechat/callback` | 微信登录回调 |

## 🔧 完整配置示例

### Auth0应用设置

```
Application Name: 图片转换服务
Application Type: Regular Web Application

Allowed Callback URLs:
https://bz.e.gaopf.top/api/auth/auth0/callback

Allowed Web Origins:
https://bz.e.gaopf.top

Allowed Logout URLs:
https://bz.e.gaopf.top/login
https://bz.e.gaopf.top/google-login
```

### 环境变量配置

```bash
# 生产环境
AUTH0_DOMAIN=gaopfediter.us.auth0.com
AUTH0_CLIENT_ID=5xzUKrmwx7bFlUb9nf7l3C0Xp0q8AqcN
AUTH0_CLIENT_SECRET=5VbXSpLULWdqS7n4dLZOQjvJmkw73otJ8KsMzTPgJPIpfCM8CxAVfU-36OQkEGET
AUTH0_REDIRECT_URI=https://bz.e.gaopf.top/api/auth/auth0/callback
```

## 🧪 测试步骤

### 1. 测试Auth0登录

1. 访问：`https://bz.e.gaopf.top/google-login`
2. 点击 "Auth0登录（推荐）" 按钮
3. 应该跳转到Auth0登录页面
4. 选择Google账号登录
5. 登录成功后应该重定向到：`https://bz.e.gaopf.top/login/success`

### 2. 测试Google直接登录

1. 访问：`https://bz.e.gaopf.top/google-login`
2. 点击 "Google直接登录" 按钮
3. 应该跳转到Google OAuth页面
4. 选择Google账号登录
5. 登录成功后应该重定向到：`https://bz.e.gaopf.top/login/success`

## 🐛 常见问题

### 1. Callback URL mismatch

**错误信息**：`Callback URL mismatch. The provided redirect_uri is not in the list of allowed callback URLs.`

**解决方案**：
- 检查Auth0控制台中的 "Allowed Callback URLs" 配置
- 确保URL完全匹配（包括协议、域名、路径）
- 确保没有多余的斜杠或空格

### 2. Invalid redirect_uri

**错误信息**：`Invalid redirect_uri`

**解决方案**：
- 检查配置文件中的 `auth0_redirect_uri` 设置
- 确保与Auth0控制台中的配置一致

### 3. 登录后页面空白

**可能原因**：
- 回调URL配置错误
- 后端服务未正常运行
- 网络连接问题

**解决方案**：
- 检查后端服务状态
- 查看浏览器控制台错误信息
- 检查网络连接

## 🔍 调试方法

### 1. 检查URL配置

```javascript
// 在浏览器控制台中检查当前URL
console.log('当前URL:', window.location.href);

// 检查Auth0配置
console.log('Auth0 Domain:', 'gaopfediter.us.auth0.com');
console.log('Client ID:', '5xzUKrmwx7bFlUb9nf7l3C0Xp0q8AqcN');
```

### 2. 检查网络请求

1. 打开浏览器开发者工具
2. 切换到 "Network" 标签
3. 点击登录按钮
4. 查看请求和响应

### 3. 检查Auth0日志

1. 登录Auth0控制台
2. 进入 "Monitoring" → "Logs"
3. 查看登录相关的日志

## 📞 技术支持

如果按照以上步骤仍然无法解决问题，请：

1. 提供完整的错误信息
2. 提供Auth0控制台配置截图
3. 提供浏览器控制台错误信息
4. 联系技术支持团队

## 🎯 最佳实践

1. **使用HTTPS**：生产环境必须使用HTTPS
2. **URL一致性**：确保所有URL配置完全一致
3. **环境分离**：开发、测试、生产环境使用不同的回调URL
4. **定期检查**：定期检查Auth0配置是否正确
5. **监控日志**：定期查看Auth0日志，及时发现问题
