FROM node:22-alpine AS builder

WORKDIR /app

# Installer les dépendances nécessaires
RUN apk add --no-cache openssl ca-certificates g++ make python3 git

# Copier les fichiers package*.json
COPY package*.json ./

# Installer les dépendances npm
RUN npm ci --legacy-peer-deps

# Copier tout le code source
COPY . .

ARG EMAIL_USER
ARG EMAIL_PASS
ARG MINIO_ENDPOINT
ARG MINIO_PORT
ARG MINIO_BUCKET
ARG MINIO_ROOT_USER
ARG MINIO_ROOT_PASSWORD
ARG CLERK_PUBLISHABLE_KEY
ARG CLERK_SECRET_KEY
ARG CLERK_ISSUER
ARG CLERK_JWKS_URL
ARG DATABASE_URL
ARG PORT

ENV \
  EMAIL_USER=${EMAIL_USER} \
  EMAIL_PASS=${EMAIL_PASS} \
  MINIO_ENDPOINT=${MINIO_ENDPOINT} \
  MINIO_PORT=${MINIO_PORT} \
  MINIO_BUCKET=${MINIO_BUCKET} \
  MINIO_ROOT_USER=${MINIO_ROOT_USER} \
  MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD} \
  CLERK_PUBLISHABLE_KEY=${CLERK_PUBLISHABLE_KEY} \
  CLERK_SECRET_KEY=${CLERK_SECRET_KEY} \
  CLERK_ISSUER=${CLERK_ISSUER} \
  CLERK_JWKS_URL=${CLERK_JWKS_URL} \
  DATABASE_URL=${DATABASE_URL} \
  PORT=${PORT}


# Générer les fichiers Prisma
RUN npx prisma generate

# Appliquer les migrations de Prisma
RUN npx prisma migrate deploy

# Copier les fichiers générés par Prisma
RUN mkdir -p generated/prisma && cp -r node_modules/.prisma/client generated/prisma

RUN npm run build


# Créer le fichier d'entrée
RUN printf '#!/bin/sh\nset -e\nif [ -n "$DATABASE_URL" ]; then npx prisma migrate deploy || true; fi\nexec node dist/main.js --port ${PORT:-3145}\n' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Étape de production
FROM node:22-alpine AS runner

WORKDIR /app

# Installer les dépendances nécessaires pour la production
RUN apk add --no-cache openssl ca-certificates

# Définir l'environnement de production
ENV NODE_ENV=production PORT=3145

# Copier les fichiers de build depuis l'étape builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/generated ./generated
COPY --from=builder /app/entrypoint.sh ./entrypoint.sh

# Rendre le fichier d'entrée exécutable
RUN chmod +x ./entrypoint.sh

# Exposer le port
EXPOSE 3145

# Utiliser un utilisateur non-root
USER node

# Lancer l'application avec le script d'entrée
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

