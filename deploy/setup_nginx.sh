#!/bin/bash
# Nginx配置脚本

set -e

echo "🌐 开始配置Nginx..."

# 读取配置
read -p "请输入域名 (例如: api.example.com): " DOMAIN
read -p "请输入应用端口 (默认: 8000): " APP_PORT
APP_PORT=${APP_PORT:-8000}

echo "📋 Nginx配置:"
echo "  域名: $DOMAIN"
echo "  应用端口: $APP_PORT"

# 创建Nginx配置文件
echo "📝 创建Nginx配置文件..."
cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # 文件上传大小限制
    client_max_body_size 50M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # 静态文件
    location /static/ {
        alias /var/www/image-convert/uploads/converted/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # 安全设置
        location ~* \.(php|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }

    # 上传文件
    location /uploads/ {
        alias /var/www/image-convert/uploads/;
        expires 7d;
        
        # 安全设置
        location ~* \.(php|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }

    # API代理
    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # 禁止访问敏感文件
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|log|ini)$ {
        deny all;
    }
}
EOF

# 启用站点
echo "🔗 启用站点..."
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# 删除默认站点
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# 测试配置
echo "🧪 测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx配置测试通过！"
    
    # 重新加载Nginx
    echo "🔄 重新加载Nginx..."
    systemctl reload nginx
    
    echo "🎉 Nginx配置完成！"
    echo "📋 下一步操作:"
    echo "1. 配置DNS解析: $DOMAIN -> 服务器IP"
    echo "2. 申请SSL证书: certbot --nginx -d $DOMAIN"
    echo "3. 测试访问: http://$DOMAIN/health"
else
    echo "❌ Nginx配置测试失败！"
    exit 1
fi
