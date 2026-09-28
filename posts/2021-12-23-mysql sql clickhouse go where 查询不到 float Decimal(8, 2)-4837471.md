---
title: "mysql  sql clickhouse  go   where 查询不到 float  Decimal(8, 2)"
date: "2021-12-23 16:44:11"
category: ""
source: "https://blog.51cto.com/hequan/4837471"
---

```
db.Where("toFloat64(test)  = ?",test)
```
