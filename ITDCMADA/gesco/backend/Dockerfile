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
ARG FRONTEND_URL
ARG MINIO_URL
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG GOOGLE_CLIENT_ID
ARG GOOGLE_CLIENT_SECRET
ARG GOOGLE_REDIRECT_URI
ARG SECRET_KEY
ARG MAIL_USERNAME
ARG MAIL_PASSWORD
ARG MAIL_FROM
ARG MAIL_SERVER
ARG MAIL_PORT
ARG PORT

ENV DATABASE_URL=${DATABASE_URL} \
    FRONTEND_URL=${FRONTEND_URL} \
    MINIO_URL=${MINIO_URL} \
    MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY} \
    MINIO_SECRET_KEY=${MINIO_SECRET_KEY} \
    GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID} \
    GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET} \
    GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI} \
    SECRET_KEY=${SECRET_KEY} \
    MAIL_USERNAME=${MAIL_USERNAME} \
    MAIL_PASSWORD=${MAIL_PASSWORD} \
    MAIL_FROM=${MAIL_FROM} \
    MAIL_SERVER=${MAIL_SERVER} \
    MAIL_PORT=${MAIL_PORT} \
    PORT=${PORT}

EXPOSE 3141

# ⚠️ On exécute main:app (plus besoin de "app.main")
CMD uvicorn app.main:app --host 0.0.0.0 --port 3141