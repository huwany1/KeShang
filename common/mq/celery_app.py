"""
模块: common.mq.celery_app
职责: 提供 Celery 应用实例与统一配置，供各服务的任务使用。
输入: settings 中的 Broker/Backend 配置。
输出: celery_app Celery 实例。
"""

from celery import Celery
from common.config.settings import settings


def create_celery_app() -> Celery:
    """创建并返回 Celery 应用实例。
    输入: 无。
    输出: Celery 实例。
    作用: 统一 Celery 配置，便于被各微服务导入。
    """
    app = Celery(
        "keshang",
        broker=settings.celeryBrokerUrl,
        backend=settings.celeryResultBackend,
        include=[],  # 由具体服务扩展
    )

    app.conf.update(
        task_soft_time_limit=settings.celeryTaskSoftTimeLimit,
        task_time_limit=settings.celeryTaskTimeLimit,
        task_always_eager=False,
    )
    return app


celery_app = create_celery_app()
