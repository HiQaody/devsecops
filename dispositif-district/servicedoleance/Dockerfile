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
ARG DB_USERNAME=""
ARG DB_PASSWORD=""
ARG BASE_URL=""
ARG DB_DATABASE=""
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_USERNAME=${DB_USERNAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV BASE_URL=${BASE_URL}
ENV DB_DATABASE=${DB_DATABASE}
ENV PORT=5030

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5030

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}"]