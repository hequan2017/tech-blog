---
title: "mysql sql clickhouse go: WHERE fails to match float Decimal(8, 2)"
date: "2021-12-23 16:44:11"
category: "go"
source: "https://blog.51cto.com/hequan/4837471"
lang: "en"
---
> **About this post**
>
> Notes on a ClickHouse query pitfall: when the column type is `Decimal(8, 2)` or Float, a plain equality condition on the Go side, `Where("test = ?", value)`, often fails to match any data. The fix is to perform an explicit type conversion in the query condition, using `toFloat64(test)` to cast the column to a float before comparing.

> **Technical notes**
>
> The root cause is a precision/type mismatch between ClickHouse's Decimal/Float and the parameters passed in from Go, which makes equality comparisons unreliable. Besides `toFloat64`, safer approaches include unifying numeric precision at table creation time, or using `toDecimal64` to align with the parameter. Also note that `toFloat64` prevents the column from using an index (partition key/primary key), so evaluate the scan cost carefully on large tables.

---

```go
db.Where("toFloat64(test) = ?", test)
```
