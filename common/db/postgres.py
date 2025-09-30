"""
模块: common.db.postgres
职责: 提供 PostgreSQL 的异步连接引擎与会话工厂。
输入: 读取 settings 中的数据库配置。
输出: get_async_engine, get_session_maker, async_session 供服务使用。
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from common.config.settings import settings


def build_database_url() -> str:
    """构建异步数据库连接 URL。
    输入: 无，使用全局 settings。
    输出: str 形式的数据库连接串。
    作用: 统一拼接数据库连接参数。
    """
    return (
        f"postgresql+asyncpg://{settings.postgresUser}:{settings.postgresPassword}"
        f"@{settings.postgresHost}:{settings.postgresPort}/{settings.postgresDb}"
    )


def get_async_engine() -> AsyncEngine:
    """创建并返回异步引擎实例。
    输入: 无。
    输出: AsyncEngine 实例。
    作用: 供应用启动或模块按需获取数据库引擎。
    """
    database_url = build_database_url()
    engine = create_async_engine(
        database_url,
        pool_size=settings.postgresPoolMin,
        max_overflow=max(0, settings.postgresPoolMax - settings.postgresPoolMin),
        pool_pre_ping=True,
        future=True,
        echo=False,
    )
    return engine


def get_session_maker(engine: AsyncEngine) -> sessionmaker[AsyncSession]:
    """创建异步会话工厂。
    输入: AsyncEngine。
    输出: sessionmaker[AsyncSession]。
    作用: 标准化会话创建，避免重复代码。
    """
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供一个作用域内的异步会话。
    输入: 无。
    输出: AsyncSession 异步生成器。
    作用: 在请求生命周期内提供事务性数据库访问。
    """
    engine = get_async_engine()
    SessionLocal = get_session_maker(engine)
    async with SessionLocal() as session:
        yield session
