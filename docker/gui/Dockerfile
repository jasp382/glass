### STAGE 1: Build ###
FROM node:12.7-alpine AS build
WORKDIR /usr/src/app
COPY glass-app/package.json glass-app/package-lock.json ./
RUN npm install
COPY ./glass-app .
RUN npm run build
### STAGE 2: Run ###
FROM nginx:1.17.1-alpine
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /usr/src/app/dist/uglass-app /usr/share/nginx/html