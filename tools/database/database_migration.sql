-- 图片处理记录系统数据库迁移脚本
-- 扩展conversion_records表以支持详细记录和对比功能

-- 1. 添加原图信息字段
ALTER TABLE conversion_records ADD COLUMN original_file_path VARCHAR(500);
ALTER TABLE conversion_records ADD COLUMN original_file_size INTEGER;
ALTER TABLE conversion_records ADD COLUMN original_format VARCHAR(10);
ALTER TABLE conversion_records ADD COLUMN original_width INTEGER;
ALTER TABLE conversion_records ADD COLUMN original_height INTEGER;
ALTER TABLE conversion_records ADD COLUMN original_mode VARCHAR(20);

-- 2. 添加生成图信息字段
ALTER TABLE conversion_records ADD COLUMN converted_file_path VARCHAR(500);
ALTER TABLE conversion_records ADD COLUMN converted_file_size INTEGER;
ALTER TABLE conversion_records ADD COLUMN converted_width INTEGER;
ALTER TABLE conversion_records ADD COLUMN converted_height INTEGER;
ALTER TABLE conversion_records ADD COLUMN converted_mode VARCHAR(20);

-- 3. 添加处理参数字段
ALTER TABLE conversion_records ADD COLUMN quality INTEGER;
ALTER TABLE conversion_records ADD COLUMN resize_width INTEGER;
ALTER TABLE conversion_records ADD COLUMN resize_height INTEGER;
ALTER TABLE conversion_records ADD COLUMN watermark BOOLEAN DEFAULT FALSE;
ALTER TABLE conversion_records ADD COLUMN compression_ratio FLOAT;
ALTER TABLE conversion_records ADD COLUMN processing_params JSON;

-- 4. 创建图片详情表
CREATE TABLE IF NOT EXISTS image_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversion_record_id INT NOT NULL,
    image_type ENUM('original', 'converted') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    format VARCHAR(10) NOT NULL,
    mode VARCHAR(20) NOT NULL,
    color_space VARCHAR(20),
    dpi_x FLOAT,
    dpi_y FLOAT,
    has_transparency BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversion_record_id) REFERENCES conversion_records(id) ON DELETE CASCADE,
    INDEX idx_conversion_record_id (conversion_record_id),
    INDEX idx_image_type (image_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 创建缩略图缓存表
CREATE TABLE IF NOT EXISTS image_thumbnails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversion_record_id INT NOT NULL,
    image_type ENUM('original', 'converted') NOT NULL,
    thumbnail_size ENUM('thumbnail', 'medium', 'large') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversion_record_id) REFERENCES conversion_records(id) ON DELETE CASCADE,
    UNIQUE KEY unique_thumbnail (conversion_record_id, image_type, thumbnail_size),
    INDEX idx_conversion_record_id (conversion_record_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 创建用户图片统计表
CREATE TABLE IF NOT EXISTS user_image_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stat_date DATE NOT NULL,
    total_conversions INT DEFAULT 0,
    total_original_size BIGINT DEFAULT 0,
    total_converted_size BIGINT DEFAULT 0,
    total_compression_saved BIGINT DEFAULT 0,
    avg_compression_ratio FLOAT DEFAULT 0,
    most_used_format VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, stat_date),
    INDEX idx_user_id (user_id),
    INDEX idx_stat_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. 创建图片处理历史表（用于分析）
CREATE TABLE IF NOT EXISTS image_processing_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    conversion_record_id INT NOT NULL,
    processing_step VARCHAR(50) NOT NULL,
    step_duration FLOAT NOT NULL,
    memory_usage INT,
    cpu_usage FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversion_record_id) REFERENCES conversion_records(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_conversion_record_id (conversion_record_id),
    INDEX idx_processing_step (processing_step)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. 更新现有记录的原始格式字段
UPDATE conversion_records 
SET original_format = (
    CASE 
        WHEN original_filename LIKE '%.jpg' OR original_filename LIKE '%.jpeg' THEN 'JPEG'
        WHEN original_filename LIKE '%.png' THEN 'PNG'
        WHEN original_filename LIKE '%.gif' THEN 'GIF'
        WHEN original_filename LIKE '%.bmp' THEN 'BMP'
        WHEN original_filename LIKE '%.tiff' THEN 'TIFF'
        WHEN original_filename LIKE '%.webp' THEN 'WEBP'
        ELSE 'UNKNOWN'
    END
)
WHERE original_format IS NULL;

-- 9. 创建索引优化查询性能
CREATE INDEX idx_conversion_records_user_created ON conversion_records(user_id, created_at);
CREATE INDEX idx_conversion_records_target_format ON conversion_records(target_format);
CREATE INDEX idx_conversion_records_status ON conversion_records(status);
CREATE INDEX idx_conversion_records_compression_ratio ON conversion_records(compression_ratio);

-- 10. 创建视图用于快速查询
CREATE VIEW conversion_records_summary AS
SELECT 
    cr.id,
    cr.user_id,
    u.username,
    cr.original_filename,
    cr.original_format,
    cr.target_format,
    cr.original_file_size,
    cr.converted_file_size,
    cr.compression_ratio,
    cr.conversion_time,
    cr.status,
    cr.created_at,
    CASE 
        WHEN cr.compression_ratio > 50 THEN 'high'
        WHEN cr.compression_ratio > 20 THEN 'medium'
        ELSE 'low'
    END as compression_level
FROM conversion_records cr
JOIN users u ON cr.user_id = u.id;

-- 11. 创建存储过程用于清理过期文件
DELIMITER //
CREATE PROCEDURE CleanupExpiredFiles(IN days_old INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE file_path VARCHAR(500);
    DECLARE file_cursor CURSOR FOR 
        SELECT DISTINCT original_file_path FROM conversion_records 
        WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY)
        AND original_file_path IS NOT NULL
        UNION
        SELECT DISTINCT converted_file_path FROM conversion_records 
        WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY)
        AND converted_file_path IS NOT NULL;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN file_cursor;
    read_loop: LOOP
        FETCH file_cursor INTO file_path;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 这里可以添加文件删除逻辑
        -- 注意：实际删除文件需要外部脚本处理
        SELECT CONCAT('File to delete: ', file_path) as cleanup_info;
    END LOOP;
    CLOSE file_cursor;
END //
DELIMITER ;

-- 12. 创建触发器用于自动更新统计
DELIMITER //
CREATE TRIGGER update_user_image_stats_after_insert
AFTER INSERT ON conversion_records
FOR EACH ROW
BEGIN
    INSERT INTO user_image_stats (
        user_id, 
        stat_date, 
        total_conversions, 
        total_original_size, 
        total_converted_size,
        total_compression_saved,
        avg_compression_ratio,
        most_used_format
    ) VALUES (
        NEW.user_id,
        DATE(NEW.created_at),
        1,
        COALESCE(NEW.original_file_size, 0),
        COALESCE(NEW.converted_file_size, 0),
        COALESCE(NEW.original_file_size, 0) - COALESCE(NEW.converted_file_size, 0),
        COALESCE(NEW.compression_ratio, 0),
        NEW.target_format
    )
    ON DUPLICATE KEY UPDATE
        total_conversions = total_conversions + 1,
        total_original_size = total_original_size + COALESCE(NEW.original_file_size, 0),
        total_converted_size = total_converted_size + COALESCE(NEW.converted_file_size, 0),
        total_compression_saved = total_compression_saved + (COALESCE(NEW.original_file_size, 0) - COALESCE(NEW.converted_file_size, 0)),
        avg_compression_ratio = (avg_compression_ratio * total_conversions + COALESCE(NEW.compression_ratio, 0)) / (total_conversions + 1),
        most_used_format = (
            SELECT target_format 
            FROM conversion_records 
            WHERE user_id = NEW.user_id 
            AND DATE(created_at) = DATE(NEW.created_at)
            GROUP BY target_format 
            ORDER BY COUNT(*) DESC 
            LIMIT 1
        ),
        updated_at = CURRENT_TIMESTAMP;
END //
DELIMITER ;

-- 13. 插入示例数据（可选）
INSERT INTO conversion_records (
    user_id, original_filename, target_format, file_size, conversion_time, status,
    original_file_path, original_file_size, original_format, original_width, original_height, original_mode,
    converted_file_path, converted_file_size, converted_width, converted_height, converted_mode,
    quality, resize_width, resize_height, watermark, compression_ratio,
    processing_params
) VALUES (
    1, 'sample.png', 'JPEG', 45000, 1.2, 'success',
    '/uploads/sample.png', 120000, 'PNG', 800, 600, 'RGB',
    '/uploads/converted/sample_converted.jpg', 45000, 400, 300, 'RGB',
    95, 400, 300, true, 62.5,
    '{"target_format": "JPEG", "quality": 95, "resize": {"width": 400, "height": 300}, "watermark": true}'
);

-- 14. 创建清理脚本的存储过程
DELIMITER //
CREATE PROCEDURE CleanupOldRecords(IN days_old INT)
BEGIN
    -- 删除超过指定天数的记录
    DELETE FROM conversion_records 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY);
    
    -- 删除相关的图片详情记录
    DELETE FROM image_details 
    WHERE conversion_record_id NOT IN (SELECT id FROM conversion_records);
    
    -- 删除相关的缩略图记录
    DELETE FROM image_thumbnails 
    WHERE conversion_record_id NOT IN (SELECT id FROM conversion_records);
    
    SELECT ROW_COUNT() as deleted_records;
END //
DELIMITER ;

-- 完成迁移
SELECT 'Database migration completed successfully!' as status;
