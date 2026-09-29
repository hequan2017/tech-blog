---
title: "Dockerfile vue+go deployment example with docker-compose"
date: "2022-03-24 21:46:11"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/5146223"
lang: "en"
---
> **About this post**
>
> This post reproduces the containerized deployment configuration of the gin-vue-admin
> open-source project: a single docker-compose file orchestrates the four services
> web, server, mysql, and redis, together with a Dockerfile for each of the
> frontend and backend — the Go backend uses a multi-stage build, and the
> frontend is built with Node and then served as static pages by Nginx.

> **Technical notes**
>
> Looking back from a 2026 perspective: node:16 reached end of maintenance in September 2023,
> and mysql:8.0.21 and redis:6.0.6 are likewise old versions from around 2020;
> in practice it is advisable to switch to newer image tags. Today's Compose V2 ignores
> the top-level version field, services can reach each other directly by service name, and links is a legacy option.

---

Reposted from <https://github.com/flipped-aurora/gin-vue-admin>.

## 1. docker-compose orchestration: start the four services with one command

```yaml
version: "3"

# Declare a networks entry named "network"; subnet is its subnet address, and the default gateway is 177.7.0.1
networks:
  network:
    ipam:
      driver: default
      config:
        - subnet: '177.7.0.0/16'

# Persistent storage for mysql and redis
volumes:
  mysql:
  redis:

services:
  web:
    build:
      context: ./web
      dockerfile: ./Dockerfile
    container_name: gva-web
    restart: always
    ports:
      - '8080:8080'
    depends_on:
      - server
    command: [ 'nginx-debug', '-g', 'daemon off;' ]
    networks:
      network:
        ipv4_address: 177.7.0.11

  server:
    build:
      context: ./server
      dockerfile: ./Dockerfile
    container_name: gva-server
    restart: always
    ports:
      - '8888:8888'
    depends_on:
      - mysql
      - redis
    links:
      - mysql
      - redis
    networks:
      network:
        ipv4_address: 177.7.0.12

  mysql:
    image: mysql:8.0.21       # On arm64 architectures (e.g. an M1 Mac), change the image to image: mysql/mysql-server:8.0.21
    container_name: gva-mysql
    command: mysqld --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci # Set the utf8 character set
    restart: always
    ports:
      - "13306:3306"  # The host port is mapped directly to 13306
    environment:
      MYSQL_DATABASE: 'qmPlus' # Name of the database to create on initial startup
      MYSQL_ROOT_PASSWORD: 'Aa@6447985' # Password of the root admin user
    volumes:
      - mysql:/var/lib/mysql
    networks:
      network:
        ipv4_address: 177.7.0.13

  redis:
    image: redis:6.0.6
    container_name: gva-redis # Container name
    restart: always
    ports:
      - '16379:6379'
    volumes:
      - redis:/data
    networks:
      network:
        ipv4_address: 177.7.0.14
```

## 2. server/Dockerfile: multi-stage build for the Go backend

```dockerfile
FROM golang:alpine as builder

WORKDIR /go/src/github.com/flipped-aurora/gin-vue-admin/server
COPY . .

RUN go env -w GO111MODULE=on \
    && go env -w GOPROXY=https://goproxy.cn,direct \
    && go env -w CGO_ENABLED=0 \
    && go env \
    && go mod tidy \
    && go build -o server .

FROM alpine:latest

LABEL MAINTAINER="SliverHorn@sliver_horn@qq.com"

WORKDIR /go/src/github.com/flipped-aurora/gin-vue-admin/server

COPY --from=0 /go/src/github.com/flipped-aurora/gin-vue-admin/server/server ./
COPY --from=0 /go/src/github.com/flipped-aurora/gin-vue-admin/server/resource ./resource/
COPY --from=0 /go/src/github.com/flipped-aurora/gin-vue-admin/server/config.docker.yaml ./

EXPOSE 8888
ENTRYPOINT ./server -c config.docker.yaml
```

## 3. web/Dockerfile: build the frontend, then serve it with Nginx

```dockerfile
FROM node:16

WORKDIR /gva_web/
COPY . .

RUN yarn && yarn build

FROM nginx:alpine
LABEL MAINTAINER="SliverHorn@sliver_horn@qq.com"

COPY .docker-compose/nginx/conf.d/my.conf /etc/nginx/conf.d/my.conf
COPY --from=0 /gva_web/dist /usr/share/nginx/html
RUN cat /etc/nginx/nginx.conf
RUN cat /etc/nginx/conf.d/my.conf
RUN ls -al /usr/share/nginx/html
```
