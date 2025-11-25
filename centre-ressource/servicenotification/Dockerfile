FROM node:22-slim

WORKDIR /app

# Installer les dépendances de l'application
COPY package*.json ./

RUN npm install --legacy-peer-deps
# Copier tous les fichiers du projet
COPY . .

# Créer un build statique pour l'application (supposons que c'est un projet React par exemple)
RUN npm run build

# Utilisation de l'ARG pour définir la variable d'environnement
ARG DB_HOST=""
ARG DB_PORT=""
ARG DB_USERNAME=""
ARG DB_PASSWORD=""
ARG DB_DATABASE=""
ARG GOOGLE_CLIENT_ID=""
ARG GOOGLE_CLIENT_SECRET=""
ARG GOOGLE_REDIRECT_URI=
ARG GOOGLE_REFRESH_TOKEN=
ARG EMAIL_FROM=

# Définir les variables d'environnement
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_USERNAME=$DB_USERNAME
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_DATABASE=$DB_DATABASE
ENV GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
ENV GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
ENV GOOGLE_REDIRECT_URI=$GOOGLE_REDIRECT_URI
ENV GOOGLE_REFRESH_TOKEN=$GOOGLE_REFRESH_TOKEN
ENV EMAIL_FROM=$EMAIL_FROM
ENV PORT=5013

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5015

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}"]