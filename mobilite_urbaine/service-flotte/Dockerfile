# Utiliser une image Node.js officielle comme base
FROM node:22-slim

# Installer les dépendances système pour `wait-for-it`
RUN apt-get update && apt-get install -y wait-for-it

# Créer le répertoire de travail dans le conteneur
WORKDIR /app

# Définir les arguments de build
ARG DB_USER=postgres
ARG DB_PASSWORD=postgres
ARG DB_NAME=postgres
ARG DB_HOST=postgres
ARG DB_PORT=5432
ARG GATEWAY_BASE_URL=http://gateway:5000
ARG GATEWAY_TIMEOUT_MS=120000

# Définir les variables d'environnement en utilisant les ARG
ENV NODE_ENV=production 
ENV DB_USER=${DB_USER} 
ENV DB_PASSWORD=${DB_PASSWORD} 
ENV DB_NAME=${DB_NAME} 
ENV DB_HOST=${DB_HOST} 
ENV DB_PORT=${DB_PORT}
ENV GATEWAY_BASE_URL=${GATEWAY_BASE_URL}
ENV GATEWAY_TIMEOUT_MS=${GATEWAY_TIMEOUT_MS}

# Copier les fichiers de configuration de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Installer sequelize-cli globalement pour éviter les problèmes d'exécution
RUN npm install -g sequelize-cli

# Copier le reste des fichiers du projet
COPY . .

# Exposer le port sur lequel l'application s'exécute
EXPOSE 5021

# Attendre que la base de données soit prête avant de lancer les migrations
CMD ["sh", "-c", "wait-for-it ${DB_HOST}:${DB_PORT} -- npx sequelize-cli db:migrate && node server.js"]
