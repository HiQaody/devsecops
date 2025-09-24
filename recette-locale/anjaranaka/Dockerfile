###########################################################################
# ÉTAPE 1 – Build Vite
###########################################################################
FROM node:20-slim AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force

COPY . .

ARG VITE_API_URL_SERVICECITOYEN
ARG VITE_API_URL_SERVICEAUTH
ARG VITE_API_URL_SERVICEZONE
ARG VITE_API_URL_SERVICEOFFRECOMMUNE
ARG VITE_API_SERVICEMODERNEMARKET
ARG VITE_APP_CLIENT_ID
ARG VITE_PORT=4005

ENV VITE_API_URL_SERVICECITOYEN=$VITE_API_URL_SERVICECITOYEN \
    VITE_API_URL_SERVICEAUTH=$VITE_API_URL_SERVICEAUTH \
    VITE_API_URL_SERVICEZONE=$VITE_API_URL_SERVICEZONE \
    VITE_API_URL_SERVICEOFFRECOMMUNE=$VITE_API_URL_SERVICEOFFRECOMMUNE \
    VITE_API_SERVICEMODERNEMARKET=$VITE_API_SERVICEMODERNEMARKET \
    VITE_APP_CLIENT_ID=$VITE_APP_CLIENT_ID \
    VITE_PORT=$VITE_PORT

RUN npm run build

###########################################################################
# ÉTAPE 2 – Image Nginx (non-root)
###########################################################################
FROM nginxinc/nginx-unprivileged:1.25-alpine AS runner
USER 101
WORKDIR /usr/share/nginx/html

# On écrase simplement les fichiers par défaut
COPY --from=builder --chown=101:101 /app/dist .

COPY nginx.conf /etc/nginx/conf.d/default.conf
ENV PORT=$VITE_PORT
EXPOSE $VITE_PORT

CMD ["nginx","-g","daemon off;"]