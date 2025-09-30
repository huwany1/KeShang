## 课熵智能课堂后端（MVP）

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
![Build](https://img.shields.io/badge/build-docker--compose-brightgreen)
![License](https://img.shields.io/badge/license-internal-lightgrey)
![Status](https://img.shields.io/badge/status-MVP-orange)

一个面向教学场景的后端服务集，支持账号认证、课件上传解析、知识图谱查询、题目生成与课堂实时互动。采用微服务架构，统一通过 Nginx API 网关对外提供接口。

---

### 功能特性
- **认证与授权**: 邮箱注册与登录，JWT 颁发与校验
- **文档处理**: 支持 PDF/PPT 上传，异步解析抽取概念与关系，写入 PostgreSQL 与 Neo4j
- **知识查询**: 按概念或文档生成子图数据，供前端可视化
- **题目生成**: 基于 Bloom 认知层级的本地/远程适配器，带缓存与质量校验
- **实时互动**: WebSocket 占位通道，支持课堂会话回显（可扩展抢答/投票）
- **统一网关**: Nginx 负责路径路由与 CORS、限流

---

### 技术栈
- Web: FastAPI, Pydantic, Uvicorn
- 数据: PostgreSQL, SQLAlchemy(Async), Redis
- 队列: RabbitMQ, Celery
- 图数据库: Neo4j
- 对象存储: MinIO（本地开发）
- 解析: PyMuPDF, python-pptx（MVP 占位）
- 运维: Docker Compose, Nginx

---

### 目录结构
```
d:/KeShang-intelligence/
  common/                  # 公共库: 配置/DB/缓存/存储/图/消息/鉴权
  services/
    auth_service/          # 认证服务（注册/登录）
    document_service/      # 文档上传/状态 + Celery 解析任务
    knowledge_service/     # 知识图谱查询
    question_service/      # 题目生成（带缓存与适配器）
    realtime_service/      # WebSocket 实时占位
  docker-compose.yml       # 一键编排（含 Postgres/Redis/RabbitMQ/Neo4j/MinIO/Nginx）
  nginx.conf               # API 网关配置
  requirements.txt         # Python 依赖
```

---

### 架构与端口
- API 网关: http://localhost:8080
  - `/auth` -> Auth Service (8001)
  - `/documents` -> Document Service (8002)
  - `/knowledge` -> Knowledge Service (8003)
  - `/questions` -> Question Service (8004)
  - `/ws` -> Realtime Service (WebSocket, 8005)
- 基础设施:
  - PostgreSQL: 5432
  - Redis: 6379
  - RabbitMQ: 5672（管理端 15672）
  - Neo4j: 7474/7687
  - MinIO: 9000（Console: 9001）

---

### 快速开始（Docker）
1) 准备环境
   - 安装 Docker Desktop（包含 Compose）
   - 克隆本仓库，并在项目根目录创建 `.env`（示例见下）

2) 启动
```bash
docker compose up -d --build
```

3) 健康检查
```bash
curl http://localhost:8080/auth/health | jq
curl http://localhost:8080/documents/health | jq
```

4) 关闭
```bash
docker compose down -v
```

---

### `.env` 示例（可按需调整）
```dotenv
# 应用
APP_ENV=development
APP_LOG_LEVEL=INFO
APP_TIMEZONE=Asia/Shanghai

# JWT
JWT_SECRET=please_change_me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=keshang
POSTGRES_USER=keshang
POSTGRES_PASSWORD=keshang_password
POSTGRES_POOL_MIN=1
POSTGRES_POOL_MAX=10

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# RabbitMQ / Celery
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TASK_SOFT_TIME_LIMIT=60
CELERY_TASK_TIME_LIMIT=120

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=keshang-documents

# 服务端口
AUTH_SERVICE_PORT=8001
DOCUMENT_SERVICE_PORT=8002
KNOWLEDGE_SERVICE_PORT=8003
QUESTION_SERVICE_PORT=8004
REALTIME_SERVICE_PORT=8005

# 题目生成
QG_MAX_TOKENS=256
QG_DEFAULT_TEMPERATURE=0.2
QG_ADAPTER_TYPE=local   # local | remote
QG_REMOTE_URL=http://model-service:9000/generate
QG_QUALITY_MIN_SCORE=0.6
```

> 备注: 若不设置上述变量，代码内已提供与 `docker-compose.yml` 匹配的默认值。

---

### 常用 API 示例

- 注册与登录（获取 `accessToken`）
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"t@example.com","name":"Teacher A","password":"pass1234"}'

curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"t@example.com","password":"pass1234"}'
```

- 文档上传与状态查询（需要 `Authorization: Bearer <token>`）
```bash
curl -X POST http://localhost:8080/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/sample.pdf"

curl http://localhost:8080/documents/{documentId}/status \
  -H "Authorization: Bearer $TOKEN"
```

- 知识查询
```bash
curl "http://localhost:8080/knowledge/concepts?concept=机器学习" \
  -H "Authorization: Bearer $TOKEN"

curl http://localhost:8080/knowledge/documents/{documentId}/graph \
  -H "Authorization: Bearer $TOKEN"
```

- 题目生成（缓存 5 分钟）
```bash
curl -X POST http://localhost:8080/questions/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"concept":"线性回归","difficulty":3}'
```

- WebSocket（占位回显）
```
ws://localhost:8080/ws/session/123
```

> 说明: 已在 `nginx.conf` 中优化了前缀转发策略，网关后的路径现已简洁（如 `/auth/login`）。

---

### 集合与示例 Token
- Postman/Thunder 集合位于 `docs/collections/`，导入后：
  - 先执行「Auth / Login」获取并自动保存 `token`
  - 其余受保护请求将自动使用 `Bearer {{token}}`
- Windows 示例脚本：`scripts/get_token.ps1`
  - 运行示例：
    ```powershell
    pwsh -File scripts/get_token.ps1 -Email "t@example.com" -Password "pass1234"
    ```


---

### 本地开发（不经 Docker）
1) Python 版本: 3.11+
2) 安装依赖
```bash
pip install -r requirements.txt
```
3) 启动某个服务（示例：认证服务）
```bash
uvicorn services.auth_service.main:app --reload --port 8001
```
4) 启动 Celery Worker（与 `document_service` 搭配）
```bash
celery -A services.document_service.worker worker -l INFO
```
> 需要本地已运行的 Postgres/Redis/RabbitMQ/Neo4j/MinIO，可通过 Docker 单独起这些基础设施。

---

### 关键设计约定
- 统一配置: `common.config.settings.Settings` 提供默认值并支持 `.env`
- DB 访问: `common.db.postgres.async_session` 作为 FastAPI 依赖注入
- 鉴权依赖: `common.security.deps.jwt_auth` 统一解析与校验 `Bearer Token`
- 存储操作: `common.storage.minio_client` 抽象对象存储常用方法
- 图写入: `common.graph.neo4j_writer` 以最小接口入图
- 任务编排: `common.mq.celery_app` 创建共享 Celery 应用

---

### 故障排查
- 端口占用: 调整 `docker-compose.yml` 暴露端口或本机占用端口
- MinIO 访问失败: 检查 `MINIO_ENDPOINT` 与凭证；首次会自动创建桶
- Neo4j 认证失败: 确认 `.env` 中 `NEO4J_PASSWORD` 与 Compose 中一致
- Celery 无法连接: 核对 `CELERY_BROKER_URL` 与 RabbitMQ 状态（15672）
- 路由前缀重复: 调整 Nginx location 或各服务路由 `prefix`

---

### 许可
内部项目（MVP）。如需开源协议，请在此处补充。

## 课熵智能课堂后端（MVP） / KeShang Intelligence Backend (MVP)

### 简介 / Overview
- **项目定位**: 面向课堂场景的多服务后端，覆盖认证、文档处理、知识图谱、题目生成与实时互动能力。
- **技术栈**: FastAPI、SQLAlchemy、PostgreSQL、Redis、RabbitMQ/Celery、Neo4j、MinIO、Nginx。
- **运行方式**: 提供 `docker-compose` 一键编排，也可本地逐服务启动（开发场景）。

### 目录结构 / Repository Structure
```
d:\KeShang-intelligence
  ├─ common/                 # 公共模块（配置、DB、缓存、图数据库、鉴权、中间件、存储）
  ├─ services/               # 业务服务（auth/document/knowledge/question/realtime）
  ├─ docker-compose.yml      # 编排入口（含 PostgreSQL/Redis/RabbitMQ/Neo4j/MinIO/Nginx 网关）
  ├─ nginx.conf              # API 网关与反向代理配置
  ├─ requirements.txt        # Python 依赖清单
  └─ README.md               # 本文件
```

### 运行前置 / Prerequisites
- Docker ≥ 24，Docker Compose 插件可用
- 端口未被占用：5432、6379、5672/15672、7474/7687、9000/9001、8001-8005、8080

### 快速开始 / Quick Start
1) 创建 `.env`（可按需覆盖默认值，未设置则使用 `common/config/settings.py` 中默认值）
```
# 应用
APP_ENV=development
APP_LOG_LEVEL=INFO
JWT_SECRET=please_change_me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=120

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=keshang
POSTGRES_USER=keshang
POSTGRES_PASSWORD=keshang_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# RabbitMQ & Celery
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=keshang-documents
```

2) 编排启动 / Compose Up
```bash
docker compose up -d --build
```

3) 健康检查 / Health Checks
```bash
curl http://localhost:8080/auth/health
curl http://localhost:8080/documents/health
curl http://localhost:8080/knowledge/health
curl http://localhost:8080/questions/health
curl http://localhost:8080/version  # 通过各服务 /version 亦可
```

### API 网关 / API Gateway
- 统一入口: `http://localhost:8080`
- 路由转发：
  - `/auth/` → `auth_service:8001`
  - `/documents/` → `document_service:8002`
  - `/knowledge/` → `knowledge_service:8003`
  - `/questions/` → `question_service:8004`
  - `/ws/` → `realtime_service:8005`（WebSocket）

### 鉴权 / Authentication
- 注册与登录接口颁发 `JWT`，后续接口需在请求头添加 `Authorization: Bearer <token>`。
- 示例 / Examples
```bash
# 注册
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@example.com","name":"Teacher","password":"Passw0rd!"}'

# 登录（获取 accessToken）
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@example.com","password":"Passw0rd!"}'
```

### 服务与端点 / Services & Endpoints
#### 认证服务 Auth Service (`/auth`)
- `POST /auth/register` → 注册并返回 `accessToken`
- `POST /auth/login` → 登录并返回 `accessToken`

#### 文档服务 Document Service (`/documents`)
- 需鉴权
- `POST /documents/upload`（表单字段 `file`，支持 PPT/PDF）
- `GET /documents/{documentId}/status` → 查询解析状态与 `knowledgeGraphId`
```bash
ACCESS_TOKEN=... # 替换为登录获得的 token
curl -X POST http://localhost:8080/documents/upload \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "file=@sample.pdf"
```

#### 知识服务 Knowledge Service (`/knowledge`)
- 需鉴权
- `GET /knowledge/concepts?concept=微积分` → 返回相关概念列表（占位）
- `GET /knowledge/documents/{documentId}/graph` → 返回文档子图（nodes/edges）

#### 题目服务 Question Service (`/questions`)
- 需鉴权，内部带 Redis 缓存
- `POST /questions/generate` 请求体：`{concept|conceptId|documentId, difficulty(1-5)}`

#### 实时服务 Realtime Service (`/ws`)
- WebSocket: `/ws/session/{sessionId}` → MVP 回显会话

### 配置与环境变量 / Configuration & Environment
默认值见 `common/config/settings.py`，可通过 `.env` 覆盖。关键项：
- **JWT**: `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`
- **PostgreSQL**: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`
- **RabbitMQ/Celery**: `RABBITMQ_*`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- **Neo4j**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **MinIO**: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_SECURE`, `MINIO_BUCKET`

### 开发模式 / Development Tips
- 可在容器外单独运行某服务（示例，以认证服务为例）：
```bash
pip install -r requirements.txt
uvicorn services.auth_service.main:app --reload --port 8001
```
- 其他服务端口：8002（documents）、8003（knowledge）、8004（questions）、8005（realtime）。
- 网关转发已在 `nginx.conf` 配置，无需本地改动。

### 依赖清单（节选） / Key Dependencies
- FastAPI, Uvicorn, Pydantic
- SQLAlchemy, asyncpg
- Redis, Celery, Kombu
- Neo4j Python Driver
- MinIO Python SDK
- PyMuPDF, python-pptx（文档解析占位）

### 故障排查 / Troubleshooting
- 访问 `http://localhost:8080` 失败：确认容器均为 `healthy`，端口未被占用。
- MinIO 上传失败：校验 `MINIO_*` 配置；默认控制台 `http://localhost:9001`，账户密码见 `.env`。
- JWT 校验失败：确保请求头包含 `Authorization: Bearer <token>`，并在生产环境修改 `JWT_SECRET`。
- Neo4j 连接错误：检查 `NEO4J_PASSWORD` 与 `neo4j` 容器日志，确认 `bolt://` 端口 7687 开放。

---

## English Section

### Overview
- Multi-service backend for classroom scenarios: auth, document processing, knowledge graph, question generation, and realtime.
- Stack: FastAPI, SQLAlchemy, PostgreSQL, Redis, RabbitMQ/Celery, Neo4j, MinIO, Nginx.
- Run via Docker Compose or per-service locally for development.

### Structure
See the tree above. Key files: `docker-compose.yml`, `nginx.conf`, `requirements.txt`, and services under `services/`.

### Quick Start
1) Create `.env` (override defaults from `common/config/settings.py` as needed). See the Chinese section for sample keys.
2) Start services:
```bash
docker compose up -d --build
```
3) Health checks (through Nginx gateway at `http://localhost:8080`).

### API Gateway
- Base URL: `http://localhost:8080`
- Routes:
  - `/auth/`, `/documents/`, `/knowledge/`, `/questions/`, `/ws/` → respective services

### Auth
- Register/Login to obtain a JWT `accessToken`.
- Use header `Authorization: Bearer <token>` for protected endpoints.

### Services
- Auth: `POST /auth/register`, `POST /auth/login`.
- Documents (protected): `POST /documents/upload`, `GET /documents/{id}/status`.
- Knowledge (protected): `GET /knowledge/concepts?concept=...`, `GET /knowledge/documents/{id}/graph`.
- Questions (protected, cached): `POST /questions/generate` with `concept|conceptId|documentId` and `difficulty(1-5)`.
- Realtime: WebSocket `/ws/session/{sessionId}`.

### Configuration
Environment variables cover JWT, PostgreSQL, Redis, RabbitMQ/Celery, Neo4j, MinIO. Defaults are defined in `common/config/settings.py`.

### Troubleshooting
- Ensure containers are healthy and ports free.
- Update `JWT_SECRET` in production.
- Verify MinIO/Neo4j credentials if connectivity fails.

---

© 2025 KeShang Intelligence. For internal MVP use.


