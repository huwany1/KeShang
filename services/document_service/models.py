"""
模块: services.document_service.models
职责: 定义文档处理相关的 ORM 模型。
输入: 无。
输出: SQLAlchemy ORM 模型。
"""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from common.db.base import Base


class Document(Base):
    """文档实体模型。
    字段:
    - id: 文档ID (UUID字符串)
    - uploaderId: 上传者用户ID（可空）
    - fileName: 原始文件名
    - objectPath: 对象存储中的对象键名
    - status: 处理状态 processing/ready/failed
    - knowledgeGraphId: 关联的图谱标识（MVP 用 docId 占位）
    """

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    uploaderId: Mapped[int | None] = mapped_column(nullable=True)
    fileName: Mapped[str] = mapped_column(String(255), nullable=False)
    objectPath: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="processing")
    knowledgeGraphId: Mapped[str | None] = mapped_column(String(128), nullable=True)


class DocumentConcept(Base):
    """文档概念表：存储解析出的概念候选。"""

    __tablename__ = "document_concepts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    documentId: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    conceptName: Mapped[str] = mapped_column(String(255), nullable=False, index=True)


class DocumentRelation(Base):
    """文档关系表：存储概念之间的简单关系（占位）。"""

    __tablename__ = "document_relations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    documentId: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sourceConcept: Mapped[str] = mapped_column(String(255), nullable=False)
    targetConcept: Mapped[str] = mapped_column(String(255), nullable=False)
