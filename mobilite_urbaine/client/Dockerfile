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
ARG VITE_API_BASE_URL=
ARG VITE_API_BASE_URL_DEFAULT
ARG VITE_IZOTRA_URL
ARG VITE_REGISTER_URL
ARG VITE_FORGOT_PWD_URL
ARG VITE_OSRM_URL
ARG VITE_TERRITORY_V2_URL
ARG VITE_APK_FILE_NAME
ARG VITE_APP_ID
ARG VITE_APP_MOBILE_ID

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_API_BASE_URL_DEFAULT=${VITE_API_BASE_URL_DEFAULT}
ENV VITE_IZOTRA_URL=${VITE_IZOTRA_URL}
ENV VITE_REGISTER_URL=${VITE_REGISTER_URL}
ENV VITE_FORGOT_PWD_URL=${VITE_FORGOT_PWD_URL}
ENV VITE_OSRM_URL=${VITE_OSRM_URL}
ENV VITE_TERRITORY_V2_URL=${VITE_TERRITORY_V2_URL}
ENV VITE_APK_FILE_NAME=${VITE_APK_FILE_NAME}
ENV VITE_APP_ID=${VITE_APP_ID}
ENV VITE_APP_MOBILE_ID=${VITE_APP_MOBILE_ID}

ENV NODE_ENV production 
ENV PORT 4007

# Exposer le port
EXPOSE 4007

# Utiliser un utilisateur non-root par sécurité
USER node

# Lancer l'application
CMD ["npx", "serve", "-s", "dist", "-l", "4007"]