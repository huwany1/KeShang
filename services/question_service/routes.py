"""
模块: services.question_service.routes
职责: 提供题目生成 API（含缓存与适配器）。
输入: 概念与难度。
输出: 题目结构。
"""

import json
from hashlib import md5
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from common.cache.redis_client import get_redis_client
from common.security.deps import jwt_auth
from services.question_service.adapters import get_adapter

router = APIRouter(prefix="/questions", tags=["questions"]) 


class GenerateRequest(BaseModel):
    """题目生成请求体。
    输入: documentId、conceptId 或 concept、difficulty。
    输出: 无（用于校验）。
    作用: 控制题目生成参数。
    """
    documentId: str | None = None
    conceptId: str | None = None
    concept: str | None = Field(default=None, min_length=1)
    difficulty: int = Field(ge=1, le=5)


@router.post("/generate")
async def generate_question(payload: GenerateRequest, claims: dict = Depends(jwt_auth)) -> dict:
    """按概念与难度生成题目，优先使用缓存，缓存未命中则调用适配器并进行质量校验。
    输入: GenerateRequest。
    输出: 题目字典。
    作用: 打通缓存与路由，后续可接入模型推理服务。
    """
    cache = get_redis_client()
    key_raw = json.dumps(payload.model_dump(), sort_keys=True, ensure_ascii=False)
    cache_key = "qg:" + md5(key_raw.encode("utf-8")).hexdigest()

    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    concept = payload.concept or payload.conceptId or "未知概念"
    adapter = get_adapter()
    item = adapter.generate(concept, payload.difficulty)
    if item is None:
        raise HTTPException(status_code=422, detail="Question generation failed quality check")

    cache.setex(cache_key, 300, json.dumps(item, ensure_ascii=False))
    return item
