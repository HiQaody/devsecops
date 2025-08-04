# Étape 1 : Construire l'application
FROM node:22-slim AS builder
WORKDIR /app

# Copier les fichiers nécessaires pour installer les dépendances
COPY package.json package-lock.json ./
RUN npm ci && npm cache clean --force

# Copier le reste du code source
COPY . .

# Construire l'application Vite (React)
RUN npm run build

# Étape 2 : Image finale pour l'exécution
FROM node:22-alpine AS runner
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour exécuter l'application
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}
# Définir les variables d'environnement
ENV NODE_ENV production
ENV PORT 4006

# Exposer le port
EXPOSE 4006

# Utiliser un utilisateur non-root par sécurité
USER node

# Lancer l'application
CMD ["npx", "serve", "-s", "dist", "-l", "4006"]