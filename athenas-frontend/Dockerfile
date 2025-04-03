# build environment
FROM node:20 as build

ARG script
ENV env_script $script

ARG version_app
ENV env_version_app $version_app

WORKDIR /app
COPY package*.json /app/
RUN npm install --force
COPY . /app/
RUN npm version --no-git-tag-version $env_version_app
RUN npm run $env_script

# production environment
FROM nginx:1.25-alpine
COPY --from=build /app/suite-athenas /usr/share/nginx/html/suite-athenas
EXPOSE 80
