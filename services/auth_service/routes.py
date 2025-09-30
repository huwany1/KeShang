"""
模块: services.auth_service.routes
职责: 提供用户注册与登录 API。
输入: HTTP 请求体（注册/登录）。
输出: JWT 令牌或错误信息。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from common.db.postgres import async_session
from common.security.auth import hash_password, verify_password, create_access_token
from services.auth_service.models import User
from services.auth_service.schemas import RegisterRequest, LoginRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(async_session)) -> AuthResponse:
    """注册用户并返回访问令牌。
    输入: RegisterRequest(email, name, password)。
    输出: AuthResponse(accessToken)。
    作用: 创建用户，避免重复注册。
    """
    exists = await session.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=payload.email, name=payload.name, passwordHash=hash_password(payload.password), role="teacher")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(str(user.id), {"role": user.role})
    return AuthResponse(accessToken=token)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(async_session)) -> AuthResponse:
    """用户登录并返回访问令牌。
    输入: LoginRequest(email, password)。
    输出: AuthResponse(accessToken)。
    作用: 校验口令并签发 JWT。
    """
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.passwordHash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(user.id), {"role": user.role})
    return AuthResponse(accessToken=token)
