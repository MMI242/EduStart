# ── Stage 1: Build ─────────────────────────────────────────────
FROM node:20-slim AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build for production
COPY . .
RUN npm run build

# ── Stage 2: Production (serve with nginx) ─────────────────────
FROM nginx:alpine AS production

# Copy the built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Handle SPA client-side routing
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
