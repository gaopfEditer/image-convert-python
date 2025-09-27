#!/usr/bin/env python3
"""
定时任务调度器
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.database.database import get_db
from models import ConversionRecord
import threading

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_anonymous_records():
    """清理匿名用户的转换记录（user_id为空的记录）"""
    try:
        db = next(get_db())
        
        # 删除7天前的匿名记录
        cutoff_date = datetime.now() - timedelta(days=7)
        
        # 查询要删除的记录
        records_to_delete = db.query(ConversionRecord).filter(
            ConversionRecord.user_id.is_(None),
            ConversionRecord.created_at < cutoff_date
        ).all()
        
        if records_to_delete:
            # 删除记录
            for record in records_to_delete:
                db.delete(record)
            
            db.commit()
            logger.info(f"✅ 清理完成：删除了 {len(records_to_delete)} 条匿名用户转换记录")
        else:
            logger.info("ℹ️ 没有需要清理的匿名用户转换记录")
            
    except Exception as e:
        logger.error(f"❌ 清理匿名记录时出错: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

def cleanup_old_records():
    """清理所有超过30天的转换记录"""
    try:
        db = next(get_db())
        
        # 删除30天前的所有记录
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # 查询要删除的记录
        records_to_delete = db.query(ConversionRecord).filter(
            ConversionRecord.created_at < cutoff_date
        ).all()
        
        if records_to_delete:
            # 删除记录
            for record in records_to_delete:
                db.delete(record)
            
            db.commit()
            logger.info(f"✅ 清理完成：删除了 {len(records_to_delete)} 条超过30天的转换记录")
        else:
            logger.info("ℹ️ 没有需要清理的旧记录")
            
    except Exception as e:
        logger.error(f"❌ 清理旧记录时出错: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

def start_scheduler():
    """启动定时任务调度器"""
    logger.info("🚀 启动定时任务调度器")
    
    # 每天凌晨12点清理匿名记录
    schedule.every().day.at("00:00").do(cleanup_anonymous_records)
    
    # 每周日凌晨2点清理所有旧记录
    schedule.every().sunday.at("02:00").do(cleanup_old_records)
    
    # 运行调度器
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

def run_scheduler_in_background():
    """在后台线程中运行调度器"""
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("✅ 定时任务调度器已在后台启动")
    return scheduler_thread

if __name__ == "__main__":
    # 直接运行清理任务（用于测试）
    print("🧹 开始清理匿名用户转换记录...")
    cleanup_anonymous_records()
    
    print("🧹 开始清理旧记录...")
    cleanup_old_records()
    
    print("✅ 清理任务完成")
