# ---- Étape 1 : Build base ----
    FROM python:3.11-slim AS base

    # Installer dépendances système minimales (psycopg2, asyncpg et cie aiment bien)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
     && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /app
    
    # Copier requirements et installer
    COPY requirements.txt .
    
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copier le code
    COPY . .
    
    # ---- Étape 2 : Run ----
    FROM python:3.11-slim AS runner
    
    WORKDIR /app
    
    # Copier les libs déjà installées
    COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
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
    
    # Variables d’env par défaut (surchageables dans docker-compose ou kubernetes)
    ENV DB_USER=${DB_USER} \
        DB_PASS=${DB_PASS} \
        DB_NAME=${DB_NAME} \
        DB_HOST=${DB_HOST} \
        DB_PORT=${DB_PORT} \
        DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME} \
        SMTP_HOST=${SMTP_HOST} \
        SMTP_PORT=${SMTP_PORT} \
        SENDER_EMAIL=${SENDER_EMAIL} \
        SENDER_PASSWORD=${SENDER_PASSWORD} \
        PORT=${PORT}
    
    EXPOSE ${PORT}
    
    # Lancer uvicorn en mode prod
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
    