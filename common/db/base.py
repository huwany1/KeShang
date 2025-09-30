"""
模块: common.db.base
职责: 提供 SQLAlchemy 声明式 Base 与元数据，供各服务模型继承。
输入: 无。
输出: Base 对象。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""
    pass
