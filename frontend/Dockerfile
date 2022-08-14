# build env
FROM node:13.12.0-alpine as build
WORKDIR .
COPY package*.json ./
RUN npm install
# COPY . ./
COPY . .
RUN npm run build
CMD cp -r build result_build
