FROM node:22-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --legacy-peer-deps
# Copier tous les fichiers du projet
COPY . .

# Utilisation de l'ARG pour définir la variable d'environnement
ARG POSTGRES_HOST=""
ARG POSTGRES_PORT=""
ARG POSTGRES_USER=""
ARG POSTGRES_PASSWORD=""
ARG POSTGRES_DB=""

# Définir les variables d'environnement
ENV POSTGRES_HOST=$POSTGRES_HOST
ENV POSTGRES_PORT=$POSTGRES_PORT
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_DB=$POSTGRES_DB
ENV PORT=5003

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5003

# Utilisation de 'npm run start:prod' pour démarrer l'application
CMD ["npm", "run", "start"]