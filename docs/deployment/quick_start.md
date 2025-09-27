# 🚀 快速启动指南

## 1. 数据库配置

### 使用PostgreSQL（推荐）

1. **安装PostgreSQL**
   ```bash
   # Windows (使用Chocolatey)
   choco install postgresql
   
   # macOS (使用Homebrew)
   brew install postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **创建数据库**
   ```bash
   # 登录PostgreSQL
   psql -U postgres
   
   # 执行SQL脚本
   \i database_init.sql
   ```

3. **或者手动创建**
   ```sql
   -- 创建数据库
   CREATE DATABASE image_convert_db;
   
   -- 创建用户（可选）
   CREATE USER image_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE image_convert_db TO image_user;
   ```

### 使用SQLite（开发测试）

修改 `config.py` 中的数据库URL：
```python
database_url = "sqlite:///./image_convert.db"
```

## 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 3. 启动服务

### 方法一：使用快速启动脚本
```bash
python run_local.py
```

### 方法二：直接启动
```bash
python start.py
```

### 方法三：使用uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. 访问API文档

启动成功后，访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API根路径**: http://localhost:8000/

## 5. 测试API

### 注册用户
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com", 
       "password": "testpassword"
     }'
```

### 用户登录
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpassword"
```

### 获取支持的图片格式
```bash
curl -X GET "http://localhost:8000/api/image/formats"
```

## 6. 常见问题

### 数据库连接失败
- 检查PostgreSQL服务是否启动
- 确认数据库连接参数正确
- 检查防火墙设置

### 端口被占用
```bash
# 查看端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 修改端口
uvicorn main:app --port 8001
```

### 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 7. 开发模式

### 启用调试模式
在 `config.py` 中设置：
```python
debug = True
```

### 热重载
使用 `--reload` 参数启动，代码修改后自动重启：
```bash
uvicorn main:app --reload
```

### 查看日志
```bash
uvicorn main:app --log-level debug
```

## 8. 生产部署

### 使用Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 使用Docker
```bash
# 构建镜像
docker build -t image-convert-api .

# 运行容器
docker run -p 8000:8000 image-convert-api
```

## 9. 配置说明

### 环境变量
创建 `.env` 文件：
```env
DATABASE_URL=postgresql://username:password@localhost:5432/image_convert_db
SECRET_KEY=your-secret-key
ALIPAY_APP_ID=your-alipay-app-id
WECHAT_APP_ID=your-wechat-app-id
```

### 支付配置
- 支付宝：需要配置应用ID、私钥、公钥
- 微信支付：需要配置应用ID、商户号、API密钥

## 10. 监控和日志

### 健康检查
```bash
curl http://localhost:8000/health
```

### 查看API统计
访问 http://localhost:8000/docs 查看完整的API文档和测试界面。
