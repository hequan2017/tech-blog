---
title: "node 最新版 yum 部署 +iview admin 线上部署 nginx配置"
date: "2019-06-05 11:08:11"
category: "vue"
source: "https://blog.51cto.com/hequan/2405165"
---
> **内容介绍**
>
> 本文记录两件事：一是在 CentOS 上通过 NodeSource 的 yum 源安装 Node.js 10.x（含卸载旧版 nodejs/npm、安装淘宝镜像 cnpm）；二是 iview-admin 前端项目打包上线时的 Nginx 配置——通过 `try_files` 把所有请求回退到 /index.html，解决前端 history 路由刷新 404 的问题。

> **技术备注**
>
> 文中 Node.js 10.x 早已 EOL（2021-04 停止支持），建议改用 Node.js 20/22 LTS（NodeSource 对应 setup_20.x / setup_22.x）。npm 淘宝镜像旧域名 registry.npm.taobao.org 已于 2022 年切换到 registry.npmmirror.com。iview-admin（iView/View UI 系）已基本停更，新项目可考虑 Vue 3 + Element Plus / Naive UI。try_files 回退到 index.html 的写法至今通用。

---

### node 最新版 yum 部署

```shell
curl --silent --location https://rpm.nodesource.com/setup_10.x | sudo bash -

sudo yum remove -y nodejs npm

sudo yum install -y nodejs  npm

npm install -g cnpm --registry=https://registry.npm.taobao.org
```

### iview admin 线上部署 nginx配置

> 主要是修改 将所有请求 都发送到  /index.html 处理。

```nginx
location / {
      index  index.html  index.htm;
      try_files $uri $uri/   /index.html;
}
```
