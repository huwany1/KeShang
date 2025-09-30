"""
模块: services.auth_service.main
职责: 认证服务入口，提供健康检查与占位路由。
输入: HTTP 请求。
输出: JSON 响应。
"""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from common.config.settings import settings
from common.db.postgres import get_async_engine
from common.db.base import Base
from services.auth_service.routes import router as auth_router

app = FastAPI(title="Auth Service", version="0.1.0")
app.include_router(auth_router)


@app.on_event("startup")
async def on_startup() -> None:
    """应用启动钩子。
    输入: 无。
    输出: 无。
    作用: 自动创建数据库表（仅开发环境）。
    """
    engine: AsyncEngine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
def health() -> dict:
    """健康检查。
    输入: 无。
    输出: 包含服务名与状态的字典。
    作用: 供编排与探针检测服务可用性。
    """
    return {"service": "auth", "status": "ok"}


@app.get("/version")
def version() -> dict:
    """版本信息。
    输入: 无。
    输出: 应用版本与环境。
    作用: 排障与可观测性。
    """
    return {"version": app.version, "env": settings.appEnv}
