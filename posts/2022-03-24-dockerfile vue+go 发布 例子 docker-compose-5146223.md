---
title: "dockerfile  vue+go 发布 例子  docker-compose"
date: "2022-03-24 21:46:11"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/5146223"
---

```
来自 https:///flipped-aurora/gin-vue-admin 转载
```

```
docker-compose.yaml
version: "3"

# 声明一个名为network的networks,subnet为network的子网地址,默认网关是177.7.0.1
networks:
  network:
    ipam:
      driver: default
      config:
        - subnet: '177.7.0.0/16'
        
# 设置mysql，redis持久化保存
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
    image: mysql:8.0.21       # 如果您是 arm64 架构：如 MacOS 的 M1，请修改镜像为 image: mysql/mysql-server:8.0.21
    container_name: gva-mysql
    command: mysqld --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci #设置utf8字符集
    restart: always
    ports:
      - "13306:3306"  # host物理直接映射端口为13306
    environment:
      MYSQL_DATABASE: 'qmPlus' # 初始化启动时要创建的数据库的名称
      MYSQL_ROOT_PASSWORD: 'Aa@6447985' # root管理员用户密码
    volumes:
      - mysql:/var/lib/mysql
    networks:
      network:
        ipv4_address: 177.7.0.13

  redis:
    image: redis:6.0.6
    container_name: gva-redis # 容器名
    restart: always
    ports:
      - '16379:6379'
    volumes:
      - redis:/data
    networks:
      network:
        ipv4_address: 177.7.0.14
```

```
server/Dockerfile 
FROM golang:alpine as builder

WORKDIR /go/src//flipped-aurora/gin-vue-admin/server
COPY . .

RUN go env -w GO111MODULE=on \
    && go env -w GOPROXY=https://goproxy.cn,direct \
    && go env -w CGO_ENABLED=0 \
    && go env \
    && go mod tidy \
    && go build -o server .

FROM alpine:latest

LABEL MAINTAINER="SliverHorn@sliver_horn@"

WORKDIR /go/src//flipped-aurora/gin-vue-admin/server

COPY --from=0 /go/src//flipped-aurora/gin-vue-admin/server/server ./
COPY --from=0 /go/src//flipped-aurora/gin-vue-admin/server/resource ./resource/
COPY --from=0 /go/src//flipped-aurora/gin-vue-admin/server/config.docker.yaml ./

EXPOSE 8888
ENTRYPOINT ./server -c config.docker.yaml
```

```
web/Dockerfile 
FROM node:16

WORKDIR /gva_web/
COPY . .

RUN yarn && yarn build

FROM nginx:alpine
LABEL MAINTAINER="SliverHorn@sliver_horn@"

COPY .docker-compose/nginx/conf.d/my.conf /etc/nginx/conf.d/my.conf
COPY --from=0 /gva_web/dist /usr/share/nginx/html
RUN cat /etc/nginx/nginx.conf
RUN cat /etc/nginx/conf.d/my.conf
RUN ls -al /usr/share/nginx/html
```
