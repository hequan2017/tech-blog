---
title: "ERROR : Error appeared during Puppet run: x.x.x.x _keystone.pp"
date: "2016-08-01 22:21:00"
category: ""
source: "https://blog.51cto.com/hequan/1833247"
---
> **内容介绍**
>
> 本文是技术实践笔记,记录了「ERROR : Error appeared during Puppet run: x.x.x.x _keystone.pp」的相关内容。主要涉及:报错 解决: 报错是 在用RDO模式 packstack安装openstack 最新版mitaka时出现的。…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

报错

```shell
ERROR : Error appeared during Puppet run: x.x.x.x_keystone.pp
Error: /Stage[main]/Keystone::Db::Sync/Exec[keystone-manage db_sync]: Failed to call refresh: Command exceeded timeout
You will find full trace in log /var/tmp/packstack/20160801-185048-pwY8Y8/manifests/x.x.x.x_keystone.pp.log
Please check log file /var/tmp/packstack/20160801-185048-pwY8Y8/openstack-setup.log for more information
```

解决:

报错是  在用RDO模式     packstack安装openstack 最新版mitaka时出现的。

是在云上的环境

inet 192.168.1.7/24 brd 192.168.1.255 scope global dynamic eth0               有一个外网IP 42.62.X.X

查看日志

```shell
[root@controller ~]# cd /var/log/keystone/
[root@controller keystone]# ls
keystone.log
2016-08-01 20:34:33.513 14145 ERROR keystone.common.wsgi DBConnectionError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'x.x.x.x' ([Errno 110] Connection timed out)")
2016-08-01 20:34:33.513 14145 ERROR keystone.common.wsgi
2016-08-01 20:35:34.671 14150 WARNING oslo_db.sqlalchemy.engines [req-12a5fe87-1163-4fbb-a049-5225ea65a05a - - - - -] SQL connection failed. 10 attempts left.
```

查看数据库

```shell
MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| cinder             |
| glance             |
| gnocchi            |
| information_schema |
| keystone           |
| mysql              |
| neutron            |
| nova               |
| nova_api           |
| performance_schema |
| test               |
+--------------------+
11 rows in set (0.00 sec)
MariaDB [(none)]> use keystone;
Database changed
MariaDB [keystone]> show tables;
Empty set (0.00 sec)
生成了库  没内容

看用户
MariaDB [mysql]> select  host,user  from user;
+-----------+----------------+
| host      | user           |
+-----------+----------------+
| %         | cinder         |
| %         | glance         |
| %         | gnocchi        |
| %         | keystone_admin |
| %         | neutron        |
| %         | nova           |
| %         | nova_api       |
| 127.0.0.1 | keystone_admin |
| localhost | root           |
+-----------+----------------+
9 rows in set (0.00 sec)
权限是  %，应该是可以的，
```sql

参考   mysql授权localhost&%区别及一直授权错误解决办法

此处多说一句，此处配置%远程其他host有权限访问，那么在mysql的配置文件中 /etc/my.cnf，也需要做一些配置，将bind_address=0.0.0.0或者直接屏蔽掉此项，更多请自行查找资料。

如果想让外面host能访问数据库：（yunjisuan为root密码）

GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'yunjisuan';

flush privileges;

```
[root@controller keystone]# cat   /etc/hosts
127.0.0.1        controller             localhost localhost.localdomain localhost4 localhost4.localdomain4                  ##在127.0.0.1也添加主机名字
::1                   localhost localhost.localdomain localhost6 localhost6.localdomain6
x.x.x.x        controller

[root@controller keystone]# mysql -ukeystone_admin   -p
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.                        ##本机测试可以登录
因为本人实在云上环境搭建的，只有一个eth0是内网，通过云是外网ip，现在不确定服务器 访问绑定的外网ip的方式是什么样的，
是直接eth0到外网ip，就回来了，， 还是过了路由再回来。如果是这样，就相当于远程访问mysql数据库。- -，关系好乱。

[root@controller ~]# route -n   ##这是默认路由
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         192.168.1.1     0.0.0.0         UG    100    0        0 eth0
192.168.1.0     0.0.0.0         255.255.255.0   U     100    0        0 eth0

所以现在要检查一下 安全组。  测试root 无法远程登录。
用别的机器测试mysql服务器可以，安全组没有问题

MariaDB [mysql]> grant  all privileges on *.*   to 'root'@'%'  identified  by 'xxxxxxxx';       ####添加%，就可以远程登录了.

[root@hequan ~]# mysql   -hip        -p    -ukeystone_admin                 ##   本地测试登录无问题。
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.

MariaDB [mysql]> use keystone;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A
Database changed

MariaDB [keystone]> show tables;
+------------------------+
| Tables_in_keystone     |
+------------------------+
| access_token           |
| assignment             |
| config_register        |
| consumer               |
| credential             |
| domain                 |
| endpoint               |

###查看有表了

再次执行，又有新的报错

RROR : Error appeared during Puppet run: x.x.x.x_cinder.pp
Error: Could not prefetch cinder_type provider 'openstack': Execution of '/usr/bin/openstack volume type list --quiet --format csv --long' returned 1: Unable to
CONFIG_CINDER_NETAPP_ESERIES_HOST_TYPE=linux_dm_mp   ##这是  cinder_type

MariaDB [keystone]> use  cinder
Database changed
MariaDB [cinder]> show tables;
Empty set (0.00 sec)
查看 cinder里面没有表，还是有问题。
MariaDB [cinder]> use glance;
Database changed
MariaDB [glance]> show tables;
Empty set (0.00 sec)
glance也没有生成表，，，只有keystone 的好了。

Applying x.x.x.x_keystone.pp
Applying x.x.x.x_glance.pp
Applying x.x.x.x_cinder.pp
x.x.x.x_keystone.pp:                              [ DONE ]
Testing if puppet apply is finished: x.x.x.x_cinder.pp    [ \ ]    $$$##卡在这里

卸载数据库，从新测试，竟然可以了。。= =，我了个大去。感动老天了。。
| %         | cinder         |
| %         | glance         |
| 127.0.0.1 | keystone_admin |
```

总结：方法3个，1是在127.0.0.1 添加主机名，，2 重新设置一遍 root 在msyql 的权限%     3 卸载掉数据库，重新测试。

打算一会测试  用内网ip,  然后在路由器上做  80映射，这样应该会好一点。不知道行不行。简直是作死，在云上搭建openstack。。。。测试完。

**** Installation completed successfully ******

Additional information:

* Time synchronization installation was skipped. Please note that unsynchronized time on server instances might be problem for some OpenStack components.

* File /root/keystonerc_admin has been created on OpenStack client host x.x.x.x . To use the command line tools you need to source the file.

* To access the OpenStack Dashboard browse to http://x.x.x.x /dashboard .

Please, find your login credentials stored in the keystonerc_admin in your home directory.

* Because of the kernel update the host   x.x.x.x  requires reboot.

* Because of the kernel update the host 127.0.0.1 requires reboot.

* The installation log file is available at: /var/tmp/packstack/20160801-224547-mTb9CN/openstack-setup.log

* The generated manifests are available at: /var/tmp/packstack/20160801-224547-mTb9CN/manifests

```shell
[root@controller ~]# netstat -lntup
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:8774            0.0.0.0:*               LISTEN      21105/python2
tcp        0      0 0.0.0.0:8775            0.0.0.0:*               LISTEN      21105/python2
tcp        0      0 0.0.0.0:9191            0.0.0.0:*               LISTEN      19676/python2
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      1307/httpd
tcp        0      0 0.0.0.0:8776            0.0.0.0:*               LISTEN      20207/python2
tcp        0      0 0.0.0.0:25672           0.0.0.0:*               LISTEN      10588/beam.smp
tcp        0      0 0.0.0.0:8777            0.0.0.0:*               LISTEN      1307/httpd
tcp        0      0 0.0.0.0:8041            0.0.0.0:*               LISTEN      1307/httpd
tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      31512/mongod
tcp        0      0 0.0.0.0:8042            0.0.0.0:*               LISTEN      1307/httpd
tcp        0      0 0.0.0.0:3306            0.0.0.0:*               LISTEN      17028/mysqld
tcp        0      0 0.0.0.0:11211           0.0.0.0:*               LISTEN      25302/memcached
tcp        0      0 0.0.0.0:9292            0.0.0.0:*               LISTEN      19705/python2
tcp        0      0 0.0.0.0:111             0.0.0.0:*               LISTEN      22134/rpcbind
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      1307/httpd
tcp        0      0 0.0.0.0:4369            0.0.0.0:*               LISTEN      1/systemd
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      816/sshd
tcp        0      0 0.0.0.0:35357           0.0.0.0:*               LISTEN      1307/httpd
tcp        0      0 0.0.0.0:16509           0.0.0.0:*               LISTEN      22855/libvirtd
tcp        0      0 0.0.0.0:9696            0.0.0.0:*               LISTEN      24517/python2
tcp        0      0 0.0.0.0:6080            0.0.0.0:*               LISTEN      22974/python2
tcp6       0      0 :::5672                 :::*                    LISTEN      10588/beam.smp
tcp6       0      0 :::111                  :::*                    LISTEN      22134/rpcbind
tcp6       0      0 :::22                   :::*                    LISTEN      816/sshd
tcp6       0      0 :::16509                :::*                    LISTEN      22855/libvirtd
udp        0      0 0.0.0.0:11211           0.0.0.0:*                           25302/memcached
udp        0      0 0.0.0.0:11431           0.0.0.0:*                           585/dhclient
udp        0      0 0.0.0.0:8125            0.0.0.0:*                           29029/python2
udp        0      0 0.0.0.0:68              0.0.0.0:*                           585/dhclient
udp        0      0 0.0.0.0:111             0.0.0.0:*                           22134/rpcbind
udp        0      0 127.0.0.1:323           0.0.0.0:*                           558/chronyd
udp        0      0 0.0.0.0:685             0.0.0.0:*                           22134/rpcbind
udp        0      0 0.0.0.0:4952            0.0.0.0:*                           32304/python2
udp6       0      0 :::111                  :::*                                22134/rpcbind
udp6       0      0 ::1:323                 :::*                                558/chronyd
udp6       0      0 :::685                  :::*                                22134/rpcbind
udp6       0      0 :::38397                :::*                                585/dhclient
```
