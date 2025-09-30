"""
模块: common.config.settings
职责: 统一加载与校验应用配置。
输入: 读取环境变量或 .env 文件。
输出: 提供类型安全的全局配置对象 Settings。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """应用配置对象。
    - 输入: 环境变量/.env
    - 输出: 可在各模块导入使用的配置属性
    - 作用: 提供集中式配置与默认值
    """

    # 通用
    appEnv: str = Field(default="development")
    appLogLevel: str = Field(default="INFO")
    appTimezone: str = Field(default="Asia/Shanghai")

    # 安全
    jwtSecret: str = Field(default="please_change_me")
    jwtAlgorithm: str = Field(default="HS256")
    jwtExpireMinutes: int = Field(default=120)
    passwordHashSchemes: str = Field(default="bcrypt")

    # PostgreSQL
    postgresHost: str = Field(default="postgres")
    postgresPort: int = Field(default=5432)
    postgresDb: str = Field(default="keshang")
    postgresUser: str = Field(default="keshang")
    postgresPassword: str = Field(default="keshang_password")
    postgresPoolMin: int = Field(default=1)
    postgresPoolMax: int = Field(default=10)

    # Redis
    redisHost: str = Field(default="redis")
    redisPort: int = Field(default=6379)
    redisDb: int = Field(default=0)
    redisPassword: str | None = Field(default=None)

    # RabbitMQ
    rabbitmqHost: str = Field(default="rabbitmq")
    rabbitmqPort: int = Field(default=5672)
    rabbitmqUser: str = Field(default="guest")
    rabbitmqPassword: str = Field(default="guest")
    rabbitmqVhost: str = Field(default="/")

    # Celery
    celeryBrokerUrl: str = Field(default="amqp://guest:guest@rabbitmq:5672//")
    celeryResultBackend: str = Field(default="redis://redis:6379/1")
    celeryTaskSoftTimeLimit: int = Field(default=60)
    celeryTaskTimeLimit: int = Field(default=120)

    # Neo4j
    neo4jUri: str = Field(default="bolt://neo4j:7687")
    neo4jUser: str = Field(default="neo4j")
    neo4jPassword: str = Field(default="neo4j_password")

    # MinIO (模拟 COS)
    minioEndpoint: str = Field(default="minio:9000")
    minioAccessKey: str = Field(default="minioadmin")
    minioSecretKey: str = Field(default="minioadmin")
    minioSecure: bool = Field(default=False)
    minioBucket: str = Field(default="keshang-documents")

    # 服务端口
    authServicePort: int = Field(default=8001)
    documentServicePort: int = Field(default=8002)
    knowledgeServicePort: int = Field(default=8003)
    questionServicePort: int = Field(default=8004)
    realtimeServicePort: int = Field(default=8005)

    # 题目生成占位
    qgMaxTokens: int = Field(default=256)
    qgDefaultTemperature: float = Field(default=0.2)
    qgAdapterType: str = Field(default="local")  # local | remote
    qgRemoteUrl: str = Field(default="http://model-service:9000/generate")
    qgQualityMinScore: float = Field(default=0.6)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
