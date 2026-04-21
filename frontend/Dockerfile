# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund
COPY tsconfig*.json vite.config.ts tailwind.config.js postcss.config.js components.json index.html ./
COPY src ./src
ARG VITE_BFF_URL=http://localhost:8080
ENV VITE_BFF_URL=$VITE_BFF_URL
RUN npm run build

# nginxinc/nginx-unprivileged corre como UID 101 y escucha en 8080 (sin root)
FROM docker.io/nginxinc/nginx-unprivileged:1.27-alpine AS runtime
USER root
RUN apk add --no-cache curl
USER nginx
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD curl -fsS http://localhost:8080/ || exit 1
