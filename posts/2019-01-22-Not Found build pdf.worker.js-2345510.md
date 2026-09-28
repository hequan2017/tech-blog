---
title: "Not Found: /build/pdf.worker.js"
date: "2019-01-22 16:59:07"
category: "前端"
source: "https://blog.51cto.com/hequan/2345510"
---
> **内容介绍**
>
> 记录在前端使用 pdf.js 预览 PDF 时报 `Setting up fake worker failed: "Cannot load script at: /build/pdf.worker.js"` 的解决办法：由于 pdf.worker.js 加载路径不正确，需要修改 viewer.js 中 worker 路径和默认 PDF 文件路径的配置。
>
> **技术备注**
>
> 现在更推荐用 ES Module / npm 方式引入 pdfjs-dist，并通过 `GlobalWorkerOptions.workerSrc` 指定 worker 路径（可配合 CDN 或打包工具），而不是直接改 viewer.js 源码，升级时不易被覆盖。

---

### pdf.js

官网：https://mozilla.github.io/pdf.js/

#### 使用报错

```text
Setting up fake worker failed: "Cannot load script at: http://127.0.0.1/build/pdf.worker.js".

Not Found: /build/pdf.worker.js
```

解决办法：修改 viewer.js

- 4489 行 `value`：改为 pdf.worker.js 实际路径
- 4353 行 `value`：改为 PDF 文件路径
