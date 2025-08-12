FROM node:22 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:22-alpine as runner
WORKDIR /app
COPY --from=build /app/out ./

ARG NEXT_PUBLIC_FRONTEND_BASE_URL
ARG NEXT_PUBLIC_API_URL

ENV NODE_ENV=production
ENV NEXT_PUBLIC_FRONTEND_BASE_URL=${NEXT_PUBLIC_FRONTEND_BASE_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV PORT=3135

EXPOSE 3135
CMD ["npx", "serve", "-s", "dist", "-l", "3135"]
