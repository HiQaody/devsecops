# ---- Étape 1 : Build base ----
FROM python:3.12-slim AS base

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
FROM python:3.12-slim AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# ⚠️ On change ici le répertoire de travail
WORKDIR /app

COPY --from=base /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app /app


ARG DATABASE_URL
#configuration minio
ARG MINIO_ENDPOINT
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG MINIO_BUCKET
ARG MINIO_SECURE
ARG PORT

ARG CORS_ORIGINS
ARG CORS_METHODS
ARG CORS_HEADERS
ARG CORS_CREDENTIALS

ENV DATABASE_URL=${DATABASE_URL} \
    MINIO_ENDPOINT=${MINIO_ENDPOINT} \
    MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY} \
    MINIO_SECRET_KEY=${MINIO_SECRET_KEY} \
    MINIO_BUCKET=${MINIO_BUCKET} \
    MINIO_SECURE=${MINIO_SECURE} \
    CORS_ORIGINS=${CORS_ORIGINS} \
    CORS_METHODS=${CORS_METHODS} \
    CORS_HEADERS=${CORS_HEADERS} \
    CORS_CREDENTIALS=${CORS_CREDENTIALS} \
    PORT=${PORT}

EXPOSE 3148


CMD uvicorn app.main:app --host 0.0.0.0 --port 3148