---
title: "Not Found: /build/pdf.worker.js"
date: "2019-01-22 16:59:07"
category: "frontend"
source: "https://blog.51cto.com/hequan/2345510"
lang: "en"
---
> **About this post**
>
> This post records the solution to the error `Setting up fake worker failed: "Cannot load script at: /build/pdf.worker.js"` when previewing PDFs with pdf.js on the frontend: since pdf.worker.js is loaded from an incorrect path, you need to modify the worker path and the default PDF file path configuration in viewer.js.
>
> **Technical notes**
>
> It is now more recommended to import pdfjs-dist via ES Module / npm and specify the worker path through `GlobalWorkerOptions.workerSrc` (optionally with a CDN or a bundler), instead of directly modifying the viewer.js source, which is less likely to be overwritten on upgrades.

---

### pdf.js

Official website: https://mozilla.github.io/pdf.js/

#### Usage Error

```text
Setting up fake worker failed: "Cannot load script at: http://127.0.0.1/build/pdf.worker.js".

Not Found: /build/pdf.worker.js
```

Solution: modify viewer.js

- Line 4489 `value`: change it to the actual path of pdf.worker.js
- Line 4353 `value`: change it to the path of the PDF file
