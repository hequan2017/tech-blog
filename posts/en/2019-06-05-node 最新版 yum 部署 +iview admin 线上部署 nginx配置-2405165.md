---
title: "Installing the Latest Node.js via yum + Nginx Configuration for iview admin Production Deployment"
date: "2019-06-05 11:08:11"
category: "vue"
source: "https://blog.51cto.com/hequan/2405165"
lang: "en"
---
> **About this post**
>
> This post records two things: first, installing Node.js 10.x on CentOS via the NodeSource yum repository (including removing the old nodejs/npm and installing cnpm from the Taobao mirror); second, the Nginx configuration for deploying a packaged iview-admin frontend project — using `try_files` to fall all requests back to /index.html, which fixes the 404 errors that occur when refreshing pages using frontend history-mode routing.

> **Technical notes**
>
> Node.js 10.x in this post has long been EOL (support ended in April 2021); it is recommended to switch to Node.js 20/22 LTS (the corresponding NodeSource setup scripts are setup_20.x / setup_22.x). The old npm Taobao mirror domain registry.npm.taobao.org was switched to registry.npmmirror.com in 2022. iview-admin (of the iView/View UI family) is essentially no longer maintained; for new projects, consider Vue 3 + Element Plus / Naive UI. The try_files fallback to index.html remains a common practice to this day.

---

### Installing the latest Node.js via yum

```shell
curl --silent --location https://rpm.nodesource.com/setup_10.x | sudo bash -

sudo yum remove -y nodejs npm

sudo yum install -y nodejs  npm

npm install -g cnpm --registry=https://registry.npm.taobao.org
```

### iview admin production deployment with Nginx configuration

> The main change is to send all requests to /index.html for handling.

```nginx
location / {
      index  index.html  index.htm;
      try_files $uri $uri/   /index.html;
}
```
