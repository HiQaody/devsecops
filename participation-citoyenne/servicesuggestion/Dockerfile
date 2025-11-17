FROM node:20-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --production


# Copier tous les fichiers du projet
COPY . .


# Utilisation de l'ARG pour définir la variable d'environnement pour DATABASE_URL
ARG DB_HOST=""
ARG DB_PORT=""
ARG DB_DATABASENAME=""
ARG DB_USER_NAME=""
ARG DB_PASSWORD=""
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_DATABASENAME=${DB_DATABASENAME}
ENV DB_USER_NAME=${DB_USER_NAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV NODE_ENV=production
ENV PORT=5009

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5009

# Utilisation de 'npm run start:prod' pour démarrer l'application
CMD ["npm", "run", "start"]