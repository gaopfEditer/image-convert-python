#!/usr/bin/env python3
"""
开发环境快速启动脚本
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
    print("🎯 图片转换服务 - 开发模式")
    print("=" * 50)
    print("📚 API文档地址:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc:      http://localhost:8000/redoc")
    print("=" * 50)
    print("💡 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 确保上传目录存在
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("uploads/uploads", exist_ok=True)
    os.makedirs("uploads/converted", exist_ok=True)
    os.makedirs("uploads/temp", exist_ok=True)
    
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
