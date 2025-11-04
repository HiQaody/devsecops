# Utilisation de la version 22 de Node.js
FROM node:22-alpine

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers package.json et package-lock.json
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie de tout le reste du code
COPY . .

ARG CORS_ORIGIN
ARG DATABASE_URL
ARG JWT_SECRET
ARG PORT
ARG SALT_ROUNDS

ENV CORS_ORIGIN=$CORS_ORIGIN
ENV DATABASE_URL=$DATABASE_URL
ENV JWT_SECRET=$JWT_SECRET
ENV PORT=$PORT
ENV SALT_ROUNDS=$SALT_ROUNDS

# Génération du schéma Prisma
RUN npx prisma generate

# Exposition du port 9095
EXPOSE 9095

# Lancement de l'application
CMD ["npm", "start"]