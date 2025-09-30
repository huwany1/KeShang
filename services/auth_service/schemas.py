"""
模块: services.auth_service.schemas
职责: 定义认证服务的请求/响应数据模型。
输入: HTTP 请求中的 JSON 载荷。
输出: 序列化的响应模型。
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """注册请求体。
    输入: email, name, password。
    输出: 无（用于请求校验）。
    作用: 注册接口请求体模型。
    """
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    """登录请求体。
    输入: email, password。
    输出: 无（用于请求校验）。
    作用: 登录接口请求体模型。
    """
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """鉴权响应体。
    输入: 无。
    输出: accessToken JWT。
    作用: 前端保存并附带于后续请求。
    """
    accessToken: str
