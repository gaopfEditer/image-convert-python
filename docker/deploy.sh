#!/bin/bash
# Docker部署脚本

set -e

echo "🐳 开始Docker部署图片转换服务..."

# 检查Docker和Docker Compose是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads/converted uploads/temp uploads/uploads
mkdir -p logs
mkdir -p mysql/init
mkdir -p ssl

# 设置权限
echo "🔐 设置文件权限..."
chmod -R 755 uploads
chmod -R 755 logs

# 创建MySQL初始化脚本
echo "🗄️ 创建MySQL初始化脚本..."
cat > mysql/init/01-init.sql << 'EOF'
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS image_convert CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'image_user'@'%' IDENTIFIED BY 'password123';

-- 授权
GRANT ALL PRIVILEGES ON image_convert.* TO 'image_user'@'%';
FLUSH PRIVILEGES;
EOF

# 创建环境变量文件
echo "⚙️ 创建环境变量文件..."
cat > .env << 'EOF'
# 数据库配置
MYSQL_ROOT_PASSWORD=rootpassword123
MYSQL_DATABASE=image_convert
MYSQL_USER=image_user
MYSQL_PASSWORD=password123

# Redis配置
REDIS_PASSWORD=

# 应用配置
DATABASE_URL=mysql+pymysql://image_user:password123@mysql:3306/image_convert
REDIS_URL=redis://redis:6379
EOF

# 构建和启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 初始化数据库
echo "🗄️ 初始化数据库..."
docker-compose exec app python init_db.py

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示日志
echo "📋 显示服务日志..."
docker-compose logs --tail=50

echo ""
echo "🎉 Docker部署完成！"
echo "================================"
echo "📋 服务信息:"
echo "  应用地址: http://localhost"
echo "  API文档: http://localhost/docs"
echo "  健康检查: http://localhost/health"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo "  进入容器: docker-compose exec app bash"
echo ""
echo "📋 数据持久化:"
echo "  数据库数据: ./mysql_data/"
echo "  Redis数据: ./redis_data/"
echo "  上传文件: ./uploads/"
echo "  日志文件: ./logs/"
echo "================================"
