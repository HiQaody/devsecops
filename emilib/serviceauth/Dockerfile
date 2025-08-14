FROM node:22-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --legacy-peer-deps


# Copier tous les fichiers du projet
COPY . .

# Créer un build statique pour l'application (supposons que c'est un projet React par exemple)
RUN npm run build

# Utilisation de l'ARG pour définir la variable d'environnement pour DATABASE_URL
ARG DATABASE_HOST=""
ARG DATABASE_PORT=""
ARG DATABASE_NAME=""
ARG DATABASE_USERNAME=""
ARG DATABASE_PASSWORD=""
ARG JWT_SECRET=""
ARG API_URL=""
ARG MAIL_HOST=""
ARG MAIL_PORT=""
ARG MAIL_USERNAME=""
ARG MAIL_PASSWORD=""
ARG MAIL_SSL_TRUST=""
# Définir les variables d'environnement pour l'application
ENV DATABASE_HOST=${DATABASE_HOST}
ENV DATABASE_PORT=${DATABASE_PORT}
ENV DATABASE_NAME=${DATABASE_NAME}
ENV DATABASE_USERNAME=${DATABASE_USERNAME}
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD}
ENV JWT_SECRET=${JWT_SECRET}
ENV API_URL=${API_URL}
ENV MAIL_HOST=${MAIL_HOST}
ENV MAIL_PORT=${MAIL_PORT}
ENV MAIL_USERNAME=${MAIL_USERNAME}
ENV MAIL_PASSWORD=${MAIL_PASSWORD}
ENV MAIL_SSL_TRUST=${MAIL_SSL_TRUST}
# Définir le port par défaut pour l'application
ENV PORT=9097

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 9097

# Utilisation de 'npm run start:prod' pour démarrer l'application
CMD ["npm", "run", "start:prod"]