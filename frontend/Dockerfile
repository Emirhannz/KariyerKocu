# Build Stage
FROM node:18-alpine as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production Stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Nginx default config is usually fine for SPA if we handle history api fallback, 
# but for a simple hackathon demo, the default might be enough if we don't use deep linking directly.
# However, adding a custom nginx.conf is safer for React Router.
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
