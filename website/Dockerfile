FROM node:9 as build-deps

WORKDIR /usr/src/app
ADD package.json ./
RUN npm install

ADD . ./
CMD ["npm", "start", "--port", "3000"]
