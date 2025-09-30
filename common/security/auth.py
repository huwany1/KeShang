"""
模块: common.security.auth
职责: 提供 JWT 签发/校验与口令哈希工具。
输入: settings（密钥、算法、过期时长）。
输出: create_access_token, verify_token, hash_password, verify_password。
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from common.config.settings import settings


password_context = CryptContext(schemes=[settings.passwordHashSchemes], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """对明文口令进行哈希。
    输入: 明文密码。
    输出: 哈希后的密码字符串。
    作用: 安全存储用户密码。
    """
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文口令与已存哈希是否匹配。
    输入: 明文密码、哈希密码。
    输出: 布尔值，表示匹配结果。
    作用: 登录鉴权。
    """
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    """创建 JWT 访问令牌。
    输入: subject（通常为用户ID），可选额外声明。
    输出: JWT 字符串。
    作用: 为前端颁发访问令牌。
    """
    expire_delta = timedelta(minutes=settings.jwtExpireMinutes)
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expire_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.jwtSecret, algorithm=settings.jwtAlgorithm)
    return token


def verify_token(token: str) -> Dict[str, Any]:
    """验证 JWT 并返回解码后的载荷。
    输入: JWT 字符串。
    输出: 载荷字典；若失败应抛出异常供上层处理。
    作用: 后端鉴权中间件或依赖使用。
    """
    try:
        payload = jwt.decode(token, settings.jwtSecret, algorithms=[settings.jwtAlgorithm])
        return payload
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
