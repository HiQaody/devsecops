# ---- Étape 1 : Build ----
FROM node:22-alpine AS builder

RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copier uniquement ce qui sert à installer les deps
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.js ./

# Installer toutes les dépendances (y compris dev pour le build)
RUN npm install --frozen-lockfile

# Copier le reste du code
COPY . .

# Build Next.js (production-ready)
RUN npm run build

# ---- Étape 2 : Production ----
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3142

# Copier uniquement ce qui est utile pour exécuter en prod
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.js ./

EXPOSE 3142

# Lancer Next.js en mode production
CMD ["npm", "run", "start"]
