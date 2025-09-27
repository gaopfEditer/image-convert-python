#!/bin/bash
# 数据库设置脚本

set -e

echo "🗄️ 开始设置数据库..."

# 读取配置
read -p "请输入MySQL root密码: " MYSQL_ROOT_PASSWORD
read -p "请输入数据库名称 (默认: image_convert): " DB_NAME
read -p "请输入数据库用户名 (默认: image_user): " DB_USER
read -p "请输入数据库密码: " DB_PASSWORD

# 设置默认值
DB_NAME=${DB_NAME:-image_convert}
DB_USER=${DB_USER:-image_user}

echo "📋 数据库配置:"
echo "  数据库名: $DB_NAME"
echo "  用户名: $DB_USER"
echo "  密码: [已隐藏]"

# 创建数据库和用户
echo "🔧 创建数据库和用户..."
mysql -u root -p$MYSQL_ROOT_PASSWORD << EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "✅ 数据库创建完成！"

# 创建配置文件
echo "📝 创建数据库配置文件..."
cat > /var/www/image-convert/database_config.py << EOF
# 数据库配置
DATABASE_URL = "mysql+pymysql://$DB_USER:$DB_PASSWORD@localhost:3306/$DB_NAME"
EOF

echo "✅ 数据库配置完成！"
echo "🎉 数据库设置完成！"
