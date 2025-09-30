"""
模块: services.realtime_service.main
职责: 实时互动服务入口，提供健康检查与占位路由。
输入: HTTP 请求与 WebSocket 请求。
输出: JSON 与消息双向传输。
"""

from fastapi import FastAPI
from common.config.settings import settings
from services.realtime_service.routes import router as realtime_router

app = FastAPI(title="Realtime Service", version="0.1.0")
app.include_router(realtime_router)


@app.get("/health")
def health() -> dict:
    """健康检查。
    输入: 无。
    输出: 服务状态字典。
    作用: 供编排与探针检测服务可用性。
    """
    return {"service": "realtime", "status": "ok"}


@app.get("/version")
def version() -> dict:
    """版本信息。
    输入: 无。
    输出: 应用版本与环境。
    作用: 排障与可观测性。
    """
    return {"version": app.version, "env": settings.appEnv}
