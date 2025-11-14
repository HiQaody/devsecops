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
ARG ADMIN_EMAIL
ARG ADMIN_PASSWORD
ARG SECRET_KEY
ARG DEBUG
ARG PORT

ENV DATABASE_URL=${DATABASE_URL} \
    FRONTEND_URL=${FRONTEND_URL} \
    ADMIN_EMAIL=${ADMIN_EMAIL} \
    ADMIN_PASSWORD=${ADMIN_PASSWORD} \
    SECRET_KEY=${SECRET_KEY} \
    DEBUG=${DEBUG} \
    PORT=${PORT}

EXPOSE 3148

CMD uvicorn app.main:app --host 0.0.0.0 --port 3148