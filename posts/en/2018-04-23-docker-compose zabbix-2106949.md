---
title: "docker-compose  zabbix"
date: "2018-04-23 19:33:56"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2106949"
lang: "en"
---
> **About this post**
>
> This post presents a docker-compose setup that brings up a complete Zabbix
> monitoring stack in one go: four services — mysql-server (5.7, utf8 charset),
> zabbix-server-mysql (10051), zabbix-web-nginx-mysql (port 80, Asia/Shanghai
> timezone) and zabbix-agent (10050) — interconnected over a self-created
> bridge network, along with the environment variables and data volume mounts
> configured for each service.

> **Technical notes**
>
> - The Docker and Kubernetes ecosystem evolves quickly; newer Kubernetes
>   versions use containerd as the default runtime, so adapt accordingly.
> - The `version` field is deprecated in Compose V2 and can simply be omitted;
>   `links` has also been officially deprecated — within the same custom
>   network, services can reach each other by service name (e.g., mysql-server).
> - mysql:5.7 reached EOL in October 2023; for the official Zabbix images,
>   it is recommended to pin a version tag instead of latest, to avoid
>   database schema incompatibilities after upgrades.
> - In this post, DB_SERVER_HOST is hard-coded to the host IP 172.31.180.21;
>   change it in sync when switching environments (or replace it with the
>   service name).

---

## 1. docker-compose.yml

```yaml
version: '3.6'
services:
  mysql-server:
    hostname: mysql-server
    container_name: mysql-server
    image: mysql:5.7
    ports:
      - 3306:3306
    networks:
      - zabbix
    volumes:
      - /data/mysql5721/data:/var/lib/mysql
    command: --character-set-server=utf8
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: zabbix
      MYSQL_USER: zabbix
      MYSQL_PASSWORD: zabbix

  zabbix-web-nginx-mysql:
    hostname: zabbix-web-nginx-mysql
    container_name: zabbix-web-nginx-mysql
    image: zabbix/zabbix-web-nginx-mysql:latest
    networks:
      - zabbix
    links:
      - mysql-server:mysql-server
      - zabbix-server:zabbix-server
    ports:
      - 80:80
    environment:
      DB_SERVER_HOST: 172.31.180.21
      MYSQL_DATABASE: zabbix
      MYSQL_USER: zabbix
      MYSQL_PASSWORD: zabbix
      MYSQL_ROOT_PASSWORD: 123456
      ZBX_SERVER_NAME: web-name
      PHP_TZ: Asia/Shanghai

  zabbix-server:
    hostname: zabbix-server-mysql
    image: zabbix/zabbix-server-mysql:latest
    networks:
      - zabbix
    links:
      - mysql-server:mysql-server
    container_name: zabbix-server-mysql
    ports:
      - 10051:10051
    environment:
      DB_SERVER_HOST: 172.31.180.21
      MYSQL_DATABASE: zabbix
      MYSQL_USER: zabbix
      MYSQL_PASSWORD: zabbix
      MYSQL_ROOT_PASSWORD: 123456
      ZBX_AGENT: zabbix-agent


  zabbix-agent:
    hostname: zabbix-agent
    image: zabbix/zabbix-agent:latest
    networks:
      - zabbix
    container_name: zabbix-agent
    links:
      - zabbix-server:zabbix-server
    ports:
      - 10050:10050
    environment:
      ZBX_HOSTNAME: monitor
      ZBX_UNSAFEUSERPARAMETERS: 1


networks:
  zabbix:
    driver: bridge
    driver_opts:
      com.docker.network.enable_ipv6: "false"
```
