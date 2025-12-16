# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies using pnpm
RUN npm install -g pnpm \
    && pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Installer uniquement les dépendances de production
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm \
    && pnpm install --prod --frozen-lockfile

# Copier le build depuis le stage précédent
COPY --from=builder /app/dist ./dist

# Copier la configuration Prisma
COPY prisma ./prisma

# Variables d'environnement
ARG DATABASE_URL
ARG KEYCLOAK_URL
ARG KEYCLOAK_REALM
ARG KEYCLOAK_CLIENT_ID
ARG KEYCLOAK_CLIENT_SECRET
ARG KEYCLOAK_POLICY_ENFORCEMENT

ARG MINIO_ENDPOINT
ARG MINIO_PORT
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG MINIO_BUCKET_NAME
ARG MINIO_USE_SSL
ARG MINIO_ENABLED

ARG THROTTLER_LIMIT=15
ARG FRONTEND_ORIGINS
ARG BACKEND_URL

ENV DATABASE_URL=${DATABASE_URL}
ENV KEYCLOAK_URL=${KEYCLOAK_URL}
ENV KEYCLOAK_REALM=${KEYCLOAK_REALM}
ENV KEYCLOAK_CLIENT_ID=${KEYCLOAK_CLIENT_ID}
ENV KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}

ENV MINIO_ENDPOINT=${MINIO_ENDPOINT}
ENV MINIO_PORT=${MINIO_PORT}
ENV MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
ENV MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
ENV MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}
ENV MINIO_USE_SSL=${MINIO_USE_SSL}
ENV MINIO_ENABLED=${MINIO_ENABLED}

ENV THROTTLER_LIMIT=${THROTTLER_LIMIT}
ENV FRONTEND_ORIGINS=${FRONTEND_ORIGINS}
ENV BACKEND_URL=${BACKEND_URL}

ENV PORT=5002
ENV NODE_ENV=production

EXPOSE 5002

# Run Prisma migrations
RUN npx prisma generate

CMD ["node", "dist/src/main"]