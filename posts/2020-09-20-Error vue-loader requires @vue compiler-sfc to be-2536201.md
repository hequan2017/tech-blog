---
title: "Error: vue-loader requires @vue/compiler-sfc to be"
date: "2020-09-20 12:59:35"
category: "前端"
source: "https://blog.51cto.com/hequan/2536201"
---

### vue常见报错

> ERROR  Error: vue-loader requires @vue/compiler-sfc to be present in the dependency tree.

### 解决办法

```
npm i -D vue-loader@14
```

- 如果还是报错执行

```
rm -rf node_modules
rm package-lock.json
npm cache clear --force
npm install
```
