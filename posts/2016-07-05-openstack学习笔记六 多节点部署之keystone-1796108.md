---
title: "openstack学习笔记六 多节点部署之keystone"
date: "2016-07-05 22:25:01"
category: "openstack"
source: "https://blog.51cto.com/hequan/1796108"
---
> **内容介绍**
>
> 本文分两部分:先讲 Keystone 身份认证原理,用「住宾馆」类比 User、Credentials、
> Token、Tenant、Service、Endpoint、Role 等概念,并在已部署节点 h1 上演练
> endpoint/service/role/user/tenant 的增删改查命令;随后在 h4(192.168.1.204)节点上
> 实操安装配置 Liberty 版 keystone:yum 安装、openstack-db 初始化数据库、
> keystone.conf 配置 admin_token 与 MySQL 连接、用 SERVICE_TOKEN 创建服务和
> endpoint、建立 admin 租户/角色/用户,最后关闭 token 改用 admin 账号登录。

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。
> 文中 `keystone` CLI 与 `openstack-db` 脚本来自 python-keystoneclient / openstack-utils,Queens 版起均已移除,
> 新版统一使用 `openstack` CLI(如 `openstack endpoint list`);tenant 概念后续更名为 project,
> Keystone v2.0 API 也已废弃,现行版本为 v3(仅 5000 端口)。

---

## 1. Keystone 是什么

**keystone** 对用户进行验证,每个组件必须得使用一个用户向 keystone 进行注册,只有成功了,这个组件才能正常工作。所以当我们在创建其他组件的时候,也包括 keystone 本身,都得为这个组件创建一个用户名和密码。

keystone 也必须知道这些组件到底在什么地方,比如在哪台主机上。

![手绘示意图:前台验证身份发放房卡,用户凭卡使用住宿、餐饮等服务](assets/1796108/01_wKioL1d7wsrRg91LAAJhGY7B4eM943.png)

用「住宾馆」类比各概念:

| 概念 | 类比 |
| --- | --- |
| User | 住宾馆的人 |
| Credentials | 开启房间的钥匙 |
| Authentication | 宾馆为了拒绝不必要的人进出宾馆,专门设置的机制,只有拥有钥匙的人才能进出 |
| Token | 也是一种钥匙,有点特别 |
| Tenant | 宾馆 |
| Service | 宾馆可以提供的服务类别,比如,饮食类,娱乐类 |
| Endpoint | 具体的一种服务,比如吃烧烤,打羽毛球 |
| Role | VIP 等级,VIP 越高,享有越高的权限 |

![白底文字笔记截图:用户属于租户,租户即项目,服务对应 services 用户](assets/1796108/02_wKioL1d7wtuQjIIKAAL5H8-n9Ow961.png)

## 2. 管理命令演练(h1 已部署节点)

先 source 管理员凭据,查看 endpoint 列表:

```shell
[root@h1 ~]# source  keystonerc_admin
[root@h1 ~(keystone_admin)]# keystone  endpoint-list
+----------------------------------+-----------+-------------------------------------------------+-------------------------------------------------+--------------------------------------------+----------------------------------+
|                id                |   region  |                    publicurl                    |                   internalurl                   |                  adminurl                  |            service_id            |
+----------------------------------+-----------+-------------------------------------------------+-------------------------------------------------+--------------------------------------------+----------------------------------+
| 03bf88d48e2648149242a571684fbfce | RegionOne |            http://192.168.1.201:9696            |            http://192.168.1.201:9696            |         http://192.168.1.201:9696          | 1100243c5a694bc5857218dd0543297b |
| 1b5ccdf306484fefadc63d1eeb20de5d | RegionOne |             http://127.0.0.1:8774/v3            |             http://127.0.0.1:8774/v3            |          http://127.0.0.1:8774/v3          | 4bda82ded4db46f68428d4e00247c14c |
| 2408bc6cb5164053b86c0983fd39961a | RegionOne | http://192.168.1.201:8080/v1/AUTH_%(tenant_id)s | http://192.168.1.201:8080/v1/AUTH_%(tenant_id)s |         http://192.168.1.201:8080          | 30c62c3c0797462a8bd4ff059a71296e |
| 432e655e85614a5eb69b7de5c5aacf34 | RegionOne |    http://192.168.1.201:8776/v2/%(tenant_id)s   |    http://192.168.1.201:8776/v2/%(tenant_id)s   | http://192.168.1.201:8776/v2/%(tenant_id)s | 5d60cb24769e403cb10bb70cb1077f2b |
| 4d5c1e505b30467c9966a5e5e93feef0 | RegionOne |            http://192.168.1.201:9292            |            http://192.168.1.201:9292            |         http://192.168.1.201:9292          | 87d30bb0dd8e44ccba00127f77831e9e |
| 8683d84884d74e7c8a73513260aec774 | RegionOne |            http://192.168.1.201:8080            |            http://192.168.1.201:8080            |         http://192.168.1.201:8080          | e6ced100d94e4f3b86cccfc82e12b83a |
| 8fa0e177bac746f79e229f16954506fb | RegionOne |    http://192.168.1.201:8776/v1/%(tenant_id)s   |    http://192.168.1.201:8776/v1/%(tenant_id)s   | http://192.168.1.201:8776/v1/%(tenant_id)s | dc75a046272548db99e1cbbe93c2025c |
| 9006207b29a04700922ee55905a7f445 | RegionOne |    http://192.168.1.201:8774/v2/%(tenant_id)s   |    http://192.168.1.201:8774/v2/%(tenant_id)s   | http://192.168.1.201:8774/v2/%(tenant_id)s | 1c9e6e4d00824327bfe4e8e7175317e1 |
| a9ec253a705c4b3c9848b5bed32e9768 | RegionOne |     http://192.168.1.201:8773/services/Cloud    |     http://192.168.1.201:8773/services/Cloud    |  http://192.168.1.201:8773/services/Admin  | 81bbcf83509a42e9a867914cde84e9d4 |
| bcab3bbc3281451494428315b24b0dba | RegionOne |            http://192.168.1.201:8777            |            http://192.168.1.201:8777            |         http://192.168.1.201:8777          | 8f54fc4364de49efbeb72020bf2aa176 |
| e3d9a4fa64bd441ea3fe143b1d72b8a4 | RegionOne |          http://192.168.1.201:5000/v2.0         |          http://192.168.1.201:5000/v2.0         |      http://192.168.1.201:35357/v2.0       | 02ce8247c5924913a73422bcf5275c40 |
+----------------------------------+-----------+-------------------------------------------------+-------------------------------------------------+--------------------------------------------+----------------------------------+
```

### 服务

```shell
[root@h1 ~(keystone_admin)]# keystone service-list     服务
+----------------------------------+------------+--------------+--------------------------------+
|                id                |    name    |     type     |          description           |
+----------------------------------+------------+--------------+--------------------------------+
| 8f54fc4364de49efbeb72020bf2aa176 | ceilometer |   metering   |   Openstack Metering Service   |
| dc75a046272548db99e1cbbe93c2025c |   cinder   |    volume    |         Cinder Service         |
| 5d60cb24769e403cb10bb70cb1077f2b |  cinderv2  |   volumev2   |       Cinder Service v2        |
| 87d30bb0dd8e44ccba00127f77831e9e |   glance   |    image     |    OpenStack Image Service     |
| 02ce8247c5924913a73422bcf5275c40 |  keystone  |   identity   |   OpenStack Identity Service   |
| 1100243c5a694bc5857218dd0543297b |   neutron  |   network    |   Neutron Networking Service   |
| 1c9e6e4d00824327bfe4e8e7175317e1 |    nova    |   compute    |   Openstack Compute Service    |
| 81bbcf83509a42e9a867914cde84e9d4 |  nova_ec2  |     ec2      |          EC2 Service           |
| 4bda82ded4db46f68428d4e00247c14c |   novav3   |  computev3   |  Openstack Compute Service v3  |
| 30c62c3c0797462a8bd4ff059a71296e |   swift    | object-store | Openstack Object-Store Service |
| e6ced100d94e4f3b86cccfc82e12b83a |  swift_s3  |      s3      |      Openstack S3 Service      |
+----------------------------------+------------+--------------+--------------------------------+
```

### 角色

```shell
[root@h1 ~(keystone_admin)]# keystone  role-list            角色
+----------------------------------+---------------+
|                id                |     name      |
+----------------------------------+---------------+
| 7455105a501842e097e7825257eb5be4 | ResellerAdmin |
| 5d2a5d2f80d442e09b9c3d514ded412e | SwiftOperator |
| 9fe2ff9ee4384b1894a90878d3e92bab |    _member_   |
| 794f590d02344bafb280f37ff29433ae |     admin     |
+----------------------------------+---------------+

[root@h1 ~(keystone_admin)]#  keystone  role-create  --name  test1
+----------+----------------------------------+
| Property |              Value               |
+----------+----------------------------------+
|    id    | 467d36315d9c4e529e9400c606f8d7a2 |
|   name   |              test1               |
+----------+----------------------------------+
[root@h1 ~(keystone_admin)]#  keystone  role-delete  test1
```

### 用户

```shell
[root@h1 ~(keystone_admin)]# keystone  user-list    用户
+----------------------------------+------------+---------+----------------------+
|                id                |    name    | enabled |        email         |
+----------------------------------+------------+---------+----------------------+
| 1627cc3d61c04f9db9608e9703a01371 |   admin    |   True  |    root@localhost    |
| 04247710cdf34914a7f5b315ab166731 | ceilometer |   True  | ceilometer@localhost |
| cb5e12e30a4a4c1dae57255c184b8b30 |   cinder   |   True  |   cinder@localhost   |
| 632fb20205ea4c40988d7d65b2844ff6 |   glance   |   True  |  glance@localhost    |
| 23c4fb48a5a247d68e50c6b74fb6f035 |    http    |   True  |                      |
| 80069f5c8edc454b8038e7f116df4ff5 |  neutron   |   True  |  neutron@localhost   |
| adbcaaf58d09495988b57be8e82b4e6b |    nova    |   True  |   nova@localhost     |
| 4f488ff4859e4973afefea6e7872ed83 |   swift    |   True  |  swift@localhost     |
+----------------------------------+------------+---------+----------------------+

[root@h1 ~(keystone_admin)]#  keystone  user-create  --name hequan  --pass hequan  --email  hequan2011@sina.com
+----------+----------------------------------+
| Property |              Value               |
+----------+----------------------------------+
|  email   |       hequan2011@sina.com        |
| enabled  |               True               |
|    id    | 9d12907283b64b02a80f1e98074a9c84 |
|   name   |              hequan              |
| username |              hequan              |
+----------+----------------------------------+

[root@h1 ~(keystone_admin)]#  keystone  user-get      hequan              ##查看信息
[root@h1 ~(keystone_admin)]#  keystone  user-delete    hequan
[root@h1 ~(keystone_admin)]#  keystone  user-password-update    --pass  hequan1 hequan   ##密码更新
[root@h1 ~(keystone_admin)]#   keystone  user-role-add  --user hequan  --role  _member_  --tenant=http  #划分角色和租户
```

### 租户

```shell
[root@h1 ~(keystone_admin)]# keystone tenant-list                租户
+----------------------------------+----------+---------+
|                id                |   name   | enabled |
+----------------------------------+----------+---------+
| 43986fb013804aa0a04ca277e4d0e69c |  admin   |   True  |
| 1af10fa8077e4b52b3427786bb15e968 |   http   |   True  |
| 842da711a1b740ddbf006a9f0a7ee116 | services |   True  |       ##内置服务默认都属于services
+----------------------------------+----------+---------+

[root@h1 ~(keystone_admin)]# keystone tenant-create --name  123    ###创建租户123
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
| description |                                  |
|   enabled   |               True               |
|      id     | c2a2e3aadf614bb08b1fc943157b668e |
|     name    |               123                |
+-------------+----------------------------------+
[root@h1 ~(keystone_admin)]# keystone tenant-delete   123
```

## 3. 安装配置 keystone(h4 节点)

安装思路:

1. 首先创建数据库
2. 使用 token 登录 keystone
3. 创建服务、endpoint
4. 创建用户
5. 关闭 token 登录,使用 admin 登录

### 3.1 基本环境

```shell
192.168.1.204            h4                     ##  keystone

systemctl   stop    NetworkManager
systemctl   disable  NetworkManager

[root@h4 ~]# yum install centos-release-openstack-liberty
[root@h4 ~]# yum install  openstack-keystone openstack-utils  openstack-selinux  -y
```

### 3.2 初始化数据库

```shell
[root@h4 ~]# openstack-db --init --service  keystone  --rootpw  123456    --password  keystone
keystone default DB is not mysql.  Would you like to reset to mysql now? (y/n): y
mysql-server is not installed.  Would you like to install it now? (y/n): y
mysqld is not running.  Would you like to start it now? (y/n): y
Verified connectivity to MySQL.
Creating 'keystone' database.
Initializing the keystone database, please wait...
Complete!

[root@h4 ~]# mysql -uroot -p123456
MariaDB [(none)]> show databases;
```

### 3.3 修改 keystone.conf

生成 token,并检查所在目录:

```shell
[root@h4 keystone]# openssl   rand -hex 10
73fa731f6fa567630fdd

[root@h4 keystone]# pwd
/etc/keystone
[root@h4 keystone]# vim keystone.conf
```

```ini
admin_token = 73fa731f6fa567630fdd
rabbit_host = localhost
rabbit_port = 5672
rabbit_hosts = $rabbit_host:$rabbit_port
rabbit_use_ssl = false
rabbit_userid = guest
rabbit_password = guest
rabbit_login_method = AMQPLAIN
rabbit_virtual_host = /
connection = mysql://keystone:keystone@192.168.1.204/keystone    ###用到上面写的用户名和密码
```

### 3.4 启动服务

```shell
[root@h4 keystone]# systemctl   list-unit-files  | grep keyston
openstack-keystone.service             disabled

[root@h4 keystone]# systemctl  start  openstack-keystone.service
[root@h4 keystone]# systemctl  enable  openstack-keystone.service
```

### 3.5 使用 token 登录

现在没有用户,只有 token。创建 `keystone_token` 文件:

```shell
cat keystone_token               ##创建文件
export   SERVICE_TOKEN=73fa731f6fa567630fdd
export   SERVICE_ENDPOINT=http://192.168.1.204:35357/v2.0
export PS1='[\u@\h \W(keystone_token)]\$ '

source keystone_token
```

确认服务与端口正常:

```shell
[root@h4 ~]# ps aux | grep keystone
keystone  3343  1.5  1.6 321844 68704 ?        Ss   20:10   0:05 /usr/bin/python2 /usr/bin/keystone-all

[root@h4 ~]# netstat -lntup | grep 35357
tcp        0      0 0.0.0.0:35357           0.0.0.0:*               LISTEN      3343/python2
```

注册 keystone 服务:

```shell
[root@h4 ~]# keystone service-list

[root@h4 ~]# keystone service-create --name keystone --type identity  --description="keystone"
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
| description |             keystone             |
|   enabled   |               True               |
|      id     | e0c6163cb7dd42098225f13a3fa4220e |
|     name    |             keystone             |
|     type    |             identity             |
+-------------+----------------------------------+
```

### 3.6 创建 endpoint

endpoint 的地址参数可以先找一个模板去抄,在 h1 上看现成的 endpoint 与 service:

```shell
[root@h1 ~(keystone_admin)]# keystone  endpoint-list
| e3d9a4fa64bd441ea3fe143b1d72b8a4 | RegionOne |          http://192.168.1.201:5000/v2.0         |          http://192.168.1.201:5000/v2.0         |      http://192.168.1.201:35357/v2.0       | 02ce8247c5924913a73422bcf5275c40 |

[root@h1 ~(keystone_admin)]# keystone service-list
| 02ce8247c5924913a73422bcf5275c40 |  keystone  |   identity   |   OpenStack Identity Service   |
```

照模板换成 h4 自己的地址:

```shell
[root@h4 ~]# keystone  endpoint-create  --service-id  e0c6163cb7dd42098225f13a3fa4220e \
  --publicurl  'http://192.168.1.204:5000/v2.0' \
  --internalurl 'http://192.168.1.204:5000/v2.0' \
  --adminurl    'http://192.168.1.204:35357/v2.0'
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
|   adminurl  | http://192.168.1.204:35357/v2.0  |
|      id     | 810e5faef22f44aebd17f55d1808e3c5 |
| internalurl |  http://192.168.1.204:5000/v2.0  |
|  publicurl  |  http://192.168.1.204:5000/v2.0  |
|    region   |            regionOne             |
|  service_id | e0c6163cb7dd42098225f13a3fa4220e |
+-------------+----------------------------------+
```

### 3.7 创建管理员

创建 admin 租户、角色、用户并授权:

```shell
[root@h4 ~]# keystone tenant-create  --name  admin
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
| description |                                  |
|   enabled   |               True               |
|      id     | 3a331dd90062458b8fcc259ce84be0e5 |
|     name    |              admin               |
+-------------+----------------------------------+

[root@h4 ~]# keystone role-create --name admin
+----------+----------------------------------+
| Property |              Value               |
+----------+----------------------------------+
|    id    | c63ed09a433144108a23a592632e2e08 |
|   name   |              admin               |
+----------+----------------------------------+

[root@h4 ~]# keystone  user-create --name admin --pass 123456
+----------+----------------------------------+
| Property |              Value               |
+----------+----------------------------------+
|  email   |                                  |
| enabled  |               True               |
|    id    | 172b6a61991e4fbeafe9039688eb2afc |
|   name   |              admin               |
| username |              admin               |
+----------+----------------------------------+

[root@h4 ~]# keystone  user-role-add  --user admin --tenant admin --role admin
```

切换到 admin 账号登录:

```shell
[root@h4 ~]# cp keystone_token keystone_token_admin
[root@h4 ~(keystone_admin)]# cat keystone_token_admin
unset   SERVICE_TOKEN
unset   SERVICE_ENDPOINT
export OS_TENANT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_AUTH_URL=http://192.168.1.204:35357/v2.0
export PS1='[\u@\h \W(keystone_admin)]\$ '

[root@h4 ~(keystone_admin)]# keystone user-list         ##可以看到就表示成功了
+----------------------------------+-------+---------+-------+
|                id                |  name | enabled | email |
+----------------------------------+-------+---------+-------+
| 172b6a61991e4fbeafe9039688eb2afc | admin |   True  |       |
+----------------------------------+-------+---------+-------+
```

### 3.8 关闭 token 验证

把 `keystone.conf` 里的 `admin_token` 一行注释掉:

```ini
#admin_token = 73fa731f6fa567630fdd
```

至此安装完成。
