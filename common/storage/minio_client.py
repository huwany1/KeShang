"""
模块: common.storage.minio_client
职责: 提供 MinIO 客户端与基础存储操作（桶创建、文件上传/下载）。
输入: settings（MinIO 端点与凭证）。
输出: get_minio_client, ensure_bucket, put_object_from_path, get_object_to_path。
"""

from pathlib import Path
from typing import Optional
from minio import Minio
from minio.error import S3Error

from common.config.settings import settings


def get_minio_client() -> Minio:
    """创建 MinIO 客户端。
    输入: 无。
    输出: Minio 客户端实例。
    作用: 统一对象存储访问入口。
    """
    endpoint = settings.minioEndpoint
    secure = settings.minioSecure
    access_key = settings.minioAccessKey
    secret_key = settings.minioSecretKey
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def ensure_bucket(client: Minio, bucket_name: Optional[str] = None) -> None:
    """确保桶存在，不存在则创建。
    输入: Minio 客户端，可选桶名（默认从 settings）。
    输出: None。
    作用: 初始化对象存储资源。
    """
    bucket = bucket_name or settings.minioBucket
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)


def put_object_from_path(client: Minio, local_path: Path, object_name: str, bucket_name: Optional[str] = None) -> None:
    """将本地文件上传到对象存储。
    输入: Minio 客户端、本地路径、对象名、可选桶名。
    输出: None。
    作用: 文档上传后端实现。
    """
    bucket = bucket_name or settings.minioBucket
    client.fput_object(bucket, object_name, str(local_path))


def get_object_to_path(client: Minio, object_name: str, local_path: Path, bucket_name: Optional[str] = None) -> None:
    """从对象存储下载文件到本地路径。
    输入: Minio 客户端、对象名、本地路径、可选桶名。
    输出: None。
    作用: 文档解析任务需要下载原文件。
    """
    bucket = bucket_name or settings.minioBucket
    client.fget_object(bucket, object_name, str(local_path))
