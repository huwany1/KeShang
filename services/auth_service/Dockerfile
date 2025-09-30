# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY common ./common
COPY services/auth_service ./services/auth_service

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "services.auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
