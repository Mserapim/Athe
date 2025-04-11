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
RUN npm run build -- --configuration=production

# production environment
FROM nginx:1.25-alpine
COPY --from=build /app/dist/suite-athenas /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
