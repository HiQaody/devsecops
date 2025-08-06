FROM node:20-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --legacy-peer-deps


# Copier tous les fichiers du projet
COPY . .

# Créer un build statique pour l'application (supposons que c'est un projet React par exemple)
RUN npm run build

# Utilisation de l'ARG pour définir la variable d'environnement pour DATABASE_URL
ARG POSTGRES_HOST=""
ARG POSTGRES_PORT=""
ARG POSTGRES_DB=""
ARG POSTGRES_USER=""
ARG POSTGRES_PASSWORD=""
ARG JWT_SECRET=""
ARG JWT_EXPIRES=""
ARG CORS_ORIGIN=""
ARG REDIS_HOST=""
ARG REDIS_PORT=6379
ARG REDIS_PASSWORD=""
# Définir les variables d'environnement pour l'application
ENV POSTGRES_HOST=${POSTGRES_HOST}
ENV POSTGRES_PORT=${POSTGRES_PORT}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV JWT_SECRET=${JWT_SECRET}
ENV JWT_EXPIRES=${JWT_EXPIRES}
ENV CORS_ORIGIN=${CORS_ORIGIN}
ENV REDIS_HOST=${REDIS_HOST}
ENV REDIS_PORT=${REDIS_PORT}
ENV REDIS_PASSWORD=${REDIS_PASSWORD}
# Définir le port par défaut pour l'application
ENV PORT=8046

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 8046

# Utilisation de 'npm run start:prod' pour démarrer l'application
CMD ["npm", "run", "start:prod"]