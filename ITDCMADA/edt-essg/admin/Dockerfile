# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Arguments pour les variables de build
ARG VITE_PORT
ARG VITE_API_BASE_URL
# Copy only package files to leverage layer caching
COPY package*.json ./

# Install dependencies (production + dev for build)
RUN npm ci

# Copy source code
COPY src ./src
COPY public ./public
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig.json ./

# Create .env file for build
RUN echo "VITE_PORT=${VITE_PORT}" > .env && \
    echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}" >> .env

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 3172

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3172 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]