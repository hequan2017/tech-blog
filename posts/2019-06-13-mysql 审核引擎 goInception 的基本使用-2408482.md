---
title: "mysql 审核引擎 goInception 的基本使用"
date: "2019-06-13 15:46:41"
category: "go"
source: "https://blog.51cto.com/hequan/2408482"
---
> **内容介绍**
>
> 本文演示 MySQL SQL 审核引擎 goInception 的安装与基本调用：从源码编译启动服务，在配置里开启备份库，然后用 Python（pymysql + prettytable）模拟 MySQL 客户端连接 goInception 的 4000 端口，通过 inception_magic_start/commit 语法提交建表和插入语句，获得逐条的审核/执行结果与备份信息。

> **技术备注**
>
> goInception 是 inception 的 Go 重写版，目前仍在维护（hanchuanchuan/goInception）。文中 `go build` 的编译方式至今适用，但官方也提供 Docker 镜像和预编译包，可免去 `make parser` 步骤。示例里把审核+执行+备份一条龙跑通的做法至今通用；生产环境注意备份库账号权限与连接串里明文密码的问题。

---

### mysql 审核引擎 goInception 的基本使用

#### 官网地址

> https://github.com/hanchuanchuan/goInception

#### 安装

```shell
git clone https://github.com/hanchuanchuan/goInception.git
cd goInception
```

#### 修改配置

- 开启备份

```shell
vim config/config.toml

[inc]

backup_host="127.0.0.1"
backup_port=3306
backup_user="root"
backup_password="123456"
```

#### 启动

```shell
make parser
go build -o goInception tidb-server/main.go

./goInception -config=config/config.toml
```

```shell
pip install pymysql prettytable
```

#### 代码

```python
import pymysql
import prettytable as pt
tb = pt.PrettyTable()

sql = '''/*--user=root;--password=123456;--host=192.168.100.90;--check=0;--port=3306;--execute=1;--backup=1;*/
inception_magic_start;
use go;
create table t1(id int primary key,c1 int,c2 int );
insert into t1(id,c1,c2) values(1,1,1);
inception_magic_commit;'''

conn = pymysql.connect(host='127.0.0.1', user='', passwd='',
                       db='', port=4000, charset="utf8mb4")
cur = conn.cursor()
ret = cur.execute(sql)
result = cur.fetchall()
cur.close()
conn.close()

tb.field_names = [i[0] for i in cur.description]
for row in result:
    tb.add_row(row)
print(tb)
```

#### 结果

```text
+----------+----------+-------------+----------------------+---------------+----------------------------------------------------+---------------+------------------------+------------------------+--------------+---------+-------------+
| order_id |  stage   | error_level |     stage_status     | error_message |                        sql                         | affected_rows |        sequence        |     backup_dbname      | execute_time | sqlsha1 | backup_time |
+----------+----------+-------------+----------------------+---------------+----------------------------------------------------+---------------+------------------------+------------------------+--------------+---------+-------------+
|    1     | EXECUTED |      0      | Execute Successfully |      None     |                       use go                       |       0       | 1560411582_21_00000000 |          None          |    0.000     |   None  |      0      |
|    2     | EXECUTED |      0      | Execute Successfully |      None     | create table t1(id int primary key,c1 int,c2 int ) |       0       | 1560411582_21_00000001 | 192_168_100_90_3306_go |    0.006     |   None  |      0      |
|          |          |             | Backup Successfully  |               |                                                    |               |                        |                        |              |         |             |
|    3     | EXECUTED |      0      | Execute Successfully |      None     |       insert into t1(id,c1,c2) values(1,1,1)       |       1       | 1560411582_21_00000002 | 192_168_100_90_3306_go |    0.002     |   None  |    0.004    |
|          |          |             | Backup Successfully  |               |                                                    |               |                        |                        |              |         |             |
+----------+----------+-------------+----------------------+---------------+----------------------------------------------------+---------------+------------------------+------------------------+--------------+---------+-------------+
```
