FROM node:9 as build-deps

WORKDIR /temp

ARG REACT_APP_SERVER_URL
ENV REACT_APP_SERVER_URL=$REACT_APP_SERVER_URL

ADD package*.json  ./
RUN npm install

ADD . ./

RUN npm run build

# Stage 2 - the production environment
FROM nginx:1.12-alpine

COPY --from=build-deps /temp/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
