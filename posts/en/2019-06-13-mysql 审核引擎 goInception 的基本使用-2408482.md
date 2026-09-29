---
title: "Basic Usage of goInception, a MySQL Audit Engine"
date: "2019-06-13 15:46:41"
category: "go"
source: "https://blog.51cto.com/hequan/2408482"
lang: "en"
---
> **About this post**
>
> This post demonstrates how to install goInception, a MySQL SQL audit engine, and invoke it in its most basic form: build the service from source and start it, enable the backup database in the configuration, then use Python (pymysql + prettytable) to act as a MySQL client connecting to goInception on port 4000, submit table-creation and insert statements via the inception_magic_start/commit syntax, and get per-statement audit/execution results along with backup information.

> **Technical notes**
>
> goInception is a Go rewrite of inception and is still actively maintained (hanchuanchuan/goInception). The `go build` compilation approach shown here still works today, but the project also offers Docker images and prebuilt packages, which spare you the `make parser` step. The all-in-one audit + execute + backup flow in the example remains generally applicable; in production, pay attention to the backup database account privileges and to plaintext passwords in the connection string.

---

### Basic Usage of goInception, a MySQL Audit Engine

#### Official Website

> https://github.com/hanchuanchuan/goInception

#### Installation

```shell
git clone https://github.com/hanchuanchuan/goInception.git
cd goInception
```

#### Modifying the Configuration

- Enable backup

```shell
vim config/config.toml

[inc]

backup_host="127.0.0.1"
backup_port=3306
backup_user="root"
backup_password="123456"
```

#### Starting the Service

```shell
make parser
go build -o goInception tidb-server/main.go

./goInception -config=config/config.toml
```

```shell
pip install pymysql prettytable
```

#### Code

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

#### Result

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
