#!/usr/bin/env python3
"""
图片转换服务启动脚本
"""
import uvicorn
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    print("🚀 启动图片转换服务...")
    print("📝 API文档地址: http://localhost:8000/docs")
    print("🔧 管理界面地址: http://localhost:8000/redoc")
    print("💡 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
