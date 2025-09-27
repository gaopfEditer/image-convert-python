#!/usr/bin/env python3
"""
项目结构重组脚本
将文档、测试、工具文件移动到对应目录
"""
import os
import shutil
from pathlib import Path

def create_directories():
    """创建必要的目录结构"""
    directories = [
        "docs",
        "docs/api",
        "docs/architecture", 
        "docs/deployment",
        "docs/features",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "tools",
        "tools/database",
        "tools/cache",
        "tools/scripts"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # 创建__init__.py文件
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('"""\n{}模块\n"""\n'.format(directory.replace('/', '.')))
    
    print("✅ 目录结构创建完成")

def move_documentation_files():
    """移动文档文件到docs目录"""
    print("📚 移动文档文件...")
    
    # 文档文件映射
    doc_files = {
        # 移动到docs/features/
        "项目架构重构方案.md": "docs/architecture/项目架构重构方案.md",
        "反馈留言和积分系统说明.md": "docs/features/反馈留言和积分系统说明.md",
        "图片处理记录系统设计.md": "docs/features/图片处理记录系统设计.md",
        "增强图片处理系统说明.md": "docs/features/增强图片处理系统说明.md",
        "README_新架构.md": "docs/architecture/README_新架构.md",
        
        # 移动到docs/deployment/
        "mysql_setup.md": "docs/deployment/mysql_setup.md",
        "远程服务器配置.md": "docs/deployment/远程服务器配置.md",
        "微信支付配置说明.md": "docs/deployment/微信支付配置说明.md",
        "微信登录配置说明.md": "docs/deployment/微信登录配置说明.md",
        "项目说明.md": "docs/architecture/项目说明.md",
        "quick_start.md": "docs/deployment/quick_start.md"
    }
    
    for old_path, new_path in doc_files.items():
        if os.path.exists(old_path):
            # 创建目标目录
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # 移动文件
            shutil.move(old_path, new_path)
            print(f"✅ {old_path} → {new_path}")
        else:
            print(f"⚠️  文件不存在: {old_path}")

def move_test_files():
    """移动测试文件到tests目录"""
    print("🧪 移动测试文件...")
    
    # 测试文件映射
    test_files = {
        # 移动到tests/integration/
        "test_connection.py": "tests/integration/test_connection.py",
        "test_feedback_points.py": "tests/integration/test_feedback_points.py",
        "test_enhanced_features.py": "tests/integration/test_enhanced_features.py",
        "test_image_processing.py": "tests/integration/test_image_processing.py",
        "redis_test.py": "tests/integration/redis_test.py",
        
        # 移动到tests/e2e/
        "test_wechat_login.html": "tests/e2e/test_wechat_login.html"
    }
    
    for old_path, new_path in test_files.items():
        if os.path.exists(old_path):
            # 创建目标目录
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # 移动文件
            shutil.move(old_path, new_path)
            print(f"✅ {old_path} → {new_path}")
        else:
            print(f"⚠️  文件不存在: {old_path}")

def move_tool_files():
    """移动工具文件到tools目录"""
    print("🔧 移动工具文件...")
    
    # 工具文件映射
    tool_files = {
        # 移动到tools/cache/
        "redis_client.py": "tools/cache/redis_client.py",
        
        # 移动到tools/database/
        "database.py": "tools/database/database.py",
        "database_init.sql": "tools/database/database_init.sql",
        "database_init_mysql.sql": "tools/database/database_init_mysql.sql",
        "database_feedback_points_migration.sql": "tools/database/database_feedback_points_migration.sql",
        "database_migration.sql": "tools/database/database_migration.sql",
        "init_db.py": "tools/database/init_db.py",
        
        # 移动到tools/scripts/
        "create_new_structure.py": "tools/scripts/create_new_structure.py",
        "migrate_to_new_structure.py": "tools/scripts/migrate_to_new_structure.py",
        "reorganize_project.py": "tools/scripts/reorganize_project.py",
        "dev_start.py": "tools/scripts/dev_start.py",
        "mysql_start.py": "tools/scripts/mysql_start.py",
        "remote_start.py": "tools/scripts/remote_start.py",
        "run_local.py": "tools/scripts/run_local.py",
        "start.py": "tools/scripts/start.py",
        "start.bat": "tools/scripts/start.bat",
        "start.sh": "tools/scripts/start.sh"
    }
    
    for old_path, new_path in tool_files.items():
        if os.path.exists(old_path):
            # 创建目标目录
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # 移动文件
            shutil.move(old_path, new_path)
            print(f"✅ {old_path} → {new_path}")
        else:
            print(f"⚠️  文件不存在: {old_path}")

def update_import_paths():
    """更新导入路径"""
    print("🔄 更新导入路径...")
    
    # 需要更新导入的文件
    files_to_update = [
        "main.py",
        "framework/fastapi_app.py",
        "business/image_conversion/service.py",
        "business/feedback/service.py",
        "business/points/service.py",
        "framework/routes/image.py",
        "framework/routes/feedback.py",
        "framework/routes/points.py"
    ]
    
    # 导入路径映射
    import_mappings = {
        # 数据库相关
        "from database import": "from tools.database.database import",
        "from models import": "from infra.database.models import",
        "from init_db import": "from tools.database.init_db import",
        
        # Redis相关
        "from redis_client import": "from tools.cache.redis_client import",
        
        # 测试相关
        "from test_connection import": "from tests.integration.test_connection import",
        "from test_feedback_points import": "from tests.integration.test_feedback_points import",
        
        # 配置相关
        "from config import": "from config import",
        "from auth import": "from tool.crypto.jwt import"
    }
    
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

def create_new_readme():
    """创建新的README文件"""
    print("📝 创建新的README文件...")
    
    readme_content = """# 🖼️ 图片处理服务

一个功能强大的图片处理服务，支持多种格式转换、压缩、水印等功能，包含用户管理、积分系统、反馈留言等完整功能。

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
```bash
# 执行数据库初始化
mysql -u root -p image_convert_db < tools/database/database_init_mysql.sql

# 执行功能迁移
mysql -u root -p image_convert_db < tools/database/database_feedback_points_migration.sql
```

### 4. 启动服务
```bash
python main.py
```

### 5. 访问服务
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 📁 项目结构

```
image-convert-python/
├── framework/          # HTTP框架层
├── business/           # 核心业务层
├── tool/              # 工具层
├── infra/             # 基础设施层
├── domain/            # 领域层
├── types/             # 类型定义
├── config/            # 配置
├── docs/              # 文档
├── tests/             # 测试
├── tools/             # 工具脚本
└── main.py            # 应用入口
```

## 🎯 核心功能

### 图片处理
- 多格式转换 (JPEG, PNG, WEBP, BMP, TIFF, GIF)
- 图片压缩和优化
- 尺寸调整
- 水印添加
- 批量处理

### 用户系统
- 用户注册和登录
- 会员等级管理
- 权限控制
- 微信登录集成

### 积分系统
- 每日签到奖励
- 连续签到额外奖励
- 图片转换积分
- 反馈奖励积分
- 积分兑换功能

### 反馈系统
- 多类型反馈提交
- 管理员回复
- 状态跟踪
- 搜索和筛选

## 📚 文档

- [架构设计](docs/architecture/)
- [功能说明](docs/features/)
- [部署指南](docs/deployment/)
- [API文档](http://localhost:8000/docs)

## 🧪 测试

```bash
# 运行集成测试
python -m pytest tests/integration/

# 运行端到端测试
python -m pytest tests/e2e/

# 运行特定测试
python tests/integration/test_feedback_points.py
```

## 🔧 工具

- [数据库工具](tools/database/)
- [缓存工具](tools/cache/)
- [部署脚本](tools/scripts/)

## 📄 许可证

MIT License
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README.md 创建完成")

def cleanup_old_files():
    """清理旧文件"""
    print("🧹 清理旧文件...")
    
    # 需要清理的旧文件
    old_files = [
        "enhanced_models.py",
        "enhanced_image_router.py",
        "test_wechat_login.html"
    ]
    
    for file_path in old_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ 删除旧文件: {file_path}")

def main():
    """主函数"""
    print("🚀 开始重组项目结构...")
    
    # 1. 创建目录结构
    create_directories()
    
    # 2. 移动文档文件
    move_documentation_files()
    
    # 3. 移动测试文件
    move_test_files()
    
    # 4. 移动工具文件
    move_tool_files()
    
    # 5. 更新导入路径
    update_import_paths()
    
    # 6. 创建新README
    create_new_readme()
    
    # 7. 清理旧文件
    cleanup_old_files()
    
    print("\n🎉 项目重组完成!")
    print("\n📋 重组后的结构:")
    print("├── docs/          # 所有文档")
    print("├── tests/         # 所有测试")
    print("├── tools/         # 所有工具脚本")
    print("└── 其他目录保持不变")

if __name__ == "__main__":
    main()
