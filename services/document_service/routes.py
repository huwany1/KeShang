"""
模块: services.document_service.routes
职责: 提供文档上传与状态查询 API（与存储/队列/DB 串联）。
输入: 表单文件或 JSON。
输出: 文档ID、处理状态、图谱ID等。
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from common.db.postgres import async_session
from common.storage.minio_client import get_minio_client, ensure_bucket, put_object_from_path
from common.security.deps import jwt_auth
from services.document_service.models import Document
from services.document_service.schemas import UploadResponse, StatusResponse
from services.document_service.worker import extract_text_task

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(async_session),
    claims: dict = Depends(jwt_auth),
) -> UploadResponse:
    """上传课件文件，存入 MinIO 并创建 DB 记录，同时触发解析任务。
    输入: UploadFile (PPT/PDF)。
    输出: UploadResponse(documentId, status)。
    作用: 串起对象存储、数据库与 Celery 任务。
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    document_id = str(uuid.uuid4())
    object_name = f"uploads/{document_id}/{file.filename}"

    tmp_path = Path(".build") / document_id
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = tmp_path
    content = await file.read()
    tmp_file.write_bytes(content)

    client = get_minio_client()
    ensure_bucket(client)
    put_object_from_path(client, tmp_file, object_name)

    doc = Document(
        id=document_id,
        uploaderId=int(claims.get("sub", 0)) if str(claims.get("sub", "0")).isdigit() else None,
        fileName=file.filename,
        objectPath=object_name,
        status="processing",
        knowledgeGraphId=None,
    )
    session.add(doc)
    await session.commit()

    extract_text_task.delay(object_name)

    return UploadResponse(documentId=document_id, status="processing")


@router.get("/{document_id}/status", response_model=StatusResponse)
async def get_document_status(document_id: str, session: AsyncSession = Depends(async_session)) -> StatusResponse:
    """查询文档处理状态（从数据库读取）。
    输入: document_id。
    输出: StatusResponse。
    作用: 前端轮询使用。
    """
    result = await session.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return StatusResponse(documentId=doc.id, status=doc.status, knowledgeGraphId=doc.knowledgeGraphId)
