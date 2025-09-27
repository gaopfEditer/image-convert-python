#!/usr/bin/env python3
"""
带定时任务的启动脚本
"""
import uvicorn
import threading
from tools.scheduler import run_scheduler_in_background
from simple_start import app

if __name__ == "__main__":
    # 启动定时任务调度器
    scheduler_thread = run_scheduler_in_background()
    
    # 启动FastAPI应用
    print("🚀 启动图片转换服务（带定时任务）...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
