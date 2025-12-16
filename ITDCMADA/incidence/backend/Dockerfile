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


ARG SUPABASE_URL
ARG SUPABASE_KEY
ARG SECRET_KEY
ARG ALGORITHM
ARG ACCESS_TOKEN_EXPIRE_MINUTES
ARG SMTP_SERVER
ARG SMTP_PORT
ARG FROM_EMAIL
ARG PASSWORD
ARG GOOGLE_APPLICATION_CREDENTIALS
ARG FACEBOOK_APP_ID
ARG FACEBOOK_APP_SECRET
ARG API_BASE_URL
ARG FRONTEND_URL
ARG PORT

ENV SUPABASE_URL=${SUPABASE_URL} \
    SUPABASE_KEY=${SUPABASE_KEY} \
    SECRET_KEY=${SECRET_KEY} \
    ALGORITHM=${ALGORITHM} \
    ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES} \
    SMTP_SERVER=${SMTP_SERVER} \
    SMTP_PORT=${SMTP_PORT} \
    FROM_EMAIL=${FROM_EMAIL} \
    PASSWORD=${PASSWORD} \
    GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} \
    FACEBOOK_APP_ID=${FACEBOOK_APP_ID} \
    FACEBOOK_APP_SECRET=${FACEBOOK_APP_SECRET} \
    API_BASE_URL=${API_BASE_URL} \
    FRONTEND_URL=${FRONTEND_URL} \
    PORT=${PORT}

EXPOSE 3157

# ⚠️ On exécute main:app (plus besoin de "app.main")
CMD uvicorn app.main:app --host 0.0.0.0 --port 3157