"""
模块: services.realtime_service.routes
职责: 提供 WebSocket 课堂会话占位接口。
输入: WebSocket 连接。
输出: 双向消息（占位）。
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["realtime"]) 


@router.websocket("/session/{session_id}")
async def ws_session(websocket: WebSocket, session_id: str) -> None:
    """课堂会话 WebSocket 占位。
    输入: WebSocket, session_id。
    输出: 回显消息。
    作用: MVP 阶段验证长连接通路。
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"session={session_id}, echo={data}")
    except WebSocketDisconnect:
        return
