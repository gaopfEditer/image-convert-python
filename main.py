"""
应用主入口 - 生产环境
包含定时任务调度器，用于清理数据库记录
"""
from framework.fastapi_app import create_app
from tools.scheduler import run_scheduler_in_background

# 创建应用
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # 启动定时任务调度器
    scheduler_thread = run_scheduler_in_background()
    
    print("🚀 启动图片转换服务（生产环境 + 定时任务）...")
    print("📅 定时任务：每天凌晨清理匿名记录，每周清理旧记录")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
