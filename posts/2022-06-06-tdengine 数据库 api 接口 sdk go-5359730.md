---
title: "tdengine 数据库 api 接口  sdk  go"
date: "2022-06-06 11:48:10"
category: "go"
source: "https://blog.51cto.com/hequan/5359730"
---
> **内容介绍**
>
> 本文是Go 语言后端开发实战,记录了「tdengine 数据库 api 接口  sdk  go」的相关内容。

---

```python
package main

import (
    "database/sql"
    "fmt"
    _ "/wenj91/taos-driver"
    "time"
)

func main() {
    var taosUri = "root:taosdata@http(192.168.X.X:6041)/teledb"
    taos, err := sql.Open("taosSql", taosUri)
    if err != nil {
        fmt.Println(err)
        return
    }
    defer taos.Close()
    taos.Exec("use teledb")
    rows, err := taos.Query("select * from teledb.d1001;")
    if err != nil {
        fmt.Println("failed to select from table, err:", err)
        return
    }
    for rows.Next() {
        var r struct {
            ts time.Time
            a  float64
            b  int
            c  float64
        }
        err := rows.Scan(&r.ts, &r.a, &r.b, &r.c)
        if err != nil {
            fmt.Println("scan error:\n", err)
            return
        }
        fmt.Println(r.ts, r.a, r.b, r.c)
    }
}
```
