"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

async def init_database():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_async():
    """获取异步数据库会话"""
    # 这里可以使用异步数据库驱动如 asyncpg
    # 目前使用同步版本
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
