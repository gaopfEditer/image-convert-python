# 🏗️ 图片处理服务 - 新架构

## 📁 项目结构

```
image-convert-python/
├── framework/                 # HTTP框架层 (可替换)
│   ├── fastapi_app.py        # FastAPI应用配置
│   ├── middleware/           # 中间件
│   ├── routes/               # 路由层
│   └── schemas/              # API模型
├── business/                 # 核心业务层 (不可替换)
│   ├── image_conversion/     # 图片转换业务
│   ├── user_management/      # 用户管理业务
│   ├── payment/              # 支付业务
│   └── permission/           # 权限管理业务
├── tool/                     # 工具层 (可复用)
│   ├── image/                # 图片处理工具
│   ├── file/                 # 文件操作工具
│   ├── crypto/               # 加密工具
│   └── utils/                # 通用工具
├── infra/                    # 基础设施层 (可插拔)
│   ├── database/             # 数据库
│   ├── cache/                # 缓存
│   ├── storage/              # 存储
│   └── external/             # 外部服务
├── domain/                   # 领域层 (DDD)
│   ├── entities/             # 实体
│   ├── value_objects/        # 值对象
│   ├── services/             # 领域服务
│   └── repositories/         # 仓储接口
├── types/                    # 类型定义
├── config/                   # 配置
├── tests/                    # 测试
├── scripts/                  # 脚本
└── docs/                     # 文档
```

## 🎯 分层职责

### 1. Framework Layer (框架层)
**职责**: HTTP框架细节处理
**特点**: 可替换，框架无关
**包含**:
- FastAPI应用配置
- 中间件 (CORS, 认证, 日志)
- 路由定义
- API模型定义

### 2. Business Layer (业务层)
**职责**: 核心业务逻辑
**特点**: 不可替换，业务核心
**包含**:
- 图片转换业务流程
- 用户管理业务
- 支付业务逻辑
- 权限管理

### 3. Tool Layer (工具层)
**职责**: 无状态工具函数
**特点**: 可复用、可测试
**包含**:
- 图片处理工具 (PIL封装)
- 文件操作工具
- 加密工具
- 通用工具函数

### 4. Infra Layer (基础设施层)
**职责**: 外部服务适配
**特点**: 可插拔，换云厂商不影响业务
**包含**:
- 数据库连接和操作
- 缓存服务
- 存储服务
- 外部API客户端

### 5. Domain Layer (领域层)
**职责**: 业务实体和规则
**特点**: 领域驱动设计
**包含**:
- 业务实体
- 值对象
- 领域服务
- 仓储接口

## 🚀 快速开始

### 1. 创建新架构
```bash
# 创建目录结构
python create_new_structure.py

# 迁移现有代码
python migrate_to_new_structure.py
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境
```bash
# 复制配置文件
cp config/settings.py.example config/settings.py

# 编辑配置
vim config/settings.py
```

### 4. 初始化数据库
```bash
python scripts/init_database.py
```

### 5. 启动服务
```bash
python main.py
```

## 🔧 核心特性

### 1. 清晰分层
- **Framework**: 处理HTTP请求/响应
- **Business**: 核心业务逻辑
- **Tool**: 可复用工具函数
- **Infra**: 外部服务适配
- **Domain**: 业务实体和规则

### 2. 依赖注入
```python
# 在路由中注入服务
@router.post("/convert")
async def convert_image(
    conversion_service: ImageConversionService = Depends(get_image_conversion_service)
):
    # 使用服务
    pass
```

### 3. 类型安全
```python
# 使用类型定义
from types import ProcessingParams, ImageFormat

params = ProcessingParams(
    target_format=ImageFormat.JPEG,
    quality=95,
    resize_width=800,
    resize_height=600
)
```

### 4. 可测试性
```python
# 每层都可以独立测试
def test_image_processor():
    processor = ImageProcessor()
    result = processor.convert_image(input_path, output_path, params)
    assert result.width == 800
```

## 📊 架构优势

### 1. 高内聚低耦合
- 相关功能聚合在同一层
- 层间依赖清晰明确
- 易于理解和维护

### 2. 可替换性
- 框架层可以替换为其他HTTP框架
- 基础设施层可以替换为其他云服务
- 工具层可以替换为其他实现

### 3. 可扩展性
- 新功能可以按层添加
- 不影响现有代码
- 易于功能扩展

### 4. 可测试性
- 每层都可以独立测试
- 可以模拟依赖进行单元测试
- 支持集成测试和端到端测试

## 🔄 迁移指南

### 1. 现有代码迁移
```bash
# 运行迁移脚本
python migrate_to_new_structure.py
```

### 2. 修复导入错误
```python
# 旧导入
from database import get_db
from models import User

# 新导入
from infra.database.connection import get_db
from infra.database.models import User
```

### 3. 更新配置文件
```python
# 旧配置
from config import settings

# 新配置
from config import settings
```

## 🧪 测试

### 1. 单元测试
```bash
# 运行单元测试
python -m pytest tests/unit/
```

### 2. 集成测试
```bash
# 运行集成测试
python -m pytest tests/integration/
```

### 3. 端到端测试
```bash
# 运行端到端测试
python -m pytest tests/e2e/
```

## 📚 文档

- [API文档](docs/api/)
- [架构文档](docs/architecture/)
- [部署文档](docs/deployment/)

## 🤝 贡献

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License
