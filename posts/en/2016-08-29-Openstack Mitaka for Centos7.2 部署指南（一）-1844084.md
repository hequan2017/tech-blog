---
title: "OpenStack Mitaka for CentOS 7.2 Deployment Guide (Part 1)"
date: "2016-08-29 21:58:02"
category: "openstack"
source: "https://blog.51cto.com/hequan/1844084"
lang: "en"
---
> **About this post**
>
> This post is the first part of rewriting the Ubuntu edition of the OpenStack Mitaka deployment guide into a CentOS 7.2 edition, based on the official documentation. It covers setting up the base environment: installing and configuring MariaDB, MongoDB (used by the Telemetry service), RabbitMQ, and Memcached; the complete deployment of the keystone Identity service (hosted under Apache mod_wsgi, Fernet tokens, domain/project/user/role creation, and openrc environment scripts); and installing the glance Image service and uploading the cirros test image.

> **Technical notes**
>
> Both Mitaka and CentOS 7 have reached end of life; for deployments today, refer to the official documentation of current releases or use solutions such as Kolla-Ansible. Several components covered here have changed considerably: glance-registry was removed after Newton; keystone's ADMIN_TOKEN temporary token mechanism and the 35357 admin port were deprecated long ago, and port 5000 has also been unified to `/v3`; the `--public` option of `openstack image create` has been replaced by `--visibility public`. The Zybuluo link referenced in this post is no longer available.

---

This post is mainly based on:

- [OpenStack Mitaka for Ubuntu 16.04 LTS Deployment Guide](https://www.zybuluo.com/ncepuwanghui/note/389373) (Zybuluo, link no longer available)
- [Official documentation](http://docs.openstack.org/mitaka/install-guide-rdo/)

Replace the Ubuntu above with CentOS; for other details, refer to the deployment guide above.

## 4.1 Configure OpenStack Basic Services

Install the RDO Mitaka repository and the OpenStack client:

```bash
yum install centos-release-openstack-mitaka
yum install python-openstackclient
```

Install MariaDB:

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
mysql_secure_installation   ## set the password
```

Install the NoSQL database (MongoDB) (Controller Node):

Note: only the Telemetry service uses it.

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

Install the message queue service RabbitMQ (Controller Node):

```bash
yum install rabbitmq-server
systemctl enable rabbitmq-server.service
systemctl start rabbitmq-server.service
rabbitmqctl add_user openstack openstack   ## password
Creating user "openstack" ...
rabbitmqctl set_permissions openstack ".*" ".*" ".*"   ## permissions
Setting permissions for user "openstack" in vhost "/" ...
```

Install Memcached (Controller Node):

The Identity service authentication mechanism requires Memcached to cache tokens.

```bash
yum install memcached python-memcached
systemctl enable memcached.service
systemctl start memcached.service
```

## 4.2 Identity Service Configuration (Keystone)

The Identity service adopts a RESTful design and provides a web service interface through the REST API.

Note: common web service styles include SOAP, WSDL, and REST.

Deployment node: Controller Node

Create the keystone database in MariaDB (MySQL):

```sql
mysql -uroot -p123456
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'keystone';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY 'keystone';
flush privileges;
quit;
```

`%` means all hosts can access this MySQL remotely. However, the official MySQL documentation points out that `%` does not include localhost, so grants must be made for both localhost and `%`.

Generate a temporary administration token (ADMIN_TOKEN) for use during the initial keystone configuration:

```bash
openssl rand -hex 10
2d3c132acf773c01838e
```

Install Keystone and Apache HTTP Server with mod_wsgi.

This post uses Apache HTTP Server with mod_wsgi to serve the Identity service on ports 5000 and 35357. By default the keystone service already listens on ports 5000 and 35357; to avoid a conflict, the keystone service must first be disabled:

```bash
yum install openstack-keystone httpd mod_wsgi
vim /etc/keystone/keystone.conf
```

```ini
admin_token = ADMIN_TOKEN
connection = mysql+pymysql://keystone:KEYSTONE_DBPASS@controller/keystone
provider = fernet    ## Fernet token provider
```

Write the configuration into the Identity service database keystone and initialize the Fernet keys:

```bash
su -s /bin/sh -c "keystone-manage db_sync" keystone
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
```

Modify the httpd configuration:

```bash
vim /etc/httpd/conf/httpd.conf
```

```ini
ServerName controller
```

`vim /etc/httpd/conf.d/wsgi-keystone.conf`:

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

Create the service entity and API endpoints. First set up the environment variables:

```bash
vim admin   ## set environment variables
export OS_TOKEN=2d3c132acf773c01838e
export OS_URL=http://controller:35357/v3
export OS_IDENTITY_API_VERSION=3
source admin
```

Create the service entity. The Identity service manages the OpenStack service catalog, which determines whether other services are available:

```bash
openstack service create --name keystone --description "OpenStack Identity" identity
```

Create the API endpoints. Each OpenStack service can use three endpoint variants: admin, internal, and public. By default, the admin endpoints can modify users and tenants, while the internal and public endpoints do not allow that operation:

```bash
openstack endpoint create --region RegionOne identity public http://controller:5000/v3
openstack endpoint create --region RegionOne identity internal http://controller:5000/v3
openstack endpoint create --region RegionOne identity admin http://controller:35357/v3
```

Create the domain, project, user, and role:

```bash
openstack domain create --description "Default Domain" default
openstack project create --domain default --description "Admin Project" admin
openstack user create --domain default --password-prompt admin
openstack role create admin
```

Any role that is created must be mapped to the role specified in the OpenStack configuration file policy.json:

```bash
openstack role add --project admin --user admin admin
```

Create the service project:

```bash
openstack project create --domain default --description "Service Project" service
```

Regular (non-admin) tasks should use an ordinary project and user:

```bash
openstack project create --domain default --description "Demo Project" demo
openstack user create --domain default --password-prompt demo
openstack role create user
```

Grant the user role to the demo project and the demo user:

```bash
openstack role add --project demo --user demo user
```

For security reasons, disable the temporary authentication token mechanism: edit the file `vi /etc/keystone/keystone-paste.ini` and remove the `admin_token_auth` entry from `[pipeline:public_api]`, `[pipeline:admin_api]`, and `[pipeline:api_v3]`.

Unset the OS_TOKEN and OS_URL environment variables:

```bash
unset OS_TOKEN OS_URL
```

Request an authentication token for the admin user:

```bash
openstack --os-auth-url http://controller:35357/v3 --os-project-domain-name default --os-user-domain-name default --os-project-name admin --os-username admin token issue
```

Request an authentication token for the demo user:

```bash
openstack --os-auth-url http://controller:5000/v3 --os-project-domain-name default --os-user-domain-name default --os-project-name demo --os-username demo token issue
```

Alternative method: create OpenStack client environment scripts.

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

## 4.3 Image Service Configuration (Glance)

Users can use the REST API provided by the OpenStack Image service to query, register, and retrieve virtual machine images.

Deployment node: Controller Node

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

Create a glance user in OpenStack:

```bash
openstack user create --domain default --password-prompt glance
User Password: glance
Repeat User Password: glance
```

Add the admin role to the glance user and the service project:

```bash
openstack role add --project service --user glance admin
```

Create the glance service entity:

```bash
openstack service create --name glance --description "OpenStack Image" image
```

Create the Image service API endpoints:

```bash
openstack endpoint create --region RegionOne image public http://controller:9292
openstack endpoint create --region RegionOne image internal http://controller:9292
openstack endpoint create --region RegionOne image admin http://controller:9292
```

Install and configure the Glance service components:

```bash
yum install openstack-glance
vim /etc/glance/glance-api.conf
```

```ini
connection = mysql+pymysql://glance:GLANCE_DBPASS@controller/glance
```

In [keystone_authtoken] and [paste_deploy], configure access to the Identity service.

Note: comment out all of the default content under [keystone_authtoken]; in the Mitaka (M) release it is all commented out by default.

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

In [glance_store], configure the local file system store and the location for storing image files:

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

Write the configuration into the glance database:

```bash
su -s /bin/sh -c "glance-manage db_sync" glance
```

Ignore all output regarding deprecation:

```text
Option "verbose" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
/usr/lib/python2.7/site-packages/oslo_db/sqlalchemy/enginefacade.py:1056: OsloDBDeprecationWarning: EngineFacade is deprecated; please use oslo_db.sqlalchemy.enginefacade
expire_on_commit=expire_on_commit, _conf=conf)
```

Start the services and upload the cirros test image:

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
