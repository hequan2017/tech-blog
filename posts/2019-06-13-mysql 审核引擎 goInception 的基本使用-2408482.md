---
title: "mysql 审核引擎 goInception 的基本使用"
date: "2019-06-13 15:46:41"
category: "go"
source: "https://blog.51cto.com/hequan/2408482"
---
> **内容介绍**
>
> 本文是Go 语言后端开发实战,记录了「mysql 审核引擎 goInception 的基本使用」的相关内容。主要涉及:### mysql 审核引擎 goInception 的基本使用 #### 官网地址 > https:///hanchuanchuan/goInception…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

### mysql 审核引擎 goInception 的基本使用

#### 官网地址

> https:///hanchuanchuan/goInception

#### 安装

```shellgit clone https:///hanchuanchuan/goInception.git
cd goInception
```shell

#### 修改配置

- 开启备份

```shellvim  config/config.toml

[inc]

backup_host="127.0.0.1"
backup_port=3306
backup_user="root"
backup_password="123456"
```

#### 启动

```shellmake parser
go build -o goInception tidb-server/main.go

./goInception -config=config/config.toml
```python

> pip install pymysql prettytable

#### 代码

```pythonimport pymysql
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

```shell+----------+----------+-------------+----------------------+---------------+----------------------------------------------------+---------------+------------------------+------------------------+--------------+---------+-------------+
| order_id |  stage   | error_level |     stage_status     | error_message |                        sql                         | affected_rows |        sequence        |     backup_dbname      | execute_time | sqlsha1 | backup_time |
+----------+----------+-------------+----------------------+---------------+----------------------------------------------------+---------------+------------------------+------------------------+--------------+---------+-------------+
|    1     | EXECUTED |      0      | Execute Successfully |      None     |                       use go                       |       0       | 1560411582_21_00000000 |          None          |    0.000     |   None  |      0      |
|    2     | EXECUTED |      0      | Execute Successfully |      None     | create table t1(id int primary key,c1 int,c2 int ) |       0       | 1560411582_21_00000001 | 192_168_100_90_3306_go |    0.006     |   None  |      0      |
|          |          |             | Backup Successfully  |               |                                                    |               |                        |                        |              |         |             |
|    3     | EXECUTED |      0      | Execute Successfully |      None     |       insert into t1(id,c1,c2) values(1,1,1)       |       1       | 1560411582_21_00000002 | 192_168_100_90_3306_go |    0.002     |   None  |    0.004    |
|          |          |             | Backup Successfully  |               |                                                    |               |                        |                        |              |         |             |
+----------+----------+-------------+----------------------+---------------+----------------------------------------------------+---------------+------------------------+------------------------+--------------+---------+-------------+
```
