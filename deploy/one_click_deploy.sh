#!/bin/bash
# 一键部署脚本

set -e

echo "🚀 开始一键部署图片转换服务..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 项目目录: $PROJECT_DIR"

# 1. 安装系统依赖
echo "📦 步骤1: 安装系统依赖..."
bash $SCRIPT_DIR/install_dependencies.sh

# 2. 检查数据库配置
echo "🗄️ 步骤2: 检查数据库配置..."
echo "ℹ️ 检测到config.py中已配置远程数据库，跳过本地数据库设置"
echo "   数据库地址: $(grep 'database_url' $PROJECT_DIR/config.py | head -1)"
echo "   Redis地址: $(grep 'redis_host' $PROJECT_DIR/config.py | head -1)"

# 3. 复制项目文件
echo "📂 步骤3: 复制项目文件..."
cp -r $PROJECT_DIR/* /var/www/image-convert/
chown -R www-data:www-data /var/www/image-convert

# 4. 部署应用
echo "🔧 步骤4: 部署应用..."
bash $SCRIPT_DIR/deploy_app.sh

# 5. 配置Nginx
echo "🌐 步骤5: 配置Nginx..."
bash $SCRIPT_DIR/setup_nginx.sh

# 6. 初始化数据库
echo "🗄️ 步骤6: 初始化数据库..."
cd /var/www/image-convert
source venv/bin/activate

# 检查数据库连接
echo "🔍 测试数据库连接..."
python -c "
from tools.database.database import engine
try:
    with engine.connect() as conn:
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"

# 初始化数据库表
echo "📋 初始化数据库表..."
python init_db.py

# 7. 启动服务
echo "🚀 步骤7: 启动服务..."
systemctl start image-convert
systemctl start image-convert-scheduler

# 8. 配置防火墙
echo "🔥 步骤8: 配置防火墙..."
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

# 9. 创建备份脚本
echo "💾 步骤9: 创建备份脚本..."
cat > /var/www/image-convert/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/image-convert"

mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u image_user -p image_convert > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/image-convert/uploads/

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
EOF

chmod +x /var/www/image-convert/backup.sh

# 10. 设置定时备份
echo "⏰ 步骤10: 设置定时备份..."
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/image-convert/backup.sh") | crontab -

# 11. 检查服务状态
echo "🔍 步骤11: 检查服务状态..."
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

# 12. 显示部署信息
echo ""
echo "🎉 部署完成！"
echo "================================"
echo "📋 服务信息:"
echo "  主服务: systemctl status image-convert"
echo "  定时任务: systemctl status image-convert-scheduler"
echo "  Nginx: systemctl status nginx"
echo ""
echo "📋 日志查看:"
echo "  主服务日志: journalctl -u image-convert -f"
echo "  定时任务日志: journalctl -u image-convert-scheduler -f"
echo "  Nginx日志: tail -f /var/log/nginx/access.log"
echo ""
echo "📋 常用命令:"
echo "  重启主服务: systemctl restart image-convert"
echo "  重启Nginx: systemctl restart nginx"
echo "  测试配置: nginx -t"
echo ""
echo "📋 下一步操作:"
echo "1. 配置域名DNS解析"
echo "2. 申请SSL证书: certbot --nginx -d your-domain.com"
echo "3. 测试API接口"
echo "================================"
