"""
模块: services.document_service.main
职责: 文档处理服务入口，提供健康检查与占位路由。
输入: HTTP 请求。
输出: JSON 响应。
"""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from common.config.settings import settings
from common.db.postgres import get_async_engine
from common.db.base import Base
from services.document_service.routes import router as document_router
from services.document_service import models  # ensure models imported

app = FastAPI(title="Document Service", version="0.1.0")
app.include_router(document_router)


@app.on_event("startup")
async def on_startup() -> None:
    """启动时创建表（开发模式）。"""
    engine: AsyncEngine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
def health() -> dict:
    """健康检查。
    输入: 无。
    输出: 服务状态字典。
    作用: 供编排与探针检测服务可用性。
    """
    return {"service": "document", "status": "ok"}


@app.get("/version")
def version() -> dict:
    """版本信息。
    输入: 无。
    输出: 应用版本与环境。
    作用: 排障与可观测性。
    """
    return {"version": app.version, "env": settings.appEnv}
