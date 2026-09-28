# Stage 1 — install deps (inclut dev deps pour builder)
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2 — build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
# Supprime les dépendances de développement pour alléger l'image finale
RUN npm prune --production

# Stage 3 — runtime minimal
FROM node:22-alpine AS runtime
WORKDIR /app

# Variables d'environnement de production
ENV NODE_ENV=production
ENV APP_PORT=3171

# Copier uniquement ce qui est nécessaire pour exécuter l'app
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

# Utilisateur non-root (fourni par l'image node)
USER node

EXPOSE 3171

# Healthcheck utilisant node (présent dans l'image)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD node -e "require('http').get('http://127.0.0.1:3171/health',res=>process.exit(res.statusCode===200?0:1)).on('error',()=>process.exit(1))"

CMD ["node", "dist/main.js"]