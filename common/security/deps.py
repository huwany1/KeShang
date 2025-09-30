"""
模块: common.security.deps
职责: 提供统一鉴权依赖（FastAPI Depends）。
输入: Authorization: Bearer <token>
输出: 解析后的 claims。
"""

from fastapi import Header, HTTPException, status
from typing import Dict

from common.security.auth import verify_token


def jwt_auth(authorization: str | None = Header(default=None)) -> Dict:
    """统一鉴权依赖：从 Authorization 头中提取 Bearer Token 并校验。
    输入: 请求头 Authorization。
    输出: 解码后的 JWT 载荷（claims）。
    作用: 保护需要鉴权的接口。
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = verify_token(token)
        return claims
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
