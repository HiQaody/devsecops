# ---------- Build ----------
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

#VITE_API_URL=http://localhost:3001/api/v1
#VITE_JWT_EXPIRE=3600s
ARG BUILD_ENV=production
ARG VITE_API_URL
ARG VITE_JWT_EXPIRE
ENV NODE_ENV=$BUILD_ENV
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_JWT_EXPIRE=$VITE_JWT_EXPIRE

RUN npm run build


# ---------- Runtime ----------
FROM nginx:1.25-alpine

# Nettoyage config par défaut
RUN rm /etc/nginx/conf.d/default.conf

# Configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Build Vite
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3155

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3155/ || exit 1

CMD ["nginx", "-g", "daemon off;"]