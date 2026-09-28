---
title: "MySQL InnoDB Cluser  |  Mysql 5.7 集群"
date: "2018-01-10 15:29:25"
category: "lnmp"
source: "https://blog.51cto.com/hequan/2059436"
---
> **内容介绍**
>
> 本文是LNMP/LAMP Web 服务架构与优化,记录了「MySQL InnoDB Cluser  |  Mysql 5.7 集群」的相关内容。主要涉及:> - 目前 本集群 应用在自己的 django demo 环境上，暂时稳定运行。 > - 欢迎加群 620176501 讨论 Mysql 集群的应用。 ---…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

> - 目前 本集群 应用在自己的 django demo 环境上，暂时稳定运行。
> - 欢迎加群      620176501                        讨论 Mysql 集群的应用。

---

### **核心架构**

```shell
* MySQL 5.7 引入了 Group Replication 功能，可以在一组 MySQL 服务器之间实现自动主机选举，形成一主多从结构。经过高级配置后，可以实现多主多从结构。
* MySQL Router 是一个轻量级透明中间件，可以自动获取上述集群的状态，规划 SQL 语句，分配到合理的 MySQL 后端进行执行。
* MySQL Shell 是一个同时支持 JavaScript 和 SQL 的交互程序，可以快速配置 InnoDB Cluster。
```shel
l

![](assets/2059436/01_8815cd9266b5f987ffcdd17c72341bf2.png)

---

### 部署

- 本次共3台机器，设置主机名及hosts  |  配置每台服务 my.cnf 中report_host 字段，为自己的 hostname

```shell
192.168.10.123 db1
192.168.10.124 db2
192.168.10.125 db3
```

- 安装 mysql5.7.21   ,可以参考下面的安装基本，我搭建的时候就是用的这个。

```shellhttp
://blog.51cto.com/hequan/2067341
```

- 安装mysql-shell

```shellwget
https://cdn.mysql.com//Downloads/MySQL-Shell/mysql-shell-1.0.11-1.el7.x86_64.rpm
yum install mysql-shell-1.0.11-1.el7.x86_64.rpm  -y
```sq
l

- 设置相关用户的权限，生产环境   可以不是  root用户

```shellgrant
all   privileges  on *.*  to 'root'@'%'  identified by '123456';
GRANT ALL PRIVILEGES ON mysql_innodb_cluster_metadata.* TO root@'%' WITH GRANT OPTION;
GRANT RELOAD, SHUTDOWN, PROCESS, FILE, SUPER, REPLICATION SLAVE, REPLICATION CLIENT, \
CREATE USER ON *.* TO root@'%' WITH GRANT OPTION;
GRANT SELECT ON *.* TO root@'%' WITH GRANT OPTION;
flush privileges;
```

---

### mysqlsh

```shell
[root@db1 ~]#  mysqlsh

## 检查mysql 配置文件   (3台主机都要操作此步骤)
dba.checkInstanceConfiguration('root@db1:3306')

+----------------------------------+---------------+----------------+--------------------------------------------------+
| Variable                         | Current Value | Required Value | Note                                             |
+----------------------------------+---------------+----------------+--------------------------------------------------+
| binlog_checksum                  | CRC32         | NONE           | Update the server variable or restart the server |
| binlog_format                    | MIXED         | ROW            | Update the server variable or restart the server |
| enforce_gtid_consistency         | OFF           | ON             | Restart the server                               |
| gtid_mode                        | OFF           | ON             | Restart the server                               |
| log_slave_updates                | 0             | ON             | Restart the server                               |
| master_info_repository           | FILE          | TABLE          | Restart the server                               |
| relay_log_info_repository        | FILE          | TABLE          | Restart the server                               |
| transaction_write_set_extraction | OFF           | XXHASH64       | Restart the server                               |
+----------------------------------+---------------+----------------+--------------------------------------------------+

## 修复mysql 配置文件，    必须用 root(3台主机都要操作此步骤)
dba.configureLocalInstance('root@db1:3306')

Please provide the password for 'root@db1:3306':
Detecting the configuration file...
Found configuration file at standard location: /etc/my.cnf
Do you want to modify this file? [Y|n]:  [Y|n]: Y

## 重启mysql

## 重新检查  (3台主机都要操作此步骤)
dba.checkInstanceConfiguration('root@db1:3306')
Please provide the password for 'root@db1:3306':
Validating instance...

The instance 'db1:3306' is valid for Cluster usage
{
    "status": "ok"
}
```javascrip
t

```shell
## 登陆
mysqlsh --uri root@db1:3306

## 创建集群     main
mysql-js> var cluster = dba.createCluster('main')
A new InnoDB cluster will be created on instance 'hequan@db1:3306'.

Creating InnoDB cluster 'main' on 'hequan@db1:3306'...
Adding Seed Instance...

Cluster successfully created. Use Cluster.addInstance() to add MySQL instances.
At least 3 instances are needed for the cluster to be able to withstand up to
one server failure.

## 添加子节点
mysql-js> cluster.addInstance('root@db2:3306')
mysql-js> cluster.addInstance('root@db3:3306')

## 查看节点信息
mysql-js> cluster.status()

## 将配置 持久化，写入到  my.cnf
mysql-js>  \connect db1
mysql-js> dba.configureLocalInstance('db1:3306')

## 查看基本信息
mysql-js>  cluster.describe();

## 退出之后，再查看节点信息
var cluster = dba.getCluster();
cluster.status();
```

### Mysql-route 设置

```shellwget
https://cdn.mysql.com//Downloads/MySQL-Router/mysql-router-2.1.4-1.el7.x86_64.rpm
yum install -y mysql-router-2.1.4-1.el7.x86_64.rpm
```sq
l

```shell
## 此命令会更新 /etc/mysqlrouter/mysqlrouter.conf 中的配置信息, 可以是别的机器 这里选择的为db2

[root@db2 ~]# mysqlrouter --bootstrap root@db1:3306 --user mysqlrouter

Please enter MySQL password for root:
WARNING: The MySQL server does not have SSL configured and metadata used by the router may be transmitted unencrypted.

Bootstrapping system MySQL Router instance...
MySQL Router  has now been configured for the InnoDB cluster 'main'.

The following connection information can be used to connect to the cluster.

Classic MySQL protocol connections to cluster 'main':
- Read/Write Connections: localhost:6446    读写
- Read/Only Connections: localhost:6447     只读

X protocol connections to cluster 'main':
- Read/Write Connections: localhost:64460
- Read/Only Connections: localhost:64470

Existing configurations backed up to /etc/mysqlrouter/mysqlrouter.conf.bak
[root@db2 ~]# systemctl start mysqlrouter

## 启动
systemctl start mysqlrouter
systemctl enable mysqlrouter

## 查看端口
[root@db2 ~]# netstat -lntup
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:64460           0.0.0.0:*               LISTEN      2958/mysqlrouter
tcp        0      0 0.0.0.0:6446            0.0.0.0:*               LISTEN      2958/mysqlrouter
tcp        0      0 0.0.0.0:6447            0.0.0.0:*               LISTEN      2958/mysqlrouter
tcp        0      0 0.0.0.0:64470           0.0.0.0:*               LISTEN      2958/mysqlrouter

## 验证
mysql -u root -h 127.0.0.1 -P 6446 -p

select @@port;
select @@hostname;
```

---

### 故障模拟

```shell
##关闭 db1 数据库，自动切换如下：

"topology": {
            "db1:3306": {
                "address": "db1:3306",
                "mode": "R/O",
                "readReplicas": {},
                "role": "HA",
                "status": "(MISSING)"
            },
            "db2:3306": {
                "address": "db2:3306",
                "mode": "R/W",
                "readReplicas": {},
                "role": "HA",
                "status": "ONLINE"
            },
            "db3:3306": {
                "address": "db3:3306",
                "mode": "R/O",
                "readReplicas": {},
                "role": "HA",
                "status": "ONLINE"
            }
```

```shell
##重启db2 ,执行命令

mysql> show databases;
ERROR 2013 (HY000): Lost connection to MySQL server during query
mysql> show databases;
ERROR 2006 (HY000): MySQL server has gone away
No connection. Trying to reconnect...
Connection id:    20
Current database: *** NONE ***
mysql> select @@hostname;
+------------+
| @@hostname |
+------------+
| db1        |
+------------+

##重启节点后，需要手动加入
"db2:3306": {
                "address": "db2:3306",
                "mode": "R/O",
                "readReplicas": {},
                "role": "HA",
                "status": "(MISSING)"

cluster.rejoinInstance('root@db2:3306')
The instance 'db2:3306' was successfully added to the MySQL Cluster.
```

```shell
## 所有节点都重启了，重新加入

mysqlsh --uri root@db1:3306
mysql-js> var cluster = dba.rebootClusterFromCompleteOutage();

Reconfiguring the default cluster from complete outage...

The instance 'db2:3306' was part of the cluster configuration.
Would you like to rejoin it to the cluster? [y|N]: y

The instance 'db3:3306' was part of the cluster configuration.
Would you like to rejoin it to the cluster? [y|N]: y

The cluster was successfully rebooted.
```shel
l

---

### 报错总结：

```
ERROR: Error joining instance to cluster: 'db2:3306' - Query failed. MySQL Error (3092): The server is not configured properly to be an active member of the group. Please see more details on error log.. Query: START group_replication (RuntimeError)

##登陆 db2 数据库 执行 reset master;
```

```shell
## 如果出现了   "status": "NO_QUORUM"     执行修复，重新加入
## 暂未测试

cluster.forceQuorumUsingPartitionOf("db1:3306")

mysql-js> cluster.rejoinInstance('root@db2:3306')
mysql-js> cluster.rejoinInstance('root@db3:3306')
```

---

### 附言：

> 官方文档：   https://dev.mysql.com/doc/refman/5.7/en/mysql-innodb-cluster-userguide.html

```shell
节点有哪状态

    * ONLINE  - 节点状态正常。
    * OFFLINE  -   实例在运行，但没有加入任何Cluster。
    * RECOVERING - 实例已加入Cluster，正在同步数据。
    * ERROR  -  同步数据发生异常。
    * UNREACHABLE -  与其他节点通讯中断，可能是网络问题，可能是节点crash。
    * MISSING 节点已加入集群，但未启动group replication

集群有哪些状态

	* OK – 所有节点处于online状态，有冗余节点。
	* OK_PARTIAL – 有节点不可用，但仍有冗余节点。
	* OK_NO_TOLERANCE – 有足够的online节点，但没有冗余，例如：两个节点的Cluster，其中一个挂了，集群就不可用了。
	* NO_QUORUM – 有节点处于online状态，但达不到法定节点数，此状态下Cluster无法写入，只能读取。
	* UNKNOWN – 不是online或recovering状态，尝试连接其他实例查看状态。
	* UNAVAILABLE – 组内节点全是offline状态，但实例在运行，可能实例刚重启还没加入Cluster。
```
