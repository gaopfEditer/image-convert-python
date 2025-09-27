-- 反馈留言模块和用户积分系统数据库迁移脚本

-- 1. 添加用户积分字段
ALTER TABLE users ADD COLUMN points INT DEFAULT 0 NOT NULL;
ALTER TABLE users ADD COLUMN last_checkin_date DATE NULL;
ALTER TABLE users ADD COLUMN consecutive_checkin_days INT DEFAULT 0 NOT NULL;
ALTER TABLE users ADD COLUMN total_checkin_days INT DEFAULT 0 NOT NULL;

-- 2. 创建反馈留言表
CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category ENUM('bug', 'feature', 'suggestion', 'complaint', 'other') DEFAULT 'other' NOT NULL,
    status ENUM('pending', 'processing', 'resolved', 'closed') DEFAULT 'pending' NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium' NOT NULL,
    admin_reply TEXT NULL,
    admin_reply_time TIMESTAMP NULL,
    admin_user_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 创建积分记录表
CREATE TABLE IF NOT EXISTS point_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points INT NOT NULL,
    type ENUM('earn', 'spend', 'expire', 'admin_adjust') NOT NULL,
    source ENUM('checkin', 'conversion', 'feedback', 'admin', 'exchange', 'other') NOT NULL,
    description VARCHAR(500) NOT NULL,
    related_id INT NULL, -- 关联的业务ID（如转换记录ID、反馈ID等）
    related_type VARCHAR(50) NULL, -- 关联的业务类型
    expires_at TIMESTAMP NULL, -- 积分过期时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_source (source),
    INDEX idx_created_at (created_at),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 创建签到记录表
CREATE TABLE IF NOT EXISTS checkin_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checkin_date DATE NOT NULL,
    points_earned INT NOT NULL,
    consecutive_days INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, checkin_date),
    INDEX idx_user_id (user_id),
    INDEX idx_checkin_date (checkin_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 创建积分规则配置表
CREATE TABLE IF NOT EXISTS point_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_type ENUM('checkin', 'conversion', 'feedback', 'other') NOT NULL,
    points INT NOT NULL,
    conditions JSON NULL, -- 规则条件（如连续签到天数要求）
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE NULL,
    end_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rule_type (rule_type),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 创建积分兑换表
CREATE TABLE IF NOT EXISTS point_exchanges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_name VARCHAR(200) NOT NULL,
    item_type ENUM('vip_upgrade', 'conversion_quota', 'feature_unlock', 'other') NOT NULL,
    points_cost INT NOT NULL,
    item_value VARCHAR(500) NULL, -- 兑换物品的具体值
    status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'pending' NOT NULL,
    admin_approve_user_id INT NULL,
    admin_approve_time TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_approve_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_item_type (item_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 插入默认积分规则
INSERT INTO point_rules (rule_name, rule_type, points, conditions, is_active) VALUES
('每日签到', 'checkin', 10, '{"daily": true}', TRUE),
('连续签到3天', 'checkin', 50, '{"consecutive_days": 3}', TRUE),
('连续签到7天', 'checkin', 150, '{"consecutive_days": 7}', TRUE),
('连续签到30天', 'checkin', 500, '{"consecutive_days": 30}', TRUE),
('图片转换', 'conversion', 5, '{"per_conversion": true}', TRUE),
('提交反馈', 'feedback', 20, '{"per_feedback": true}', TRUE),
('反馈被采纳', 'feedback', 100, '{"feedback_accepted": true}', TRUE);

-- 8. 创建积分统计视图
CREATE VIEW user_points_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.points as current_points,
    u.consecutive_checkin_days,
    u.total_checkin_days,
    u.last_checkin_date,
    COALESCE(earned.total_earned, 0) as total_earned_points,
    COALESCE(spent.total_spent, 0) as total_spent_points,
    COALESCE(expired.total_expired, 0) as total_expired_points
FROM users u
LEFT JOIN (
    SELECT user_id, SUM(points) as total_earned
    FROM point_records 
    WHERE type = 'earn'
    GROUP BY user_id
) earned ON u.id = earned.user_id
LEFT JOIN (
    SELECT user_id, SUM(ABS(points)) as total_spent
    FROM point_records 
    WHERE type = 'spend'
    GROUP BY user_id
) spent ON u.id = spent.user_id
LEFT JOIN (
    SELECT user_id, SUM(ABS(points)) as total_expired
    FROM point_records 
    WHERE type = 'expire'
    GROUP BY user_id
) expired ON u.id = expired.user_id;

-- 9. 创建反馈统计视图
CREATE VIEW feedback_summary AS
SELECT 
    f.id,
    f.user_id,
    u.username,
    f.title,
    f.category,
    f.status,
    f.priority,
    f.created_at,
    f.admin_reply_time,
    CASE 
        WHEN f.admin_reply IS NOT NULL THEN 'replied'
        WHEN f.status = 'resolved' THEN 'resolved'
        WHEN f.status = 'closed' THEN 'closed'
        ELSE 'pending'
    END as reply_status
FROM feedbacks f
JOIN users u ON f.user_id = u.id;

-- 10. 创建触发器：用户积分变化时更新积分记录
DELIMITER //
CREATE TRIGGER update_user_points_after_point_record
AFTER INSERT ON point_records
FOR EACH ROW
BEGIN
    UPDATE users 
    SET points = points + NEW.points
    WHERE id = NEW.user_id;
END //
DELIMITER ;

-- 11. 创建触发器：签到后更新用户签到信息
DELIMITER //
CREATE TRIGGER update_user_checkin_after_record
AFTER INSERT ON checkin_records
FOR EACH ROW
BEGIN
    UPDATE users 
    SET 
        last_checkin_date = NEW.checkin_date,
        consecutive_checkin_days = NEW.consecutive_days,
        total_checkin_days = total_checkin_days + 1
    WHERE id = NEW.user_id;
END //
DELIMITER ;

-- 12. 创建存储过程：处理用户签到
DELIMITER //
CREATE PROCEDURE ProcessUserCheckin(IN user_id INT, IN checkin_date DATE)
BEGIN
    DECLARE last_checkin DATE;
    DECLARE consecutive_days INT DEFAULT 1;
    DECLARE points_to_earn INT DEFAULT 10;
    DECLARE rule_points INT;
    DECLARE rule_conditions JSON;
    
    -- 检查是否已经签到过
    IF EXISTS (SELECT 1 FROM checkin_records WHERE user_id = user_id AND checkin_date = checkin_date) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '今天已经签到过了';
    END IF;
    
    -- 获取上次签到日期
    SELECT last_checkin_date INTO last_checkin FROM users WHERE id = user_id;
    
    -- 计算连续签到天数
    IF last_checkin IS NOT NULL AND last_checkin = DATE_SUB(checkin_date, INTERVAL 1 DAY) THEN
        SELECT consecutive_checkin_days + 1 INTO consecutive_days FROM users WHERE id = user_id;
    END IF;
    
    -- 计算应得积分
    SELECT points, conditions INTO rule_points, rule_conditions
    FROM point_rules 
    WHERE rule_type = 'checkin' 
    AND is_active = TRUE
    AND (conditions->>'$.consecutive_days' IS NULL OR JSON_EXTRACT(conditions, '$.consecutive_days') <= consecutive_days)
    ORDER BY JSON_EXTRACT(conditions, '$.consecutive_days') DESC
    LIMIT 1;
    
    IF rule_points IS NOT NULL THEN
        SET points_to_earn = rule_points;
    END IF;
    
    -- 插入签到记录
    INSERT INTO checkin_records (user_id, checkin_date, points_earned, consecutive_days)
    VALUES (user_id, checkin_date, points_to_earn, consecutive_days);
    
    -- 插入积分记录
    INSERT INTO point_records (user_id, points, type, source, description, related_type, related_id)
    VALUES (user_id, points_to_earn, 'earn', 'checkin', 
            CONCAT('连续签到', consecutive_days, '天'), 'checkin', LAST_INSERT_ID());
    
    -- 返回结果
    SELECT 
        consecutive_days as consecutive_days,
        points_to_earn as points_earned,
        (SELECT points FROM users WHERE id = user_id) as total_points;
END //
DELIMITER ;

-- 13. 创建存储过程：处理积分兑换
DELIMITER //
CREATE PROCEDURE ProcessPointExchange(
    IN user_id INT,
    IN item_name VARCHAR(200),
    IN item_type VARCHAR(50),
    IN points_cost INT,
    IN item_value VARCHAR(500)
)
BEGIN
    DECLARE current_points INT;
    
    -- 检查用户积分是否足够
    SELECT points INTO current_points FROM users WHERE id = user_id;
    
    IF current_points < points_cost THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '积分不足';
    END IF;
    
    -- 插入兑换记录
    INSERT INTO point_exchanges (user_id, item_name, item_type, points_cost, item_value)
    VALUES (user_id, item_name, item_type, points_cost, item_value);
    
    -- 扣除积分
    INSERT INTO point_records (user_id, points, type, source, description, related_type, related_id)
    VALUES (user_id, -points_cost, 'spend', 'exchange', 
            CONCAT('兑换', item_name), 'exchange', LAST_INSERT_ID());
    
    -- 返回结果
    SELECT 
        LAST_INSERT_ID() as exchange_id,
        (SELECT points FROM users WHERE id = user_id) as remaining_points;
END //
DELIMITER ;

-- 完成迁移
SELECT 'Feedback and Points system migration completed successfully!' as status;
