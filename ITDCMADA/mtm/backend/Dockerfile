# ---- Étape 1 : Build base ----
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ---- Étape 2 : Run ----
FROM python:3.11-slim AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libxml2 \
    libxslt1.1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app/app

COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app /app

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ARG POSTGRES_SERVER
ARG POSTGRES_PORT
ARG SECRET_KEY
ARG ACCESS_TOKEN_EXPIRE_MINUTES
ARG MINIO_ENDPOINT
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG MINIO_BUCKET
ARG MINIO_SECURE
ARG TINIFY_API_KEY
ARG PORT

ENV POSTGRES_USER=${POSTGRES_USER} \
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    POSTGRES_DB=${POSTGRES_DB} \
    POSTGRES_SERVER=${POSTGRES_SERVER} \
    POSTGRES_PORT=${POSTGRES_PORT} \
    SECRET_KEY=${SECRET_KEY} \
    ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES} \
    MINIO_ENDPOINT=${MINIO_ENDPOINT} \
    MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY} \
    MINIO_SECRET_KEY=${MINIO_SECRET_KEY} \
    MINIO_BUCKET=${MINIO_BUCKET} \
    MINIO_SECURE=${MINIO_SECURE} \
    TINIFY_API_KEY=${TINIFY_API_KEY} \
    PORT=${PORT}

EXPOSE 3146

# ⚠️ On exécute main:app (plus besoin de "app.main")
CMD uvicorn main:app --host 0.0.0.0 --port 3146
