## Contributing Guide

Thank you for contributing to KeShang Intelligence Backend (MVP). This guide explains how to propose changes and keep the codebase consistent.

### Ground Rules
- Write production-quality code following KISS and SOLID principles.
- Reuse existing utilities in `common/` where possible; avoid duplication.
- Naming:
  - Variables/functions: camelCase (e.g., `buildDatabaseUrl`)
  - Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
  - Classes: PascalCase (e.g., `AuthService`)
- Comments:
  - Every function should have a purpose docstring (inputs, outputs, role)
  - Add detailed comments for complex logic explaining the intent
  - Module/class-level docstrings for large code blocks
- Formatting: match existing style; prefer multi-line clarity over clever one-liners.

### Branch & Commit
- Branch model: `feature/<topic>`, `fix/<topic>`, `chore/<topic>`
- Conventional Commits:
  - `feat: add question generation adapter`
  - `fix: handle token verification errors`
  - `docs: update README for gateway paths`
  - `chore: bump dependencies`

### Development Workflow
1. Create a topic branch from `master`
2. Run the stack (Docker) or local services as needed
3. Add/modify code and tests (if applicable)
4. Ensure linting/type checks pass
5. Open a PR with a clear description and testing notes

### Running Locally
- Python 3.11+
- Install deps: `pip install -r requirements.txt`
- Start a service (example): `uvicorn services.auth_service.main:app --reload --port 8001`
- Celery worker: `celery -A services.document_service.worker worker -l INFO`
- Infra: use `docker compose up -d` or run individual containers for Postgres/Redis/RabbitMQ/Neo4j/MinIO

### API & Auth
- Use the collections in `docs/collections/` for Postman/Thunder
- Obtain token by calling `POST /auth/login`, then set header `Authorization: Bearer <token>`

### Security
- Never commit secrets. Use `.env` and rely on defaults matching `docker-compose.yml`
- JWT secret should be changed in non-dev environments

### Code Review Checklist
- Clear purpose docstrings and module/class headers
- Proper error handling and early returns for edge cases
- No dead code; no ad-hoc debugging prints
- Respect service boundaries and shared utilities


