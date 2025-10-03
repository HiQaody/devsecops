FROM node:22-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --legacy-peer-deps
# Copier tous les fichiers du projet
COPY . .

# Utilisation de l'ARG pour définir la variable d'environnement
ARG DB_HOST=""
ARG DB_PORT=""
ARG DB_USERNAME=""
ARG DB_PASSWORD=""
ARG DB_DATABASE=""

# Définir les variables d'environnement
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_USERNAME=$DB_USERNAME
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_DATABASE=$DB_DATABASE
ENV PORT=5015

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5015

# Utilisation de 'npm run start:prod' pour démarrer l'application
CMD ["npm", "run", "start"]