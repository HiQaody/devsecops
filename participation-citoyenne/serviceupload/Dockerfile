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
ARG MINIO_END_POINT
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG MINIO_PORT
ARG MINIO_SSL
ARG MINIO_BUCKET_NAME

ENV MINIO_END_POINT=${MINIO_END_POINT}
ENV MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
ENV MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
ENV MINIO_PORT=${MINIO_PORT}
ENV MINIO_SSL=${MINIO_SSL}
ENV MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}
ENV PORT=5012

# Exposer le port que nous utiliserons pour le serveur 'serve'
EXPOSE 5012

# Command to run the application
CMD ["node", "dist/main", "--port", "${PORT}"]