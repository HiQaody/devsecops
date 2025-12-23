FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Ajouter les arguments pour la construction
ARG NEXT_PUBLIC_API_BASE_URL

# Définir les variables d'environnement
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

RUN npm run build

EXPOSE 3160

# Copier le script d'initialisation et s'assurer qu'il est exécutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]