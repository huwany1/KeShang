"""
模块: services.auth_service.models
职责: 定义认证服务的数据模型。
输入: 无。
输出: SQLAlchemy ORM 模型类。
"""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from common.db.base import Base


class User(Base):
    """用户实体模型。
    字段:
    - id: 用户ID主键
    - email: 邮箱（唯一索引）
    - name: 昵称
    - passwordHash: 口令哈希
    - role: 角色（teacher/student）
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    passwordHash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="teacher")


class Class(Base):
    """班级实体模型。
    字段:
    - id: 班级ID
    - name: 班级名称
    - teacherId: 任课教师ID（users.id）
    - joinCode: 加入码
    """

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    teacherId: Mapped[int] = mapped_column(Integer, nullable=False)
    joinCode: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)


class ClassSession(Base):
    """课堂会话实体模型。
    字段:
    - id: 会话ID
    - classId: 班级ID（classes.id）
    - documentId: 文档ID（documents.id）
    - startTime: ISO 字符串（MVP 简化）
    """

    __tablename__ = "class_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    classId: Mapped[int] = mapped_column(Integer, nullable=False)
    documentId: Mapped[str] = mapped_column(String(64), nullable=False)
    startTime: Mapped[str] = mapped_column(String(32), nullable=False, default="")
