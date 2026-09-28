---
title: "Error: vue-loader requires @vue/compiler-sfc to be"
date: "2020-09-20 12:59:35"
category: "前端"
source: "https://blog.51cto.com/hequan/2536201"
---
> **内容介绍**
>
> 本文是前端开发学习与实践,记录了「Error: vue-loader requires @vue/compiler-sfc to be」的相关内容。主要涉及:### vue常见报错 > ERROR Error: vue-loader requires @vue/compiler-sfc to be present i…

---

### vue常见报错

> ERROR  Error: vue-loader requires @vue/compiler-sfc to be present in the dependency tree.

### 解决办法

```shellnpm i -D vue-loader@14
```shell

- 如果还是报错执行

```shellrm -rf node_modules
rm package-lock.json
npm cache clear --force
npm install
```
