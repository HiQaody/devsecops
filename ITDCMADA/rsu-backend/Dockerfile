# Étape 1 : build des dépendances
FROM python:3.10-slim AS build
# Installer dépendances système nécessaires à psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app
# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copier le code source
COPY --chown=app:app . .

# Étape 2 : runner
FROM python:3.10-slim
# Installer dépendances d'exécution
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app
# Copier les dépendances depuis l'étape build
COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=build /usr/local/bin /usr/local/bin
# Copier le code source avec les permissions appropriées
COPY --from=build --chown=app:app /app .
# Créer le répertoire uploads avec les permissions appropriées
RUN mkdir -p uploads && chown app:app uploads
# Exposer le port FastAPI
EXPOSE 3138
# Changer d'utilisateur
USER app
# Lancer FastAPI avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3138"]