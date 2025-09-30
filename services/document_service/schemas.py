"""
模块: services.document_service.schemas
职责: 文档上传与状态查询的请求/响应模型。
输入: HTTP 请求体与路径参数。
输出: 结构化响应。
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """上传响应体。
    输入: 无。
    输出: documentId 与初始状态。
    作用: 前端据此轮询状态。
    """
    documentId: str
    status: str


class StatusResponse(BaseModel):
    """状态查询响应体。
    输入: 无。
    输出: 状态与可选知识图谱ID。
    作用: 前端判断是否可进入课堂互动。
    """
    documentId: str
    status: str
    knowledgeGraphId: str | None = None
