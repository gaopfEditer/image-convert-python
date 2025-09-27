#!/bin/bash
# 使用远程数据库的部署脚本

set -e

echo "🚀 开始部署图片转换服务（使用远程数据库）..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 项目目录: $PROJECT_DIR"

# 检查config.py中的数据库配置
echo "🔍 检查数据库配置..."
if grep -q "1.94.137.69" $PROJECT_DIR/config.py; then
    echo "✅ 检测到远程数据库配置"
    DB_HOST=$(grep 'database_url' $PROJECT_DIR/config.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
    REDIS_HOST=$(grep 'redis_host' $PROJECT_DIR/config.py | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
    echo "   数据库地址: $DB_HOST"
    echo "   Redis地址: $REDIS_HOST"
else
    echo "❌ 未检测到远程数据库配置，请检查config.py"
    exit 1
fi

# 1. 安装系统依赖（跳过MySQL和Redis）
echo "📦 步骤1: 安装系统依赖..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt &> /dev/null; then
        # Ubuntu/Debian
        apt update
        apt install -y python3 python3-pip python3-venv python3-dev nginx git curl wget unzip htop
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum update -y
        yum install -y python3 python3-pip python3-devel nginx git curl wget unzip htop
    fi
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 2. 复制项目文件
echo "📂 步骤2: 复制项目文件..."
mkdir -p /var/www/image-convert
cp -r $PROJECT_DIR/* /var/www/image-convert/
chown -R www-data:www-data /var/www/image-convert

# 3. 创建虚拟环境
echo "🐍 步骤3: 创建Python虚拟环境..."
cd /var/www/image-convert
python3 -m venv venv
source venv/bin/activate

# 4. 安装Python依赖
echo "📦 步骤4: 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 5. 测试数据库连接
echo "🔍 步骤5: 测试数据库连接..."
python -c "
from tools.database.database import engine
try:
    with engine.connect() as conn:
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"

# 6. 初始化数据库
echo "🗄️ 步骤6: 初始化数据库..."
python init_db.py

# 7. 创建上传目录
echo "📂 步骤7: 创建上传目录..."
mkdir -p uploads/converted uploads/temp uploads/uploads
chown -R www-data:www-data uploads

# 8. 创建Gunicorn配置文件
echo "⚙️ 步骤8: 创建Gunicorn配置..."
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
pidfile = "/var/run/gunicorn.pid"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
EOF

# 9. 创建日志目录
mkdir -p /var/log/gunicorn
chown -R www-data:www-data /var/log/gunicorn

# 10. 创建系统服务文件
echo "🔧 步骤10: 创建系统服务..."
cat > /etc/systemd/system/image-convert.service << 'EOF'
[Unit]
Description=Image Convert API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/image-convert
Environment=PATH=/var/www/image-convert/venv/bin
ExecStart=/var/www/image-convert/venv/bin/gunicorn --config /var/www/image-convert/gunicorn.conf.py simple_start:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 11. 创建定时任务服务
echo "⏰ 步骤11: 创建定时任务服务..."
cat > /etc/systemd/system/image-convert-scheduler.service << 'EOF'
[Unit]
Description=Image Convert Scheduler
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/image-convert
Environment=PATH=/var/www/image-convert/venv/bin
ExecStart=/var/www/image-convert/venv/bin/python tools/scheduler.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 12. 配置Nginx
echo "🌐 步骤12: 配置Nginx..."
read -p "请输入域名 (例如: api.example.com): " DOMAIN

cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # 文件上传大小限制
    client_max_body_size 50M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # 静态文件
    location /static/ {
        alias /var/www/image-convert/uploads/converted/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /uploads/ {
        alias /var/www/image-convert/uploads/;
        expires 7d;
    }

    # API代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# 测试Nginx配置
nginx -t

# 13. 重新加载systemd
echo "🔄 步骤13: 重新加载systemd..."
systemctl daemon-reload

# 14. 启动服务
echo "🚀 步骤14: 启动服务..."
systemctl enable image-convert
systemctl enable image-convert-scheduler
systemctl start image-convert
systemctl start image-convert-scheduler
systemctl reload nginx

# 15. 配置防火墙
echo "🔥 步骤15: 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 22
    ufw allow 80
    ufw allow 443
    ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
fi

# 16. 检查服务状态
echo "🔍 步骤16: 检查服务状态..."
sleep 5

if systemctl is-active --quiet image-convert; then
    echo "✅ 主服务运行正常"
else
    echo "❌ 主服务启动失败"
    systemctl status image-convert
fi

if systemctl is-active --quiet image-convert-scheduler; then
    echo "✅ 定时任务服务运行正常"
else
    echo "❌ 定时任务服务启动失败"
    systemctl status image-convert-scheduler
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx运行正常"
else
    echo "❌ Nginx启动失败"
    systemctl status nginx
fi

# 17. 显示部署信息
echo ""
echo "🎉 部署完成！"
echo "================================"
echo "📋 服务信息:"
echo "  主服务: systemctl status image-convert"
echo "  定时任务: systemctl status image-convert-scheduler"
echo "  Nginx: systemctl status nginx"
echo ""
echo "📋 访问地址:"
echo "  本地访问: http://localhost"
echo "  域名访问: http://$DOMAIN"
echo "  API文档: http://$DOMAIN/docs"
echo "  健康检查: http://$DOMAIN/health"
echo ""
echo "📋 数据库信息:"
echo "  数据库地址: $DB_HOST:3306"
echo "  Redis地址: $REDIS_HOST:6379"
echo ""
echo "📋 常用命令:"
echo "  重启主服务: systemctl restart image-convert"
echo "  重启Nginx: systemctl restart nginx"
echo "  查看日志: journalctl -u image-convert -f"
echo ""
echo "📋 下一步操作:"
echo "1. 配置域名DNS解析: $DOMAIN -> 服务器IP"
echo "2. 申请SSL证书: certbot --nginx -d $DOMAIN"
echo "3. 测试API接口"
echo "================================"
