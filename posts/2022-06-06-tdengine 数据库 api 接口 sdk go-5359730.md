---
title: "tdengine 数据库 api 接口  sdk  go"
date: "2022-06-06 11:48:10"
category: "go"
source: "https://blog.51cto.com/hequan/5359730"
---
> **内容介绍**
>
> 一段 Go 最小示例：通过 `database/sql` 标准接口访问 TDengine 时序数据库，
> 以 HTTP 连接串（6041 端口）打开连接，切换到 `teledb` 库后查询表
> `teledb.d1001`，逐行 Scan 并打印时间戳与三列数据；依赖社区的纯 Go 驱动
> `wenj91/taos-driver`。

> **技术备注**
>
> 以 2026 年视角看：文中 `wenj91/taos-driver` 是 TDengine 2.x 时代的社区纯
> Go 驱动——driver 名虽为 `taosSql`，实际走的是 RESTful 接口（6041）。官方
> Go 连接器已迭代至 `github.com/taosdata/driver-go/v3`，提供 `taosWS`
> （WebSocket，v3 推荐）与 `taosRestful`（REST）等无需客户端库的连接方式，
> 新项目建议直接使用官方驱动。

---

## 1. 连接与查询示例

完整示例：`sql.Open("taosSql", ...)` 以 HTTP 连接串连接 TDengine（6041 为
taosAdapter 提供的 REST 端口），随后切库、查询并逐行打印结果。

```go
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/wenj91/taos-driver"
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
