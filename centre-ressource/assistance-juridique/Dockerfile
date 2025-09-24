###########################################################################
# ÉTAPE 1 – Build Vite
###########################################################################
FROM node:20-slim AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force

COPY . .

ARG VITE_API_URL
ARG VITE_AUTH_TOKEN_KEY
ARG VITE_DISABLE_AUTH
ARG VITE_APP_NAME
ARG VITE_PORT=4013

ENV VITE_API_URL=$VITE_API_URL \
    VITE_AUTH_TOKEN_KEY=$VITE_AUTH_TOKEN_KEY \
    VITE_DISABLE_AUTH=$VITE_DISABLE_AUTH \
    VITE_APP_NAME=$VITE_APP_NAME \
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