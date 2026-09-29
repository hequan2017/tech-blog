---
title: "Error: vue-loader requires @vue/compiler-sfc to be present"
date: "2020-09-20 12:59:35"
category: "frontend"
source: "https://blog.51cto.com/hequan/2536201"
lang: "en"
---
> **About this post**
>
> This post documents the troubleshooting process for the `vue-loader requires @vue/compiler-sfc to be present in the dependency tree` error reported when starting a Vue project: the cause is a Vue 2 project with the Vue 3 version of `vue-loader` installed by mistake. Downgrading to `vue-loader@14` and clearing the dependency cache resolves it.

> **Technical notes**
>
> This error mostly appears when a Vue 2 project mistakenly installs `vue-loader@15+`, or when a Vue 3 project lacks `@vue/compiler-sfc`. Vue 2 has reached EOL; new projects are advised to use Vue 3 + Vite, while legacy projects can avoid the issue by pinning `vue-loader@14` or migrating the build tooling.

---

### Common vue error

> ERROR  Error: vue-loader requires @vue/compiler-sfc to be present in the dependency tree.

### Solution

```shell
npm i -D vue-loader@14
```

- If the error persists, run:

```shell
rm -rf node_modules
rm package-lock.json
npm cache clear --force
npm install
```
