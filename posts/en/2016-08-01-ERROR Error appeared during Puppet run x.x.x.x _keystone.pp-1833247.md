---
title: "ERROR : Error appeared during Puppet run: x.x.x.x _keystone.pp"
date: "2016-08-01 22:21:00"
category: "openstack"
source: "https://blog.51cto.com/hequan/1833247"
lang: "en"
---
> **About this post**
>
> A complete troubleshooting record of the `keystone-manage db_sync` timeout error in `x.x.x.x_keystone.pp` when installing OpenStack Mitaka with packstack (RDO mode) on a cloud host. The logs showed that keystone could not connect to the local MySQL (Connection timed out). The author tried three approaches in turn — adding the hostname to 127.0.0.1 in /etc/hosts, granting root `%` remote login, and uninstalling and reinstalling the database — until the installation finally succeeded, followed by a list of listening ports after the installation.

> **Technical notes**
>
> The latest OpenStack version at the time of writing was still Mitaka (released in 2016, long since EOL); for deployments today, use Kolla-Ansible, OpenStack-Ansible, or a current RDO release. Old MariaDB 5.5/10.x versions are no longer supported either. Opening root for `%` remote login in this post was merely a temporary debugging measure for troubleshooting — never grant privileges that way in production.

---

## The Error

The error that appeared while installing the latest OpenStack release, Mitaka, with packstack in RDO mode:

```text
ERROR : Error appeared during Puppet run: x.x.x.x_keystone.pp
Error: /Stage[main]/Keystone::Db::Sync/Exec[keystone-manage db_sync]: Failed to call refresh: Command exceeded timeout
You will find full trace in log /var/tmp/packstack/20160801-185048-pwY8Y8/manifests/x.x.x.x_keystone.pp.log
Please check log file /var/tmp/packstack/20160801-185048-pwY8Y8/openstack-setup.log for more information
```

The environment is on the cloud: the internal network is `inet 192.168.1.7/24 brd 192.168.1.255 scope global dynamic eth0`, plus a public IP 42.62.X.X.

## Troubleshooting

Checking the keystone logs:

```text
[root@controller ~]# cd /var/log/keystone/
[root@controller keystone]# ls
keystone.log
2016-08-01 20:34:33.513 14145 ERROR keystone.common.wsgi DBConnectionError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'x.x.x.x' ([Errno 110] Connection timed out)")
2016-08-01 20:34:33.513 14145 ERROR keystone.common.wsgi
2016-08-01 20:35:34.671 14150 WARNING oslo_db.sqlalchemy.engines [req-12a5fe87-1163-4fbb-a049-5225ea65a05a - - - - -] SQL connection failed. 10 attempts left.
```

Checking the database: the databases for all the components had been created, but the keystone database contained no tables:

```sql
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
```

Then the user privileges:

```sql
MariaDB [mysql]> select host,user from user;
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
```

The privilege is `%`, so it should work. For reference, see the article "The Difference Between MySQL Grants for localhost & % and How to Fix Persistent Grant Errors" (《mysql 授权 localhost & % 区别及一直授权错误解决办法》).

One more note here: when you configure `%` to let other remote hosts access the server, the MySQL configuration file `/etc/my.cnf` also needs a change — set `bind_address=0.0.0.0` or simply comment out that option; for more details, look it up yourself.

If you want external hosts to be able to access the database (yunjisuan is the root password):

```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'yunjisuan';
flush privileges;
```

## Solution 1: Add the Hostname to 127.0.0.1 in /etc/hosts

```text
[root@controller keystone]# cat /etc/hosts
127.0.0.1   controller localhost localhost.localdomain localhost4 localhost4.localdomain4   ## also add the hostname on 127.0.0.1
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
x.x.x.x     controller
```

A local login test works:

```text
[root@controller keystone]# mysql -ukeystone_admin -p
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.
```

Since this was set up in a cloud environment, there is only one eth0 on the internal network, with a public IP bound through the cloud provider. I was not sure how the server accesses its bound public IP — does the traffic go straight out eth0 to the public IP and back, or does it pass through a router first? If the latter, it effectively amounts to remotely accessing the MySQL database.

```text
[root@controller ~]# route -n   ## this is the default route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         192.168.1.1     0.0.0.0         UG    100    0        0 eth0
192.168.1.0     0.0.0.0         255.255.255.0   U     100    0        0 eth0
```

So the security group needs to be checked as well. Testing showed that root could not log in remotely; but testing the MySQL server from another machine worked, which means the security group was fine.

## Solution 2: Grant root the % Remote Login Privilege

```sql
MariaDB [mysql]> grant all privileges on *.* to 'root'@'%' identified by 'xxxxxxxx';   ## adding % allows remote login
```

The local test login had no problems:

```text
[root@hequan ~]# mysql -h ip -p -ukeystone_admin
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.
```

```sql
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
```

The keystone database has tables now.

## The Subsequent cinder.pp Error

Running it again produced a new error:

```text
ERROR : Error appeared during Puppet run: x.x.x.x_cinder.pp
Error: Could not prefetch cinder_type provider 'openstack': Execution of '/usr/bin/openstack volume type list --quiet --format csv --long' returned 1: Unable to
```

The corresponding option in the answer file is `CONFIG_CINDER_NETAPP_ESERIES_HOST_TYPE=linux_dm_mp` (this is cinder_type-related configuration).

```sql
MariaDB [keystone]> use cinder
Database changed
MariaDB [cinder]> show tables;
Empty set (0.00 sec)
```

There were no tables in cinder, so something was still wrong:

```sql
MariaDB [cinder]> use glance;
Database changed
MariaDB [glance]> show tables;
Empty set (0.00 sec)
```

glance had not generated tables either; only keystone was fine.

```text
Applying x.x.x.x_keystone.pp
Applying x.x.x.x_glance.pp
Applying x.x.x.x_cinder.pp
x.x.x.x_keystone.pp:                              [ DONE ]
Testing if puppet apply is finished: x.x.x.x_cinder.pp    [ \ ]    ## stuck here
```

## Solution 3: Uninstall and Reinstall the Database

Uninstalled the database and tested again — and surprisingly it worked:

```text
| %         | cinder         |
| %         | glance         |
| 127.0.0.1 | keystone_admin |
```

**Summary: there are 3 methods** — 1. add the hostname on 127.0.0.1; 2. set the root `%` privilege in MySQL again; 3. uninstall the database and test again.

I plan to test with the internal IP in a bit and set up port 80 mapping on the router, which should work a little better. Not sure whether it will. It is simply asking for trouble, setting up OpenStack on a cloud host... testing done.

## Installation Successful

```text
**** Installation completed successfully ******

Additional information:

* Time synchronization installation was skipped. Please note that unsynchronized time on server instances might be problem for some OpenStack components.

* File /root/keystonerc_admin has been created on OpenStack client host x.x.x.x. To use the command line tools you need to source the file.

* To access the OpenStack Dashboard browse to http://x.x.x.x/dashboard .

Please, find your login credentials stored in the keystonerc_admin in your home directory.

* Because of the kernel update the host x.x.x.x requires reboot.

* Because of the kernel update the host 127.0.0.1 requires reboot.

* The installation log file is available at: /var/tmp/packstack/20160801-224547-mTb9CN/openstack-setup.log

* The generated manifests are available at: /var/tmp/packstack/20160801-224547-mTb9CN/manifests
```

The list of listening ports after the installation completed:

```text
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
