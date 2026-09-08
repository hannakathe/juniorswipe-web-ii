# Build context = repository root (see docker-compose.yml: context: .)
# --- build stage ---
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Same-origin requests: nginx proxies /api to the backend container.
ENV VITE_API_URL=""
RUN npm run build

# --- serve stage ---
FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# Bundle the static landing site too, served under /landing/
COPY landing/ /usr/share/nginx/html/landing/
EXPOSE 80
HEALTHCHECK --interval=15s --timeout=3s --retries=5 \
    CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1
