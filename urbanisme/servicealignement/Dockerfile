FROM node:22-slim

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
ARG DATABASE_DB=""
ARG DATABASE_USERNAME=""
ARG DATABASE_PASSWORD=""
ENV DATABASE_HOST=${DATABASE_HOST}
ENV DATABASE_PORT=${DATABASE_PORT}
ENV DATABASE_DB=${DATABASE_DB}
ENV DATABASE_USERNAME=${DATABASE_USERNAME}
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD}
ENV PORT=5040

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5040

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}"]