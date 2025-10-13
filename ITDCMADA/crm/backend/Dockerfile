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
WORKDIR /app/app

COPY --from=base /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app /app

ARG DB_USER
ARG DB_PASS
ARG DB_NAME
ARG DB_HOST
ARG DB_PORT
ARG DATABASE_URL
ARG SMTP_HOST
ARG SMTP_PORT
ARG SENDER_EMAIL
ARG SENDER_PASSWORD
ARG PORT

ENV DB_USER=${DB_USER} \
    DB_PASS=${DB_PASS} \
    DB_NAME=${DB_NAME} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    DATABASE_URL=${DATABASE_URL} \
    SMTP_HOST=${SMTP_HOST} \
    SMTP_PORT=${SMTP_PORT} \
    SENDER_EMAIL=${SENDER_EMAIL} \
    SENDER_PASSWORD=${SENDER_PASSWORD} \
    PORT=${PORT}

EXPOSE 3143

# ⚠️ On exécute main:app (plus besoin de "app.main")
CMD uvicorn main:app --host 0.0.0.0 --port 3143