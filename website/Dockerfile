FROM node:9 as build-deps

WORKDIR /usr/src/app
ADD package.json ./
RUN npm install

ADD . ./
CMD ["npm", "run", "build"]

# Stage 2
FROM nginx:1.15

COPY --from=build-stage /app/build/ /usr/share/nginx/html

COPY --from=build-stage /nginx.conf /etc/nginx/conf.d/default.conf

