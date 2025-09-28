-- 添加Google和Auth0登录相关字段到users表
-- 执行前请备份数据库

-- 添加Google登录相关字段
ALTER TABLE users 
ADD COLUMN google_id VARCHAR(100) NULL,
ADD COLUMN google_name VARCHAR(100) NULL,
ADD COLUMN google_picture VARCHAR(500) NULL,
ADD COLUMN is_google_user BOOLEAN DEFAULT FALSE;

-- 添加Auth0登录相关字段
ALTER TABLE users 
ADD COLUMN auth0_id VARCHAR(100) NULL,
ADD COLUMN auth0_name VARCHAR(100) NULL,
ADD COLUMN auth0_picture VARCHAR(500) NULL,
ADD COLUMN is_auth0_user BOOLEAN DEFAULT FALSE;

-- 添加索引以提高查询性能
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_auth0_id ON users(auth0_id);

-- 添加唯一约束
ALTER TABLE users ADD CONSTRAINT uk_users_google_id UNIQUE (google_id);
ALTER TABLE users ADD CONSTRAINT uk_users_auth0_id UNIQUE (auth0_id);

-- 显示表结构确认
DESCRIBE users;
