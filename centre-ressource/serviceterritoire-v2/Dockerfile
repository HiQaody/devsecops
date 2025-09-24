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
ARG POSTGRES_HOST=""
ARG POSTGRES_PORT=""
ARG POSTGRES_DB=""
ARG POSTGRES_USER=""
ARG POSTGRES_PASSWORD=""
ENV POSTGRES_HOST=${POSTGRES_HOST}
ENV POSTGRES_PORT=${POSTGRES_PORT}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV PORT=5039

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5039

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}"]