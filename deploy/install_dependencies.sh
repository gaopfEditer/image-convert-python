#!/bin/bash
# 安装系统依赖脚本

set -e

echo "🚀 开始安装系统依赖..."

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ 无法检测操作系统"
    exit 1
fi

echo "📋 检测到操作系统: $OS $VER"

# Ubuntu/Debian
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    echo "📦 更新包列表..."
    apt update
    
    echo "🔧 安装基础依赖..."
    apt install -y python3 python3-pip python3-venv python3-dev
    
    echo "🗄️ 安装MySQL..."
    apt install -y mysql-server
    
    echo "🔴 安装Redis..."
    apt install -y redis-server
    
    echo "🌐 安装Nginx..."
    apt install -y nginx
    
    echo "🛠️ 安装其他工具..."
    apt install -y git curl wget unzip htop

# CentOS/RHEL
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    echo "📦 更新包列表..."
    yum update -y
    
    echo "🔧 安装基础依赖..."
    yum install -y python3 python3-pip python3-devel
    
    echo "🗄️ 安装MySQL..."
    yum install -y mysql-server
    
    echo "🔴 安装Redis..."
    yum install -y redis
    
    echo "🌐 安装Nginx..."
    yum install -y nginx
    
    echo "🛠️ 安装其他工具..."
    yum install -y git curl wget unzip htop

else
    echo "❌ 不支持的操作系统: $OS"
    exit 1
fi

echo "✅ 系统依赖安装完成！"

# 启动服务
echo "🚀 启动服务..."
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    systemctl start mysql
    systemctl enable mysql
    systemctl start redis-server
    systemctl enable redis-server
    systemctl start nginx
    systemctl enable nginx
else
    systemctl start mysqld
    systemctl enable mysqld
    systemctl start redis
    systemctl enable redis
    systemctl start nginx
    systemctl enable nginx
fi

echo "✅ 服务启动完成！"
echo "🎉 系统依赖安装完成！"
