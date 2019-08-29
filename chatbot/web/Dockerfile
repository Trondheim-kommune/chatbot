FROM node:9 as build-deps

WORKDIR /temp


ADD package*.json  ./
RUN npm install

ENV REACT_APP_SERVER_URL="http://${SERVER_URL}/"

ADD . ./

RUN npm run build

# Stage 2 - the production environment
FROM nginx:1.12-alpine


COPY --from=build-deps /temp/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
