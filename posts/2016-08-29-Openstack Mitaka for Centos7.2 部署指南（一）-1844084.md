---
title: "Openstack Mitaka for  Centos7.2 部署指南（一）"
date: "2016-08-29 21:58:02"
category: "openstack"
source: "https://blog.51cto.com/hequan/1844084"
---
> **内容介绍**
>
> 本篇是参照官方文档把 Ubuntu 版 OpenStack Mitaka 部署指南改写为 CentOS 7.2 版本的第一部分，覆盖基础环境搭建：MariaDB、MongoDB（计量服务用）、RabbitMQ、Memcached 的安装配置，keystone 身份服务的完整部署（Apache mod_wsgi 托管、Fernet 令牌、域/项目/用户/角色创建、openrc 环境脚本），以及 glance 镜像服务的安装与 cirros 测试镜像上传。

> **技术备注**
>
> Mitaka 与 CentOS 7 均已 EOL，如今部署请参考现行版本的官方文档或使用 Kolla-Ansible 等方案。文中若干组件已发生大变化：glance-registry 在 Newton 之后被移除；keystone 的 ADMIN_TOKEN 临时令牌机制与 35357 管理端口早已废弃，5000 端口也已统一为 `/v3`；`openstack image create` 的 `--public` 参数已改为 `--visibility public`。文中参考的作业部落链接已失效。

---

本文主要参考：

- [OpenStack Mitaka for Ubuntu 16.04 LTS 部署指南](https://www.zybuluo.com/ncepuwanghui/note/389373)（作业部落，链接已失效）
- [官方文档](http://docs.openstack.org/mitaka/install-guide-rdo/)

把上面的 Ubuntu 换成 CentOS，其他详情请看上面的部署指南。

## 4.1 配置 OpenStack 基础服务

安装 RDO Mitaka 源与 OpenStack client：

```bash
yum install centos-release-openstack-mitaka
yum install python-openstackclient
```

安装 MariaDB：

```bash
yum install mariadb mariadb-server python2-PyMySQL
[root@controller ~]# vim /etc/my.cnf.d/openstack.cnf
```

```ini
[mysqld]
bind-address = 10.0.0.11
default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8
```

```bash
systemctl enable mariadb.service
systemctl start mariadb.service
mysql_secure_installation   ## 设置密码
```

安装 NoSQL 数据库（MongoDB）（Controller Node）：

注：只有计量服务（Telemetry Service）用到。

```bash
yum install mongodb-server mongodb
[root@controller ~]# vim /etc/mongod.conf
```

```ini
bind_ip = 10.0.0.11
smallfiles = true
```

```bash
systemctl enable mongod.service
systemctl start mongod.service
```

安装消息队列服务 RabbitMQ（Controller Node）：

```bash
yum install rabbitmq-server
systemctl enable rabbitmq-server.service
systemctl start rabbitmq-server.service
rabbitmqctl add_user openstack openstack   ## 密码
Creating user "openstack" ...
rabbitmqctl set_permissions openstack ".*" ".*" ".*"   ## 权限
Setting permissions for user "openstack" in vhost "/" ...
```

安装 Memcached（Controller Node）：

身份服务（Identity Service）认证机制需要使用 Memcached 缓存令牌（Token）。

```bash
yum install memcached python-memcached
systemctl enable memcached.service
systemctl start memcached.service
```

## 4.2 身份服务配置（Identity Service Keystone）

Identity 服务采用 RESTful 设计，使用 REST API 提供 Web 服务接口。

注：常见的 Web Service 方式有 SOAP、WSDL、REST。

部署节点：Controller Node

在 MariaDB（MySQL）中创建 keystone 数据库：

```sql
mysql -uroot -p123456
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'keystone';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'keystone';
flush privileges;
quit;
```

`%` 代表所有的 host 都能远程访问该 MySQL。但 MySQL 官方文档指出，`%` 并不包括 localhost，因此需要对 localhost 和 % 都进行授权。

生成临时管理身份认证令牌（ADMIN_TOKEN），作为 keystone 初始配置时使用：

```bash
openssl rand -hex 10
2d3c132acf773c01838e
```

安装 Keystone 和 Apache HTTP Server with mod_wsgi。

本文采用 Apache HTTP server with mod_wsgi 监听端口 5000 和 35357 提供身份服务。默认 keystone 服务已经监听端口 5000 和 35357，为避免冲突，需首先关闭 keystone 服务：

```bash
yum install openstack-keystone httpd mod_wsgi
vim /etc/keystone/keystone.conf
```

```ini
admin_token = ADMIN_TOKEN
connection = mysql+pymysql://keystone:KEYSTONE_DBPASS@controller/keystone
provider = fernet    ## Fernet令牌提供者
```

将配置信息写入到身份服务数据库 keystone，并初始化 Fernet keys：

```bash
su -s /bin/sh -c "keystone-manage db_sync" keystone
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
```

修改 httpd 配置：

```bash
vim /etc/httpd/conf/httpd.conf
```

```ini
ServerName controller
```

`vim /etc/httpd/conf.d/wsgi-keystone.conf`：

```apache
Listen 5000
Listen 35357

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
    </Directory>
</VirtualHost>

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
    </Directory>
</VirtualHost>
```

```bash
systemctl enable httpd.service
systemctl start httpd.service
```

创建服务实体（Service Entity）和 API 路径（API Endpoints），先设置环境变量：

```bash
vim admin   ## 设置环境变量
export OS_TOKEN=2d3c132acf773c01838e
export OS_URL=http://controller:35357/v3
export OS_IDENTITY_API_VERSION=3
source admin
```

创建服务实体。身份服务管理着一个 OpenStack 的服务目录，通过服务目录确定其他服务是否可用：

```bash
openstack service create --name keystone --description "OpenStack Identity" identity
```

创建 API 路径。OpenStack 每个服务可使用三种 API 路径变体：admin、internal 和 public。默认情况下，admin 类型的 API 路径可修改用户（user）和租户（tenant），而 internal 和 public 类型的 API 路径不允许该操作：

```bash
openstack endpoint create --region RegionOne identity public http://controller:5000/v3
openstack endpoint create --region RegionOne identity internal http://controller:5000/v3
openstack endpoint create --region RegionOne identity admin http://controller:35357/v3
```

创建域（Domain）、项目（Project）、用户（User）、角色（Role）：

```bash
openstack domain create --description "Default Domain" default
openstack project create --domain default --description "Admin Project" admin
openstack user create --domain default --password-prompt admin
openstack role create admin
```

创建的任何角色都必须映射到 OpenStack 配置文件 policy.json 指定的角色：

```bash
openstack role add --project admin --user admin admin
```

创建服务项目：

```bash
openstack project create --domain default --description "Service Project" service
```

常规（非管理员）的任务应该使用一个普通的项目和用户：

```bash
openstack project create --domain default --description "Demo Project" demo
openstack user create --domain default --password-prompt demo
openstack role create user
```

将普通用户角色授予示例项目和示例用户：

```bash
openstack role add --project demo --user demo user
```

出于安全考虑，禁用临时身份认证令牌机制：修改文件 `vi /etc/keystone/keystone-paste.ini`，从 `[pipeline:public_api]`、`[pipeline:admin_api]`、`[pipeline:api_v3]` 处移除 `admin_token_auth` 配置信息。

取消环境变量 OS_TOKEN 和 OS_URL：

```bash
unset OS_TOKEN OS_URL
```

为 admin 用户申请一个身份认证令牌：

```bash
openstack --os-auth-url http://controller:35357/v3 --os-project-domain-name default --os-user-domain-name default --os-project-name admin --os-username admin token issue
```

为 demo 用户申请一个身份认证令牌：

```bash
openstack --os-auth-url http://controller:5000/v3 --os-project-domain-name default --os-user-domain-name default --os-project-name demo --os-username demo token issue
```

其他申请方法：创建 OpenStack 客户端环境脚本。

```bash
vim admin-openrc
```

```bash
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=admin
export OS_AUTH_URL=http://controller:35357/v3
export OS_AUTH_TYPE=password
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
```

```bash
source admin-openrc
openstack token issue
```

```bash
vim demo-openrc
```

```bash
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=demo
export OS_AUTH_URL=http://controller:5000/v3
export OS_AUTH_TYPE=password
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
```

```bash
source demo-openrc
openstack token issue
```

## 4.3 镜像服务配置（Image Service Glance）

用户可使用 OpenStack 镜像服务提供的 REST API 查询、注册、恢复虚拟机镜像。

部署节点：Controller Node

```sql
mysql -uroot -p123456
CREATE DATABASE glance;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY 'glance';
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY 'glance';
flush privileges;
```

```bash
. admin-openrc
```

在 OpenStack 中创建一个 glance 用户：

```bash
openstack user create --domain default --password-prompt glance
User Password: glance
Repeat User Password: glance
```

将 admin 角色授予 glance 用户和 service 项目：

```bash
openstack role add --project service --user glance admin
```

创建 glance 服务实体：

```bash
openstack service create --name glance --description "OpenStack Image" image
```

创建镜像服务 API 路径：

```bash
openstack endpoint create --region RegionOne image public http://controller:9292
openstack endpoint create --region RegionOne image internal http://controller:9292
openstack endpoint create --region RegionOne image admin http://controller:9292
```

安装和配置 Glance 服务组件：

```bash
yum install openstack-glance
vim /etc/glance/glance-api.conf
```

```ini
connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance
```

在 [keystone_authtoken] 和 [paste_deploy] 处，配置身份服务访问。

注：注释掉 [keystone_authtoken] 处所有默认内容，M 版默认是全注释掉的。

```ini
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
```

在 [glance_store] 处配置本地文件系统存储和镜像文件存储位置：

```ini
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
```

```bash
vim /etc/glance/glance-registry.conf
```

```ini
connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance
[keystone_authtoken]
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
flavor = keystone
```

将配置信息写入 glance 数据库：

```bash
su -s /bin/sh -c "glance-manage db_sync" glance
```

忽略所有有关"弃用"（deprecate）的输出：

```text
Option "verbose" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
/usr/lib/python2.7/site-packages/oslo_db/sqlalchemy/enginefacade.py:1056: OsloDBDeprecationWarning: EngineFacade is deprecated; please use oslo_db.sqlalchemy.enginefacade
expire_on_commit=expire_on_commit, _conf=conf)
```

启动服务并上传 cirros 测试镜像：

```bash
systemctl enable openstack-glance-api.service openstack-glance-registry.service
systemctl start openstack-glance-api.service openstack-glance-registry.service
wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
openstack image create "cirros" --file cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --container-format bare --public
[root@controller ~]# openstack image list
+--------------------------------------+--------+--------+
| ID                                   | Name   | Status |
+--------------------------------------+--------+--------+
| 9866bbe8-5efb-43e4-9c22-3984a63276c8 | cirros | active |
+--------------------------------------+--------+--------+
```
