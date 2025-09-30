## KeShang Classroom Backend (MVP)

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
![Build](https://img.shields.io/badge/build-docker--compose-brightgreen)
![License](https://img.shields.io/badge/license-internal-lightgrey)
![Status](https://img.shields.io/badge/status-MVP-orange)

Microservice-based backend for classroom scenarios: authentication, courseware ingestion, knowledge graph queries, question generation, and realtime interactions. All services are exposed behind an Nginx API gateway.

---

### Highlights
- **Auth**: Email sign-up and login with JWT issuance and verification
- **Document pipeline**: Upload PDF/PPT, asynchronously extract concepts/relations, persist to PostgreSQL and Neo4j
- **Knowledge queries**: Retrieve subgraphs by concept or document for frontend visualization
- **Question generation**: Bloom-level guided, local/remote adapters with caching and quality checks
- **Realtime**: WebSocket placeholder for classroom sessions (extensible for buzz-in, polling, etc.)
- **Unified gateway**: Nginx handles routing, CORS, and rate limiting

---

### Tech Stack
- Web: FastAPI, Pydantic, Uvicorn
- Data: PostgreSQL, SQLAlchemy (Async), Redis
- Queue: RabbitMQ, Celery
- Graph DB: Neo4j
- Object Storage: MinIO (local dev)
- Parsing: PyMuPDF, python-pptx (MVP placeholders)
- Ops: Docker Compose, Nginx

---

### Directory Layout
```
d:/KeShang-intelligence/
  common/                  # Shared libs: config/db/cache/storage/graph/mq/security
  services/
    auth_service/          # Sign-up/login
    document_service/      # Upload/status + Celery pipeline
    knowledge_service/     # Knowledge graph queries
    question_service/      # Question generation with cache/adapters
    realtime_service/      # WebSocket placeholder
  docker-compose.yml       # One-click infra + services (Postgres/Redis/RabbitMQ/Neo4j/MinIO/Nginx)
  nginx.conf               # API gateway
  requirements.txt         # Python deps
```

---

### Architecture & Ports
- API Gateway: http://localhost:8080
  - `/auth` -> Auth Service (8001)
  - `/documents` -> Document Service (8002)
  - `/knowledge` -> Knowledge Service (8003)
  - `/questions` -> Question Service (8004)
  - `/ws` -> Realtime Service (WebSocket, 8005)
- Infra:
  - PostgreSQL: 5432
  - Redis: 6379
  - RabbitMQ: 5672 (Mgmt 15672)
  - Neo4j: 7474/7687
  - MinIO: 9000 (Console 9001)

---

### Quick Start (Docker)
1) Prereqs
   - Docker Desktop (with Compose)
   - Clone the repo and create `.env` in project root (see sample below)

2) Launch
```bash
docker compose up -d --build
```

3) Health checks
```bash
curl http://localhost:8080/auth/health | jq
curl http://localhost:8080/documents/health | jq
```

4) Shutdown
```bash
docker compose down -v
```

---

### `.env` sample
```dotenv
# App
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

# Service ports
AUTH_SERVICE_PORT=8001
DOCUMENT_SERVICE_PORT=8002
KNOWLEDGE_SERVICE_PORT=8003
QUESTION_SERVICE_PORT=8004
REALTIME_SERVICE_PORT=8005

# Question generation
QG_MAX_TOKENS=256
QG_DEFAULT_TEMPERATURE=0.2
QG_ADAPTER_TYPE=local   # local | remote
QG_REMOTE_URL=http://model-service:9000/generate
QG_QUALITY_MIN_SCORE=0.6
```

> Note: Code provides sensible defaults that align with `docker-compose.yml` if variables are omitted.

---

### Common APIs

- Sign-up & login (get `accessToken`)
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"t@example.com","name":"Teacher A","password":"pass1234"}'

curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"t@example.com","password":"pass1234"}'
```

- Document upload & status (requires `Authorization: Bearer <token>`)
```bash
curl -X POST http://localhost:8080/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/sample.pdf"

curl http://localhost:8080/documents/{documentId}/status \
  -H "Authorization: Bearer $TOKEN"
```

- Knowledge queries
```bash
curl "http://localhost:8080/knowledge/concepts?concept=machine%20learning" \
  -H "Authorization: Bearer $TOKEN"

curl http://localhost:8080/knowledge/documents/{documentId}/graph \
  -H "Authorization: Bearer $TOKEN"
```

- Question generation (5-minute cache)
```bash
curl -X POST http://localhost:8080/questions/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"concept":"linear regression","difficulty":3}'
```

- WebSocket (echo placeholder)
```
ws://localhost:8080/ws/session/123
```

> Note: Nginx routing has been simplified; gateway paths are now clean (e.g., `/auth/login`).

---

### Collections & Sample Token
- Postman/Thunder collections are in `docs/collections/`. After import:
  - Run "Auth / Login" to obtain and auto-save `token`
  - Subsequent protected requests will automatically use `Bearer {{token}}`
- Windows script: `scripts/get_token.ps1`
  - Usage:
    ```powershell
    pwsh -File scripts/get_token.ps1 -Email "t@example.com" -Password "pass1234"
    ```

---

### Local Dev (without Docker)
1) Python 3.11+
2) Install deps
```bash
pip install -r requirements.txt
```
3) Run a service (example: auth)
```bash
uvicorn services.auth_service.main:app --reload --port 8001
```
4) Run Celery worker (with `document_service`)
```bash
celery -A services.document_service.worker worker -l INFO
```
> Requires local instances of Postgres/Redis/RabbitMQ/Neo4j/MinIO; you can spin them up via Docker separately.

---

### Conventions
- Config: centralized in `common.config.settings.Settings`, supports `.env` with defaults
- DB access: `common.db.postgres.async_session` for FastAPI DI
- Auth dependency: `common.security.deps.jwt_auth` validates `Bearer Token`
- Storage: `common.storage.minio_client` wraps common MinIO ops
- Graph writes: `common.graph.neo4j_writer` minimal write helpers
- Tasks: `common.mq.celery_app` provides a shared Celery app

---

### Troubleshooting
- Port conflicts: tweak published ports in `docker-compose.yml` or free local ports
- MinIO errors: verify endpoint/credentials; bucket is auto-created if missing
- Neo4j auth failure: ensure `.env` `NEO4J_PASSWORD` matches Compose
- Celery broker issues: confirm `CELERY_BROKER_URL` and RabbitMQ status (15672)
- Double prefixes: adjust Nginx locations or service router prefixes

---

### License
Internal project (MVP). Add an open-source license here if applicable.


