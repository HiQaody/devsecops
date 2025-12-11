# syntax=docker/dockerfile:1

ARG NODE_VERSION=22
ARG PNPM_VERSION=10.15.0

# Base stage
FROM node:${NODE_VERSION}-alpine AS base

WORKDIR /app

# Install pnpm globally
RUN --mount=type=cache,target=/root/.npm \
    npm install -g pnpm@${PNPM_VERSION}

ENV PNPM_HOME="/usr/local/share/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# Dependencies stage
FROM base AS deps

COPY package.json pnpm-lock.yaml ./

RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Build stage
FROM base AS build

COPY . .
COPY --from=deps /app/node_modules ./node_modules

ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

RUN pnpm run build

# Final stage
FROM base AS final

ENV NODE_ENV=production
ENV PORT=5001
EXPOSE 5001

COPY package.json ./
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
CMD wget --quiet --tries=1 --spider http://localhost:${PORT}/ || exit 1

CMD ["pnpm", "start"]
