"""
数据库连接模块

使用SQLAlchemy ORM + aiosqlite实现异步数据库操作
支持与TypeScript版本共享同一个SQLite数据库文件
"""

from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from config.settings import settings
from core.logger import logger


class Base(DeclarativeBase):
    """SQLAlchemy模型基类"""
    pass


# 创建异步引擎
def create_engine():
    """
    创建数据库引擎
    
    特性：
    - 异步操作（aiosqlite）
    - 与TypeScript版本共享数据库文件
    - 支持连接池配置
    """
    # 获取数据库路径
    db_path = settings.get_database_path()
    
    # 确保数据库目录存在
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 构造异步SQLite连接URL
    # file:./.voltagent/trading.db -> sqlite+aiosqlite:///.voltagent/trading.db
    db_url = f"sqlite+aiosqlite:///{db_path}"
    
    logger.info(f"数据库连接: {db_url}")
    
    # 创建异步引擎
    engine = create_async_engine(
        db_url,
        echo=settings.DEV_MODE,  # 开发模式下打印SQL
        poolclass=NullPool,  # SQLite不需要连接池
        connect_args={
            "check_same_thread": False,  # SQLite多线程配置
        }
    )
    
    return engine


# 全局引擎实例
engine = create_engine()

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（依赖注入）
    
    使用方式：
        async with get_session() as session:
            result = await session.execute(...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 别名，保持兼容性
get_async_session = get_session

# 导出AsyncSession类型供外部使用
__all__ = [
    'Base',
    'engine',
    'get_session',
    'get_async_session',
    'AsyncSession',  # 重新导出
    'init_database',
    'close_database',
    'get_sync_session',
    'init_database_sync',
]


async def init_database():
    """
    初始化数据库
    
    创建所有表（如果不存在）
    注意：这会读取所有继承自Base的模型类
    """
    from core.models import (
        Trade, Position, AccountHistory,
        TradingSignal, AgentDecision, SystemConfig
    )
    
    logger.info("初始化数据库...")
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ 数据库初始化完成")


async def close_database():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("数据库连接已关闭")


# 同步版本的数据库操作（用于脚本和工具）
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import sessionmaker, Session


def create_sync_engine_instance():
    """创建同步引擎（用于简单脚本）"""
    db_path = settings.get_database_path()
    db_url = f"sqlite:///{db_path}"
    
    return create_sync_engine(
        db_url,
        echo=settings.DEV_MODE,
        connect_args={"check_same_thread": False}
    )


# 同步会话工厂
sync_engine = create_sync_engine_instance()
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_sync_session() -> Session:
    """
    获取同步数据库会话
    
    使用方式：
        with get_sync_session() as session:
            result = session.execute(...)
    """
    return SyncSessionLocal()


def init_database_sync():
    """同步初始化数据库"""
    from core.models import (
        Trade, Position, AccountHistory,
        TradingSignal, AgentDecision, SystemConfig
    )
    
    logger.info("初始化数据库（同步）...")
    Base.metadata.create_all(sync_engine)
    logger.info("✅ 数据库初始化完成")


if __name__ == "__main__":
    # 测试数据库初始化
    import asyncio
    
    async def test():
        await init_database()
        
        # 测试会话创建
        async with get_session() as session:
            logger.info("✅ 数据库会话创建成功")
        
        await close_database()
    
    asyncio.run(test())
    
    print("\n✅ 数据库测试完成")

