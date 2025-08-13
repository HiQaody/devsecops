# Étape 1 : Construire l'application
FROM node:20-slim AS builder
WORKDIR /app

# Copier les fichiers nécessaires pour installer les dépendances
COPY package.json package-lock.json ./
RUN npm ci && npm cache clean --force

# Copier le reste du code source
COPY . .

# Construire l'application Vite (React)
RUN npm run build

# Étape 2 : Image finale pour l'exécution
FROM node:20-alpine AS runner
WORKDIR /app

# Copier uniquement les fichiers nécessaires pour exécuter l'application
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Définir les variables d'environnement
ARG VITE_APP_SERVICENOTIFICATION=
ARG VITE_APP_SERVICEAUTH=
ARG VITE_APP_REGISTER_URL=

ENV VITE_APP_SERVICENOTIFICATION=${VITE_APP_SERVICENOTIFICATION}
ENV VITE_APP_SERVICEAUTH=${VITE_APP_SERVICEAUTH}
ENV VITE_APP_REGISTER_URL=${VITE_APP_REGISTER_URL}

ENV NODE_ENV production
ENV PORT 4008

# Exposer le port
EXPOSE 4008

# Utiliser un utilisateur non-root par sécurité
USER node

# Lancer l'application
CMD ["npx", "serve", "-s", "dist", "-l", "4008"]