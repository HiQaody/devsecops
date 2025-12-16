FROM node:24-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

ARG DB_HOST
ARG DB_PORT
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_DATABASE
ARG PORT


RUN npm run build

ENV \
    DB_HOST=$DB_HOST \
    DB_PORT=$DB_PORT \
    DB_USERNAME=$DB_USERNAME \
    DB_PASSWORD=$DB_PASSWORD \
    DB_DATABASE=$DB_DATABASE \
    PORT=${PORT}

EXPOSE 3153

USER node

CMD ["node", "dist/main", "--port", "${PORT}"]