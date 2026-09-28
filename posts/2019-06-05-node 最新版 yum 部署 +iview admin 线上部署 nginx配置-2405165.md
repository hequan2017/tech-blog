---
title: "node 最新版 yum 部署 +iview admin 线上部署 nginx配置"
date: "2019-06-05 11:08:11"
category: "vue"
source: "https://blog.51cto.com/hequan/2405165"
---
> **内容介绍**
>
> 本文是Vue 前端工程化实践,记录了「node 最新版 yum 部署 +iview admin 线上部署 nginx配置」的相关内容。主要涉及:### node 最新版 yum 部署 ### iview admin 线上部署 nginx配置 > 主要是修改 将所有请求 都发送到 /index.html …

> **技术备注**
>
> Nginx 配置在不同大版本间略有差异,建议以当前稳定版(1.24+/1.26+)官方文档为准。

---

### node 最新版 yum 部署

```shellcurl --silent --location https://rpm.nodesource.com/setup_10.x | sudo bash -

sudo yum remove -y nodejs npm

sudo yum install -y nodejs  npm

npm install -g cnpm --registry=https://registry.npm.taobao.org
```

### iview admin 线上部署 nginx配置

> 主要是修改 将所有请求 都发送到  /index.html 处理。

```shelllocation / {
      index  index.html  index.htm;
      try_files $uri $uri/   /index.html;
}
```
