-- Google登录相关字段迁移脚本
-- 为users表添加Google登录相关字段

-- 添加Google登录相关字段
ALTER TABLE users ADD COLUMN google_id VARCHAR(100) UNIQUE;
ALTER TABLE users ADD COLUMN google_name VARCHAR(100);
ALTER TABLE users ADD COLUMN google_picture VARCHAR(500);
ALTER TABLE users ADD COLUMN is_google_user BOOLEAN DEFAULT FALSE;

-- 添加索引
CREATE INDEX idx_users_google_id ON users(google_id);

-- 更新现有用户，确保新字段有默认值
UPDATE users SET is_google_user = FALSE WHERE is_google_user IS NULL;
