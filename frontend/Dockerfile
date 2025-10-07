FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
# RUN npm ci
RUN npm install

COPY . .
RUN npm run build

FROM nginx:stable-alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

CMD ["/docker-entrypoint.sh"]