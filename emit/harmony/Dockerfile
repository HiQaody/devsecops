FROM node:20-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --legacy-peer-deps

# Utilisation de l'ARG pour définir la variable d'environnement pour DATABASE_URL
ARG DB_USER=""
ARG DB_PORT=""
ARG DB_NAME=""
ARG DB_HOST=""
ARG DB_PASSWORD=""
ARG JWT_SECRET=""
ARG JWT_EXPIRES=""
ARG END_DATE=""
ARG CLIENT_URL=""
# Définir les variables d'environnement pour l'application
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV JWT_SECRET=${JWT_SECRET}
ENV JWT_EXPIRES=${JWT_EXPIRES}
ENV END_DATE=${END_DATE}
ENV CLIENT_URL=${CLIENT_URL}

# Copier tous les fichiers du projet
COPY . .

RUN node addAmin.js


# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5000

# Utilisation de 'npm run start:prod' pour démarrer l'application
CMD ["npm", "start"]
