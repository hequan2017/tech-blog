---
title: "Error: vue-loader requires @vue/compiler-sfc to be"
date: "2020-09-20 12:59:35"
category: "前端"
source: "https://blog.51cto.com/hequan/2536201"
---
> **内容介绍**
>
> 记录 Vue 项目启动时报错 `vue-loader requires @vue/compiler-sfc to be present in the dependency tree` 的排查过程：原因是 Vue 2 项目误装了 Vue 3 版本的 `vue-loader`，降级到 `vue-loader@14` 并清理依赖缓存即可解决。

> **技术备注**
>
> 该报错多出现在 Vue 2 项目误装 `vue-loader@15+` 或 Vue 3 项目缺少 `@vue/compiler-sfc` 时；Vue 2 已进入 EOL，新项目建议使用 Vue 3 + Vite，旧项目可通过锁定 `vue-loader@14` 或迁移构建工具规避。

---

### vue常见报错

> ERROR  Error: vue-loader requires @vue/compiler-sfc to be present in the dependency tree.

### 解决办法

```shell
npm i -D vue-loader@14
```

- 如果还是报错执行

```shell
rm -rf node_modules
rm package-lock.json
npm cache clear --force
npm install
```
