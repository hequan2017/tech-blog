---
title: "mysql  sql clickhouse  go   where 查询不到 float  Decimal(8, 2)"
date: "2021-12-23 16:44:11"
category: ""
source: "https://blog.51cto.com/hequan/4837471"
---
> **内容介绍**
>
> 记录一个 ClickHouse 查询踩坑：当字段类型为 `Decimal(8, 2)` 或 Float 时，Go 侧用普通等值条件 `Where("test = ?", value)` 经常匹配不到数据。解决办法是在查询条件里显式做类型转换，用 `toFloat64(test)` 把列转成浮点后再比较。

> **技术备注**
>
> 根本原因是 ClickHouse 的 Decimal/Float 与 Go 传入参数之间存在精度与类型不匹配，等值比较容易落空；更稳妥的做法除了 `toFloat64`，也可以在建表时统一数值精度，或使用 `toDecimal64` 与参数对齐。另外 `toFloat64` 转换会使该列无法走索引（分区键/主键），大表上注意评估扫描成本。

---

```go
db.Where("toFloat64(test) = ?", test)
```
