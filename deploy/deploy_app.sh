#!/bin/bash
# 应用部署脚本

set -e

echo "🚀 开始部署应用..."

# 设置变量
APP_DIR="/var/www/image-convert"
APP_USER="www-data"
SERVICE_NAME="image-convert"

# 创建应用目录
echo "📁 创建应用目录..."
mkdir -p $APP_DIR
cd $APP_DIR

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 设置文件权限
echo "🔐 设置文件权限..."
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR

# 创建上传目录
echo "📂 创建上传目录..."
mkdir -p $APP_DIR/uploads/converted
mkdir -p $APP_DIR/uploads/temp
mkdir -p $APP_DIR/uploads/uploads
chown -R $APP_USER:$APP_USER $APP_DIR/uploads

# 创建Gunicorn配置文件
echo "⚙️ 创建Gunicorn配置..."
cat > $APP_DIR/gunicorn.conf.py << EOF
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

# 创建日志目录
mkdir -p /var/log/gunicorn
chown -R $APP_USER:$APP_USER /var/log/gunicorn

# 创建系统服务文件
echo "🔧 创建系统服务..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Image Convert API
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --config $APP_DIR/gunicorn.conf.py simple_start:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 创建定时任务服务
echo "⏰ 创建定时任务服务..."
cat > /etc/systemd/system/$SERVICE_NAME-scheduler.service << EOF
[Unit]
Description=Image Convert Scheduler
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python tools/scheduler.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
echo "🔄 重新加载systemd..."
systemctl daemon-reload

# 启用服务
echo "✅ 启用服务..."
systemctl enable $SERVICE_NAME
systemctl enable $SERVICE_NAME-scheduler

echo "🎉 应用部署完成！"
echo "📋 下一步操作:"
echo "1. 运行: systemctl start $SERVICE_NAME"
echo "2. 运行: systemctl start $SERVICE_NAME-scheduler"
echo "3. 检查状态: systemctl status $SERVICE_NAME"
