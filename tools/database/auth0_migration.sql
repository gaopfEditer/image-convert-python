-- Auth0登录相关字段迁移脚本
-- 为users表添加Auth0登录相关字段

-- 添加Auth0登录相关字段
ALTER TABLE users ADD COLUMN auth0_id VARCHAR(100) UNIQUE;
ALTER TABLE users ADD COLUMN auth0_name VARCHAR(100);
ALTER TABLE users ADD COLUMN auth0_picture VARCHAR(500);
ALTER TABLE users ADD COLUMN is_auth0_user BOOLEAN DEFAULT FALSE;

-- 添加索引
CREATE INDEX idx_users_auth0_id ON users(auth0_id);

-- 更新现有用户，确保新字段有默认值
UPDATE users SET is_auth0_user = FALSE WHERE is_auth0_user IS NULL;
