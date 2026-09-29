---
title: "TDengine Database API SDK in Go"
date: "2022-06-06 11:48:10"
category: "go"
source: "https://blog.51cto.com/hequan/5359730"
lang: "en"
---
> **About this post**
>
> A minimal Go example: accessing the TDengine time-series database through the
> standard `database/sql` interface, opening a connection with an HTTP connection
> string (port 6041), switching to the `teledb` database, querying the table
> `teledb.d1001`, then scanning row by row and printing the timestamp together
> with three data columns; it relies on the community pure-Go driver
> `wenj91/taos-driver`.

> **Technical notes**
>
> From a 2026 perspective: `wenj91/taos-driver` in this post is a community
> pure-Go driver from the TDengine 2.x era — although the driver name is
> `taosSql`, it actually goes through the RESTful interface (port 6041). The
> official Go connector has since evolved to `github.com/taosdata/driver-go/v3`,
> which offers connection methods that require no client library, such as
> `taosWS` (WebSocket, recommended in v3) and `taosRestful` (REST); new projects
> are advised to use the official driver directly.

---

## 1. Connection and Query Example

Full example: `sql.Open("taosSql", ...)` connects to TDengine with an HTTP
connection string (6041 is the REST port provided by taosAdapter), then switches
the database, queries, and prints the results row by row.

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
