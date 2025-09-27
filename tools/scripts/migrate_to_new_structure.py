#!/usr/bin/env python3
"""
迁移现有代码到新架构
"""
import os
import shutil
from pathlib import Path

def migrate_existing_files():
    """迁移现有文件到新架构"""
    
    # 文件映射关系
    file_mappings = {
        # 配置文件
        "config.py": "config/settings.py",
        
        # 数据库相关
        "database.py": "infra/database/connection.py",
        "models.py": "infra/database/models.py",
        "schemas.py": "framework/schemas/common.py",
        
        # 认证相关
        "auth.py": "tool/crypto/jwt.py",
        "routers/auth.py": "framework/routes/auth.py",
        
        # 图片处理
        "routers/image.py": "framework/routes/image.py",
        "services/image_service.py": "business/image_conversion/service.py",
        "services/permission_service.py": "business/permission/service.py",
        
        # 支付相关
        "routers/payment.py": "framework/routes/payment.py",
        "services/payment_service.py": "business/payment/service.py",
        "services/wechat_pay_service.py": "business/payment/wechat_service.py",
        
        # 用户管理
        "services/user_service.py": "business/user_management/service.py",
        
        # 微信登录
        "routers/wechat_auth.py": "framework/routes/wechat.py",
        "services/wechat_auth_service.py": "business/user_management/wechat_service.py",
        
        # 缓存
        "redis_client.py": "infra/cache/redis_client.py",
        
        # 工具函数
        "init_db.py": "scripts/init_database.py",
        "dev_start.py": "scripts/dev_start.py",
    }
    
    # 创建备份目录
    backup_dir = "backup_old_structure"
    os.makedirs(backup_dir, exist_ok=True)
    
    print("🔄 开始迁移文件...")
    
    for old_path, new_path in file_mappings.items():
        if os.path.exists(old_path):
            # 创建新目录
            new_dir = os.path.dirname(new_path)
            os.makedirs(new_dir, exist_ok=True)
            
            # 复制文件
            shutil.copy2(old_path, new_path)
            print(f"✅ {old_path} → {new_path}")
            
            # 备份原文件
            backup_path = os.path.join(backup_dir, old_path)
            backup_dir_path = os.path.dirname(backup_path)
            os.makedirs(backup_dir_path, exist_ok=True)
            shutil.copy2(old_path, backup_path)
        else:
            print(f"⚠️  文件不存在: {old_path}")
    
    print("✅ 文件迁移完成")

def update_imports():
    """更新导入语句"""
    
    # 需要更新的文件列表
    files_to_update = [
        "framework/routes/auth.py",
        "framework/routes/image.py", 
        "framework/routes/payment.py",
        "framework/routes/wechat.py",
        "business/image_conversion/service.py",
        "business/user_management/service.py",
        "business/payment/service.py",
        "business/permission/service.py",
    ]
    
    # 导入映射
    import_mappings = {
        "from database import": "from infra.database.connection import",
        "from models import": "from infra.database.models import",
        "from schemas import": "from framework.schemas.common import",
        "from auth import": "from tool.crypto.jwt import",
        "from config import": "from config import",
        "from services.image_service import": "from business.image_conversion.service import",
        "from services.user_service import": "from business.user_management.service import",
        "from services.payment_service import": "from business.payment.service import",
        "from services.permission_service import": "from business.permission.service import",
    }
    
    print("🔄 更新导入语句...")
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新导入语句
            for old_import, new_import in import_mappings.items():
                content = content.replace(old_import, new_import)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 更新导入: {file_path}")
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print("✅ 导入语句更新完成")

def create_missing_files():
    """创建缺失的文件"""
    
    missing_files = {
        "framework/middleware/__init__.py": '''"""
中间件模块
"""''',
        
        "framework/middleware/auth.py": '''"""
认证中间件
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tool.crypto.jwt import verify_token
from business.user_management.service import UserService

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    
    # 这里需要从数据库获取用户信息
    # user = await user_service.get_user_by_id(user_id)
    # return user
    return {"id": user_id, "username": "admin"}
''',
        
        "framework/middleware/logging.py": '''"""
日志中间件
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
''',
        
        "infra/database/repositories/__init__.py": '''"""
数据访问层
"""''',
        
        "infra/cache/__init__.py": '''"""
缓存模块
"""''',
        
        "infra/cache/cache_service.py": '''"""
缓存服务
"""
from typing import Any, Optional
import json

class CacheService:
    """缓存服务"""
    
    def __init__(self):
        # 这里可以集成Redis或其他缓存
        self.cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """设置缓存"""
        self.cache[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def set_conversion_result(self, record_id: int, record: Any) -> bool:
        """设置转换结果缓存"""
        key = f"conversion_result:{record_id}"
        return await self.set(key, record, ttl=600)
'''
    }
    
    print("🔄 创建缺失文件...")
    
    for file_path, content in missing_files.items():
        # 创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 创建文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 创建文件: {file_path}")
    
    print("✅ 缺失文件创建完成")

def main():
    """主函数"""
    print("🚀 开始迁移到新架构...")
    
    # 1. 迁移现有文件
    migrate_existing_files()
    
    # 2. 创建缺失文件
    create_missing_files()
    
    # 3. 更新导入语句
    update_imports()
    
    print("🎉 架构迁移完成!")
    print("\n📋 下一步:")
    print("1. 检查迁移后的文件")
    print("2. 修复导入错误")
    print("3. 更新配置文件")
    print("4. 运行测试")

if __name__ == "__main__":
    main()
