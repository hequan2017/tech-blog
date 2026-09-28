---
title: "Not Found: /build/pdf.worker.js"
date: "2019-01-22 16:59:07"
category: "前端"
source: "https://blog.51cto.com/hequan/2345510"
---

### pdf.js

```
https://mozilla.github.io/pdf.js/
```

#### 使用报错

```
Setting up fake worker failed: "Cannot load script at: http://127.0.0.1/build/pdf.worker.js".

Not Found: /build/pdf.worker.js

修改 viewer.js
4489行   value: 实际路径

4353行   value：PDF文件路径
```
