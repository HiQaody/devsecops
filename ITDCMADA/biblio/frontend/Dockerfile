###########################################################################
# ÉTAPE 1 – Build Vite
###########################################################################
FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_BASE_URL
ARG VITE_API_TIMEOUT
ARG VITE_PORT=3154

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_API_TIMEOUT=$VITE_API_TIMEOUT \
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