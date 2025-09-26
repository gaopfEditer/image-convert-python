# 图片转换服务 API

一个基于 FastAPI 的图片格式转换服务，支持多种图片格式转换，包含完整的会员系统和支付功能。

## 功能特性

### 🖼️ 图片转换
- 支持多种图片格式：JPEG、PNG、WebP、BMP、TIFF、GIF
- 高质量图片转换
- 图片大小调整
- 水印添加功能
- 批量转换（VIP功能）

### 👥 用户系统
- 用户注册/登录
- JWT 身份验证
- 用户信息管理
- 密码加密存储

### 💎 会员系统
- 免费用户：每日5次转换
- VIP会员：每日100次转换，更多功能
- SVIP会员：每日1000次转换，全部功能
- 会员权益管理

### 💳 支付系统
- 支付宝支付集成
- 微信支付集成
- 支付回调处理
- 订单管理

### 🔒 权限管理
- 基于角色的访问控制
- 使用次数限制
- 功能权限控制

## 技术栈

- **后端框架**: FastAPI
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **认证**: JWT + OAuth2
- **图片处理**: Pillow
- **支付**: 支付宝SDK + 微信支付SDK
- **数据库迁移**: Alembic

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制配置文件并修改：

```bash
cp config.py config_local.py
```

修改 `config_local.py` 中的数据库连接和其他配置。

### 3. 初始化数据库

```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
python start.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/me` - 更新用户信息

### 图片转换接口
- `GET /api/image/formats` - 获取支持的图片格式
- `POST /api/image/convert` - 转换图片格式
- `POST /api/image/info` - 获取图片信息
- `GET /api/image/usage` - 获取使用统计
- `GET /api/image/records` - 获取转换记录

### 支付接口
- `POST /api/payment/create` - 创建支付订单
- `POST /api/payment/alipay/create` - 创建支付宝支付
- `POST /api/payment/wechat/create` - 创建微信支付
- `POST /api/payment/alipay/callback` - 支付宝支付回调
- `POST /api/payment/wechat/callback` - 微信支付回调
- `GET /api/payment/orders` - 获取支付记录
- `GET /api/payment/upgrade-options` - 获取升级选项
- `GET /api/payment/role-benefits` - 获取角色权益

## 配置说明

### 数据库配置
```python
database_url = "postgresql://username:password@localhost:5432/image_convert_db"
```

### 支付配置
需要配置支付宝和微信支付的相关参数：

```python
# 支付宝配置
alipay_app_id = "your-alipay-app-id"
alipay_private_key = "your-alipay-private-key"
alipay_public_key = "alipay-public-key"

# 微信支付配置
wechat_app_id = "your-wechat-app-id"
wechat_mch_id = "your-wechat-mch-id"
wechat_api_key = "your-wechat-api-key"
```

### 文件存储配置
```python
upload_dir = "uploads"  # 上传文件目录
max_file_size = 10485760  # 最大文件大小（10MB）
allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]
```

## 会员等级说明

### 免费用户 (FREE)
- 每日5次免费转换
- 基础图片格式转换
- 标准转换质量

### VIP会员
- 每日100次转换
- 高质量图片转换
- 批量转换功能
- 去除水印
- 优先处理队列

### SVIP会员
- 每日1000次转换
- 最高质量图片转换
- 无限制批量转换
- API接口访问
- 自定义水印
- 24/7技术支持

## 部署说明

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "start.py"]
```

### 生产环境配置

1. 修改数据库连接为生产环境
2. 配置正确的支付参数
3. 设置安全的JWT密钥
4. 配置HTTPS
5. 设置适当的CORS策略

## 开发说明

### 项目结构
```
image-convert-python/
├── alembic/                 # 数据库迁移
├── routers/                 # API路由
│   ├── auth.py             # 认证路由
│   ├── image.py            # 图片转换路由
│   └── payment.py          # 支付路由
├── services/               # 业务逻辑服务
│   ├── user_service.py     # 用户服务
│   ├── image_service.py    # 图片转换服务
│   ├── payment_service.py  # 支付服务
│   └── permission_service.py # 权限服务
├── models.py               # 数据库模型
├── schemas.py              # Pydantic模型
├── auth.py                 # 认证相关
├── database.py             # 数据库配置
├── config.py               # 配置文件
├── main.py                 # 主应用
└── start.py                # 启动脚本
```

### 添加新功能

1. 在 `models.py` 中定义数据库模型
2. 在 `schemas.py` 中定义API模型
3. 在 `services/` 中实现业务逻辑
4. 在 `routers/` 中创建API路由
5. 在 `main.py` 中注册路由

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过以下方式联系：

- 邮箱: your-email@example.com
- GitHub: https://github.com/your-username/image-convert-python
