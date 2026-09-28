---
title: "docker-compose  zabbix"
date: "2018-04-23 19:33:56"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2106949"
---
> **内容介绍**
>
> 本文给出一份一键拉起 Zabbix 监控套件的 docker-compose 编排：包含
> mysql-server（5.7、utf8 字符集）、zabbix-server-mysql（10051）、
> zabbix-web-nginx-mysql（80 端口、Asia/Shanghai 时区）与 zabbix-agent
> （10050）四个服务，通过自建 bridge 网络互联，并给出各服务的环境变量
> 与数据卷挂载配置。

> **技术备注**
>
> - Docker 与 Kubernetes 生态演进较快,新版 K8s 默认运行时为 containerd,
>   请注意适配。
> - `version` 字段在 Compose V2 中已废弃，可直接省略；`links` 也已被
>   官方标记弃用，同一自定义网络内用服务名（如 mysql-server）互访即可。
> - mysql:5.7 已于 2023 年 10 月 EOL；zabbix 官方镜像建议固定版本 tag
>   而非 latest，避免升级后数据库结构不兼容。
> - 文中 DB_SERVER_HOST 写死宿主机 IP 172.31.180.21，换环境需同步修改
>   （或改为服务名）。

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
