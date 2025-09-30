"""
模块: services.knowledge_service.main
职责: 知识引擎服务入口，提供健康检查与占位路由。
输入: HTTP 请求。
输出: JSON 响应。
"""

from fastapi import FastAPI
from common.config.settings import settings
from services.knowledge_service.routes import router as knowledge_router

app = FastAPI(title="Knowledge Service", version="0.1.0")
app.include_router(knowledge_router)


@app.get("/health")
def health() -> dict:
    """健康检查。
    输入: 无。
    输出: 服务状态字典。
    作用: 供编排与探针检测服务可用性。
    """
    return {"service": "knowledge", "status": "ok"}


@app.get("/version")
def version() -> dict:
    """版本信息。
    输入: 无。
    输出: 应用版本与环境。
    作用: 排障与可观测性。
    """
    return {"version": app.version, "env": settings.appEnv}
