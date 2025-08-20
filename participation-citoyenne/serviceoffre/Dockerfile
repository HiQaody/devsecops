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
ARG DB_HOST=""
ARG DB_PORT=""
ARG DB_USER=""
ARG DB_PASSWORD=""
ARG DB_NAME=""
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_NAME=${DB_NAME}
ENV PORT=5007

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5007

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}"]