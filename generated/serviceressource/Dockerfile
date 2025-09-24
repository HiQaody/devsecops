FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

ARG DB_HOST
ARG DB_PORT
ARG DB_USER
ARG DB_PASS
ARG DB_NAME

ARG PORT

ENV DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    DB_USER=${DB_USER} \
    DB_PASS=${DB_PASS} \
    DB_NAME=${DB_NAME} \
    PORT=${PORT}

EXPOSE ${PORT}

USER node
CMD ["node", "dist/main", "--port", "${PORT}"]
