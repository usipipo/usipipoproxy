FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production=false
COPY . .
RUN npm run build

FROM nginx:alpine
EXPOSE 80
COPY --from=build /app/dist /usr/share/nginx/html
