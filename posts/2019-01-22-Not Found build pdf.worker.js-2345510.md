---
title: "Not Found: /build/pdf.worker.js"
date: "2019-01-22 16:59:07"
category: "前端"
source: "https://blog.51cto.com/hequan/2345510"
---
> **内容介绍**
>
> 本文是前端开发学习与实践,记录了「Not Found: /build/pdf.worker.js」的相关内容。主要涉及:### pdf.js #### 使用报错…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

### pdf.js

```shellhttps://mozilla.github.io/pdf.js/
```

#### 使用报错

```shellSetting up fake worker failed: "Cannot load script at: http://127.0.0.1/build/pdf.worker.js".

Not Found: /build/pdf.worker.js

修改 viewer.js
4489行   value: 实际路径

4353行   value：PDF文件路径
```
