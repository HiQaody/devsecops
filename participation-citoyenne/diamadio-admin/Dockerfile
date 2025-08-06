# Étape 1 : Construire l'application
FROM node:20-slim AS builder
WORKDIR /app

# Copier les fichiers nécessaires pour installer les dépendances
COPY package.json package-lock.json ./
RUN npm install

# Copier le reste du code source
COPY . .

# Construire l'application React.js
RUN npm run build

# Étape 2 : Image finale pour l'exécution
FROM node:20-alpine AS runner
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour exécuter l'application
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Définir les variables d'environnement
ENV NODE_ENV production
ENV PORT 4002

# Exposer le port
EXPOSE 4002

# Utiliser un utilisateur non-root par sécurité
USER node

# Lancer l'application
CMD ["npx", "serve", "-s", "build", "-l", "4002"]