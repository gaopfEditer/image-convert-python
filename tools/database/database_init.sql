-- 图片转换服务数据库初始化脚本
-- 创建数据库
CREATE DATABASE image_convert_db;

-- 使用数据库
\c image_convert_db;

-- 创建用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    role VARCHAR(10) DEFAULT 'FREE' NOT NULL CHECK (role IN ('FREE', 'VIP', 'SVIP')),
    is_active BOOLEAN DEFAULT TRUE,
    -- 微信登录相关字段
    wechat_openid VARCHAR(100) UNIQUE,
    wechat_unionid VARCHAR(100),
    wechat_nickname VARCHAR(100),
    wechat_avatar VARCHAR(500),
    is_wechat_user BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建转换记录表
CREATE TABLE conversion_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    original_filename VARCHAR(255) NOT NULL,
    original_format VARCHAR(10) NOT NULL,
    target_format VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    conversion_time FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建支付记录表
CREATE TABLE payment_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_id VARCHAR(100) UNIQUE NOT NULL,
    amount FLOAT NOT NULL,
    payment_method VARCHAR(10) NOT NULL CHECK (payment_method IN ('alipay', 'wechat')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'cancelled')),
    transaction_id VARCHAR(100),
    target_role VARCHAR(10) NOT NULL CHECK (target_role IN ('FREE', 'VIP', 'SVIP')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建每日使用记录表
CREATE TABLE daily_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    usage_date TIMESTAMP WITH TIME ZONE NOT NULL,
    usage_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_wechat_openid ON users(wechat_openid);
CREATE INDEX idx_conversion_records_user_id ON conversion_records(user_id);
CREATE INDEX idx_conversion_records_created_at ON conversion_records(created_at);
CREATE INDEX idx_payment_records_user_id ON payment_records(user_id);
CREATE INDEX idx_payment_records_order_id ON payment_records(order_id);
CREATE INDEX idx_daily_usage_user_id ON daily_usage(user_id);
CREATE INDEX idx_daily_usage_date ON daily_usage(usage_date);

-- 插入测试数据
INSERT INTO users (username, email, hashed_password, role) VALUES 
('admin', 'admin@example.com', '$2b$12$gindbyUFbD4QixtPA7ywOu3mmjGPqJ4YRCtklyRtft4CODAN9wpK2', 'SVIP'),
('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2', 'FREE');

-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_records_updated_at BEFORE UPDATE ON payment_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_usage_updated_at BEFORE UPDATE ON daily_usage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
