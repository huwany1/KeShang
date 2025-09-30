"""
模块: common.cache.redis_client
职责: 提供 Redis 同步/异步客户端工厂（此处用同步，题目缓存可选异步）。
输入: settings 中的 Redis 配置。
输出: get_redis_client() 返回已配置的 Redis 客户端。
"""

from typing import Optional
import redis

from common.config.settings import settings


def build_redis_url(db: Optional[int] = None) -> str:
    """构建 Redis 连接 URL。
    输入: 可选 db 索引。
    输出: 形如 redis://[:password]@host:port/db 的 URL。
    作用: 统一拼接 Redis 连接。
    """
    host = settings.redisHost
    port = settings.redisPort
    password = settings.redisPassword or ""
    database = db if db is not None else settings.redisDb
    auth = f":{password}@" if password else ""
    return f"redis://{auth}{host}:{port}/{database}"


def get_redis_client(db: Optional[int] = None) -> redis.Redis:
    """创建 Redis 客户端实例。
    输入: 可选 db 索引。
    输出: redis.Redis 客户端。
    作用: 提供统一的 Redis 访问入口。
    """
    url = build_redis_url(db)
    return redis.from_url(url, decode_responses=True)
