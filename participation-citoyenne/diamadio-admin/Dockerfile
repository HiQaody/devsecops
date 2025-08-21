# Étape 1 : Construire l'application
FROM node:20-slim AS builder
WORKDIR /app

# Copier les fichiers nécessaires pour installer les dépendances
COPY package.json package-lock.json ./
RUN npm install && npm cache clean --force

# Copier le reste du code source
COPY . .

# Définir la variable d'environnement build-time
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Construire l'application Vite avec la variable injectée
RUN npm run build

# Étape 2 : Image finale pour l'exécution
FROM node:20-alpine AS runner
WORKDIR /app

# Installer "serve" pour servir les fichiers statiques
RUN npm install -g serve

# Copier uniquement le build final
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./package.json

# Définir l'environnement runtime
ENV NODE_ENV production
ENV PORT 4002

# Exposer le port
EXPOSE 4002

# Utiliser un utilisateur non-root
USER node

# Lancer l'application
CMD ["serve", "-s", "dist", "-l", "4002"]
