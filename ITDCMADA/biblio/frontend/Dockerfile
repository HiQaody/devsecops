FROM node:24-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

ARG VITE_API_BASE_URL
ARG VITE_API_TIMEOUT
ARG PORT


RUN npm run build

ENV \
    VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_API_TIMEOUT=${VITE_API_TIMEOUT} \
    PORT=${PORT}

EXPOSE 3153

USER node

CMD ["node", "dist/main", "--port", "${PORT}"]