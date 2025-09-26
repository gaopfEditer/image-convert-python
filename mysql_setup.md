# 🗄️ MySQL数据库配置指南

## 📋 安装MySQL

### Windows
1. 下载MySQL安装包：https://dev.mysql.com/downloads/mysql/
2. 运行安装程序，选择"Developer Default"
3. 设置root密码
4. 启动MySQL服务

### macOS
```bash
# 使用Homebrew安装
brew install mysql

# 启动MySQL服务
brew services start mysql

# 设置root密码
mysql_secure_installation
```

### Ubuntu/Debian
```bash
# 安装MySQL
sudo apt update
sudo apt install mysql-server

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 设置root密码
sudo mysql_secure_installation
```

## 🔧 配置数据库

### 1. 登录MySQL
```bash
mysql -u root -p
```

### 2. 创建数据库和用户
```sql
-- 创建数据库
CREATE DATABASE image_convert_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'image_user'@'localhost' IDENTIFIED BY 'image_password';
GRANT ALL PRIVILEGES ON image_convert_db.* TO 'image_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

### 3. 执行初始化脚本
```bash
# 方法一：使用mysql命令行
mysql -u root -p < database_init_mysql.sql

# 方法二：使用Python脚本
python init_db.py
```

## ⚙️ 修改配置文件

### 1. 修改数据库连接
编辑 `config.py`：
```python
# 使用root用户
database_url = "mysql+pymysql://root:your_password@localhost:3306/image_convert_db"

# 或使用专用用户
database_url = "mysql+pymysql://image_user:image_password@localhost:3306/image_convert_db"
```

### 2. 环境变量配置
创建 `.env` 文件：
```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/image_convert_db
SECRET_KEY=your-secret-key
```

## 🚀 启动服务

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_db.py
```

### 3. 启动服务
```bash
python dev_start.py
```

## 🔍 验证安装

### 1. 检查数据库连接
```python
from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.database_url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT VERSION()"))
    print(f"MySQL版本: {result.scalar()}")
```

### 2. 检查表结构
```sql
USE image_convert_db;
SHOW TABLES;
DESCRIBE users;
```

### 3. 测试API
访问 http://localhost:8000/docs 查看API文档

## 🐛 常见问题

### 1. 连接被拒绝
```bash
# 检查MySQL服务状态
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# 启动MySQL服务
sudo systemctl start mysql  # Linux
brew services start mysql  # macOS
```

### 2. 认证失败
```sql
-- 重置root密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

### 3. 字符集问题
```sql
-- 检查数据库字符集
SHOW CREATE DATABASE image_convert_db;

-- 修改字符集
ALTER DATABASE image_convert_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 权限问题
```sql
-- 授予权限
GRANT ALL PRIVILEGES ON image_convert_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

## 📊 性能优化

### 1. 配置MySQL
编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：
```ini
[mysqld]
# 基本配置
max_connections = 200
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M

# 字符集配置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 查询缓存
query_cache_type = 1
query_cache_size = 32M
```

### 2. 重启MySQL服务
```bash
sudo systemctl restart mysql  # Linux
brew services restart mysql  # macOS
```

## 🔒 安全建议

### 1. 创建专用用户
```sql
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON image_convert_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. 限制root访问
```sql
-- 禁用root远程登录
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
FLUSH PRIVILEGES;
```

### 3. 启用SSL（可选）
```sql
-- 检查SSL状态
SHOW VARIABLES LIKE 'have_ssl';
```

## 📝 备份和恢复

### 备份数据库
```bash
mysqldump -u root -p image_convert_db > backup.sql
```

### 恢复数据库
```bash
mysql -u root -p image_convert_db < backup.sql
```

## 🎯 下一步

1. 确保MySQL服务正在运行
2. 执行数据库初始化脚本
3. 修改配置文件中的数据库连接
4. 启动图片转换服务
5. 访问 http://localhost:8000/docs 测试API
