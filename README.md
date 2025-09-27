# 🖼️ 图片处理服务

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
