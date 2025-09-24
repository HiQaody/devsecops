# Étape 1 : build des dépendances
FROM python:3.12-slim AS build

# Installer dépendances système nécessaires à psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier uniquement requirements.txt pour utiliser le cache Docker
COPY requirements.txt .

# Upgrade pip + installer dépendances
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier le code source (avec permissions)
COPY --chown=app:app . .

# Étape 2 : runner
FROM python:3.12-slim

# Installer dépendances d'exécution
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app

# Copier les dépendances Python depuis le build
COPY --from=build /usr/local /usr/local

# Copier le code source avec les bonnes permissions
COPY --from=build --chown=app:app /app .

# Créer le répertoire uploads avec les permissions
RUN mkdir -p uploads && chown app:app uploads

# Exposer le port FastAPI
EXPOSE 3141

# Changer d’utilisateur
USER app

# Lancer FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3141"]
