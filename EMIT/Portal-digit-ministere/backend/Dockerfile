# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:24-alpine

WORKDIR /app

# Installer uniquement les dépendances de production
COPY package*.json ./
RUN npm ci --only=production

# Copier le build depuis le stage précédent
COPY --from=builder /app/dist ./dist

# Copier la configuration Prisma
COPY prisma ./prisma

# Variables d'environnement
ARG DATABASE_URL=""
ARG KEYCLOAK_URL=""
ARG KEYCLOAK_REALM=""
ARG KEYCLOAK_CLIENT_ID=""
ARG KEYCLOAK_CLIENT_SECRET=""
ARG THROTTLER_LIMIT=15

ENV DATABASE_URL=${DATABASE_URL}
ENV KEYCLOAK_URL=${KEYCLOAK_URL}
ENV KEYCLOAK_REALM=${KEYCLOAK_REALM}
ENV KEYCLOAK_CLIENT_ID=${KEYCLOAK_CLIENT_ID}
ENV KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
ENV PORT=5002
ENV NODE_ENV=production

EXPOSE 5002

# Run Prisma migrations
RUN npx prisma db push --skip-generate

CMD ["node", "dist/src/main"]