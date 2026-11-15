# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_APP_NAME=CDIS
ARG VITE_APP_ENV=production
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_ENV=$VITE_APP_ENV
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:1.29-alpine AS runtime
RUN apk add --no-cache libcap && setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx && apk del libcap
COPY --from=build --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx
USER nginx
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD wget -q --spider http://127.0.0.1/health || exit 1