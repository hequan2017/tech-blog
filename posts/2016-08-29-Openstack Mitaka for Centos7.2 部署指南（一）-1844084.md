---
title: "Openstack Mitaka for  Centos7.2 部署指南（一）"
date: "2016-08-29 21:58:02"
category: "openstack"
source: "https://blog.51cto.com/hequan/1844084"
---
> **内容介绍**
>
> 本文是OpenStack 私有云部署与运维笔记,记录了「Openstack Mitaka for  Centos7.2 部署指南（一）」的相关内容。主要涉及:本文主要参考 [https://www.zybuluo.com/ncepuwanghui/note/389373](https://www.zybuluo.co…

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护(EOL),生产环境建议迁移至 Rocky Linux / AlmaLinux / Ubuntu LTS。

---

本文主要参考

[https://www.zybuluo.com/ncepuwanghui/note/389373](https://www.zybuluo.com/ncepuwanghui/note/389373)

OpenStack Mitaka for Ubuntu 16.04 LTS 部署指南

[http://docs.openstack.org/mitaka/install-guide-rdo/](http://docs.openstack.org/mitaka/install-guide-rdo/)

官方文档

把上面的Ubuntu 换成Centos，其他详情请看上面的部署指南

---

**4.1配置OpenStack**

```bash
yum install centos-release-openstack-mitaka

安装OpenStack client：
yum install python-openstackclient

安装MariaDB
yum install mariadb mariadb-server python2-PyMySQL

[root@controller ~]# vim /etc/my.cnf.d/openstack.cnf
[mysqld]
bind-address = 10.0.0.11
default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8

systemctl enable  mariadb.service
systemctl start  mariadb.service

mysql_secure_installation  ##设置密码
```

安装NoSQL数据库（MongoDB）

注：只有计量服务（Telemetry Service）用到

Controller Node

```bash
① 安装MongoDB
yum install mongodb-server mongodb
[root@controller ~]# vim /etc/mongod.conf
bind_ip = 10.0.0.11
smallfiles = true
systemctl enable mongod.service
systemctl start mongod.service
```

安装消息队列服务（RabbitMQ）

Controller Node

① 安装RabbitMQ

```bash
yum install rabbitmq-server
systemctl enable rabbitmq-server.service
systemctl start rabbitmq-server.service
rabbitmqctl add_user openstack  openstack ##密码
Creating user "openstack" ...
rabbitmqctl set_permissions openstack ".*" ".*" ".*" ##权限
Setting permissions for user "openstack" in vhost "/" ...
```

安装Memcached

身份服务（Identity Service）认证机制需要使用Memcached缓存令牌（Token）

Controller Node

① 安装Memcached

```bash
yum install memcached python-memcached
systemctl enable memcached.service
systemctl start memcached.service
```

4.2 身份服务配置（Identity Service Keystone）

Identity服务采用RESTful设计，使用REST API提供Web服务接口。

注：常见的Web Service 方式有SOAP 、WSDL 、REST 。

部署节点：Controller Node

在MariaDB（MySQL）中创建Keystone数据库

```bash
mysql -uroot -p123456
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY  'keystone';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'keystone';
flush privileges;
quit;

% 则代表了所有的host都能远程访问该mysql。但MySQL官方文档指出， % 并不包括localhost 。因此需要对localhost 和% 都进行授权。
```

生成临时管理身份认证令牌（ADMIN_TOKEN）

生成一个随机值，作为keystone初始配置时的ADMIN_TOKEN

```bash
openssl rand  -hex 10
2d3c132acf773c01838e
```

安装Keystone和Apache HTTP Server with mod_wsgi

本文采用Apache HTTP server with mod_wsgi 监听端口5000 和35357 提供身份服务。默认keystone 服务已经监听端口5000 和35357 ，为避免冲突，需首先关闭keystone服务

```bash
yum install openstack-keystone httpd mod_wsgi
vim  /etc/keystone/keystone.conf
admin_token = ADMIN_TOKEN
connection = mysql+pymysql://keystone:KEYSTONE_DBPASS@controller/keystone
provider = fernet #####Fernet令牌提供者
将配置信息写入到身份服务数据库keystone ：
su -s /bin/sh  -c "keystone-manage db_sync" keystone
初始化Fernet keys:
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
```

vim /etc/httpd/conf/httpd.conf

ServerName controller

vim /etc/httpd/conf.d/wsgi-keystone.conf

Listen 5000Listen 35357

<VirtualHost *:5000>
    WSGIDaemonProcess keystone-public processes=5 threads=1 user=keystone group=keystone display-name=%{GROUP}
    WSGIProcessGroup keystone-public
    WSGIScriptAlias / /usr/bin/keystone-wsgi-public
    WSGIApplicationGroup %{GLOBAL}
    WSGIPassAuthorization On
    ErrorLogFormat "%{cu}t %M"
    ErrorLog /var/log/httpd/keystone-error.log
    CustomLog /var/log/httpd/keystone-access.log combined

    <Directory /usr/bin>
        Require all granted
    </Directory></VirtualHost>

<VirtualHost *:35357>
    WSGIDaemonProcess keystone-admin processes=5 threads=1 user=keystone group=keystone display-name=%{GROUP}
    WSGIProcessGroup keystone-admin
    WSGIScriptAlias / /usr/bin/keystone-wsgi-admin
    WSGIApplicationGroup %{GLOBAL}
    WSGIPassAuthorization On
    ErrorLogFormat "%{cu}t %M"
    ErrorLog /var/log/httpd/keystone-error.log
    CustomLog /var/log/httpd/keystone-access.log combined

    <Directory /usr/bin>
        Require all granted

</Directory></VirtualHost>

```bash
systemctl enable httpd.service
systemctl start httpd.service
```

创建服务实体（Service Entity）和API路径（API Endpoints）

```bash
vim admin ##设置环境变量
export OS_TOKEN=2d3c132acf773c01838e
export OS_URL=http://controller:35357/v3
export OS_IDENTITY_API_VERSION=3
source admin
```

创建服务实体

身份服务管理着一个OpenStack的服务目录，通过服务目录确定其他服务是否可用

```bash
openstack service create --name keystone --description "OpenStack Identity" identity
```

创建API路径

OpenStack每个服务可使用三种API路径变体： admin ， internal 和public 。默认情况， admin 类型的

API路径可修改用户（user）和租户（tenant），而internal 和public 类型的API路径不允许该操作。

```bash
openstack endpoint create --region RegionOne  identity public http://controller:5000/v3
openstack endpoint create --region RegionOne  identity internal http://controller:5000/v3
openstack endpoint create --region RegionOne identity admin http://controller:35357/v3
```

创建域（Domain）、计划（Project）、用户（User）、角色（Role）：

```bash
openstack domain create --description "Default Domain" default
openstack project create --domain default  --description "Admin Project" admin
openstack user create --domain default  --password-prompt admin
openstack role create admin
```

创建的任何角色都必须映射到OpenStack配置文件policy.json 指定的角色：

```bash
openstack role add --project admin --user admin admin
```

创建服务计划

```bash
openstack project create --domain default --description "Service Project" service
```

常规（非管理员）的任务应该使用一个普通的项目和用户。

```bash
openstack project create --domain default  --description "Demo Project" demo
openstack user create --domain default  --password-prompt demo
openstack role create user
```

将普通用户角色授予示例计划和示例用户：

```bash
openstack role add --project demo --user demo user
```

处于安全考虑，禁用临时身份认证令牌机制

修改文件vi /etc/keystone/keystone‐paste.ini ，从

[pipeline:public_api] 、[pipeline:admin_api] ， [pipeline:api_v3] 处移除admin_token_auth 配置信息。

取消环境变量OS_TOKEN 和OS_URL

```bash
unset OS_TOKEN OS_URL
```

为admin 用户申请一个身份认证令牌

```bash
openstack ‐‐os‐auth‐url http://controller:35357/v3 ‐‐os‐project‐domain‐name default ‐‐osuser‐domain‐name default ‐‐os‐project‐name admin ‐‐os‐username admin token issue

为demo 用户申请一个身份认证令牌
openstack --os-auth-url http://controller:5000/v3   --os-project-domain-name default --os-user-domain-name       default   --os-project-name demo --os-username demo  token issue
```

其他申请方法：

创建OpenStack客户端环境脚本方法

```bash
vim   admin-openrc
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=admin
export OS_AUTH_URL=http://controller:35357/v3
export OS_AUTH_TYPE=password
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
source   admin-openrc
openstack token issue

vim  demo-openrc
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=demo
export OS_AUTH_URL=http://controller:5000/v3
export OS_AUTH_TYPE=password
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
source   demo-openrc
openstack token issue
```

4.3 镜像服务配置（Image Service Glance）

用户可使用OpenStack镜像服务提供的REST API 查询、注册、恢复虚拟机镜像。

部署节点：Controller Node

```bash
mysql -uroot -p123456
CREATE DATABASE glance;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost'  IDENTIFIED BY 'glance';
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%'   IDENTIFIED BY 'glance';
flush privileges;
```

. admin-openrc

在OpenStack中创建一个glance用户

```bash
openstack user create --domain default --password-prompt glance
User Password: glance
Repeat User Password:glance
```

将admin 角色授予glance 用户和service 计划

```bash
openstack role add --project service --user glance admin
```

创建glance服务实体

```bash
openstack service create --name glance --description "OpenStack Image" p_w_picpath
```

创建镜像服务API路径

```bash
openstack endpoint create --region RegionOne   p_w_picpath public http://controller:9292
openstack endpoint create --region RegionOne   p_w_picpath internal http://controller:9292
openstack endpoint create --region RegionOne   p_w_picpath admin http://controller:9292
```

安装和配置Glance服务组件

```bash
yum install openstack-glance
vim /etc/glance/glance-api.conf
```

connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance

在[keystone_authtoken] 和[paste_deploy] 处，配置身份服务访问。

注：注释掉[keystone_authtoken] 处所有默认内容  M版默认是全注释掉的

[keystone_authtoken]
...
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = GLANCE_PASS

[paste_deploy]
...

flavor = keystone

在[glance_store]处配置本地文件系统存储和镜像文件存储位置。

stores = file,http

default_store = file

filesystem_store_datadir = /var/lib/glance/p_w_picpaths/

```bash
vim /etc/glance/glance-registry.conf
connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = GLANCE_PASS
[paste_deploy]
flavor = keystone
```

将配置信息写入glance数据库

```bash
 su -s /bin/sh -c "glance-manage  db_sync" glance
```

忽略所有有关’弃用’（deprecate）的输出

Option "verbose" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.

/usr/lib/python2.7/site-packages/oslo_db/sqlalchemy/enginefacade.py:1056: OsloDBDeprecationWarning: EngineFacade is deprecated; please use oslo_db.sqlalchemy.enginefacade

expire_on_commit=expire_on_commit, _conf=conf)

```bash
systemctl enable openstack-glance-api.service   openstack-glance-registry.service
systemctl start openstack-glance-api.service   openstack-glance-registry.service
wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
openstack p_w_picpath create "cirros"   --file cirros-0.3.4-x86_64-disk.img  --disk-format qcow2 --container-format bare   --public
[root@controller ~]# openstack p_w_picpath list
+--------------------------------------+--------+--------+
| ID                                   | Name   | Status |
+--------------------------------------+--------+--------+
| 9866bbe8-5efb-43e4-9c22-3984a63276c8 | cirros | active |
+--------------------------------------+--------+--------+
```
