###########################################################################
# �TAPE 1 � Build Vite
###########################################################################
FROM node:20-slim AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force

COPY . .

ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ARG CLERK_SECRET_KEY
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_APP_DOMAIN
ARG PORT=3144

ENV \
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY} \
  CLERK_SECRET_KEY=${CLERK_SECRET_KEY} \
  NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL} \
  NEXT_PUBLIC_APP_DOMAIN=${NEXT_PUBLIC_APP_DOMAIN} \
  PORT=${PORT}

RUN npm run build

###########################################################################
# �TAPE 2 � Image Nginx (non-root)
###########################################################################
FROM nginxinc/nginx-unprivileged:1.25-alpine AS runner
USER 101
WORKDIR /usr/share/nginx/html

COPY --from=builder --chown=101:101 /app/dist .

COPY nginx.conf /etc/nginx/conf.d/default.conf
ENV PORT=${PORT}
EXPOSE 3144

CMD ["nginx","-g","daemon off;"]