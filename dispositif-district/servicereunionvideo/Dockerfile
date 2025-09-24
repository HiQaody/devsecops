FROM node:20-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install


# Copier tous les fichiers du projet
COPY . .

# Créer un build statique pour l'application (supposons que c'est un projet React par exemple)
RUN npm run build

# Utilisation de l'ARG pour définir la variable d'environnement pour DATABASE_URL
ARG DATABASE_HOST=""
ARG DATABASE_PORT=""
ARG DATABASE_USER=""
ARG DATABASE_PASSWORD=""
ARG API_GATEWAY_URL=""
ARG DATABASE_NAME=""

ENV DATABASE_HOST=${DATABASE_HOST}
ENV DATABASE_PORT=${DATABASE_PORT}
ENV DATABASE_USER=${DATABASE_USER}
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD}
ENV API_GATEWAY_URL=${API_GATEWAY_URL}
ENV DATABASE_NAME=${DATABASE_NAME}
ENV NODE_ENV=production
ENV PORT=5035

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5035

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}", "--env", "${NODE_ENV}"]