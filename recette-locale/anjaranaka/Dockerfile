# Étape 1 : Construction de l'application
FROM node:20-slim AS builder
WORKDIR /app

# Copier les fichiers nécessaires pour installer les dépendances
COPY package.json package-lock.json ./
RUN npm ci

# Copier le reste du code source
COPY . .

# Définir des variables d'environnement par défaut pour la build
ARG VITE_API_URL_SERVICERECETTE="http://localhost:9093"
ARG VITE_API_URL_SERVICECITOYEN="http://localhost:9094"
ARG VITE_API_URL_SERVICEAUTH="http://localhost:9095"

# Injecter ces valeurs dans le build si nécessaire (si Vite les utilise au build)
ENV VITE_API_URL_SERVICERECETTE=${VITE_API_URL_SERVICERECETTE}
ENV VITE_API_URL_SERVICECITOYEN=${VITE_API_URL_SERVICECITOYEN}
ENV VITE_API_URL_SERVICEAUTH=${VITE_API_URL_SERVICEAUTH}

# Construire l'application Vite
RUN npm run build

# Étape 2 : Image finale pour l'exécution
FROM node:20-alpine AS runner
WORKDIR /app

# Installer un serveur léger pour servir Vite
RUN npm install -g serve

# Copier uniquement les fichiers nécessaires pour exécuter l'application
COPY --from=builder /app/dist ./dist

# Définir les variables d'environnement avec possibilité de surcharge lors du run
ENV VITE_API_URL_SERVICERECETTE=${VITE_API_URL_SERVICERECETTE}
ENV VITE_API_URL_SERVICECITOYEN=${VITE_API_URL_SERVICECITOYEN}
ENV VITE_API_URL_SERVICEAUTH=${VITE_API_URL_SERVICEAUTH}
ENV NODE_ENV=production
ENV PORT=4005

# Exposer le port
EXPOSE 4005

# Utiliser un utilisateur non-root par sécurité
USER node

# Définir le point d'entrée et la commande par défaut
ENTRYPOINT ["serve", "-s", "dist"]
CMD ["-l", "4005"]
