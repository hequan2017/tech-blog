---
title: "Openstack Mitaka for  Centos7.2 部署指南（三）"
date: "2016-09-04 14:20:27"
category: "openstack"
source: "https://blog.51cto.com/hequan/1846096"
---

4.7 块存储服务配置（Block Storage Service Cinder）

部署节点：Controller Node

mysql -u root -p123456

CREATE DATABASE cinder;

GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' \

IDENTIFIED BY 'cinder';

GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' \

IDENTIFIED BY 'cinder';

openstack user create --domain default --password-prompt cinder

openstack role add --project service --user cinder admin

openstack service create --name cinder   --description "OpenStack Block Storage" volume

openstack service create --name cinderv2   --description "OpenStack Block Storage" volumev2

openstack endpoint create --region RegionOne   volume public http://controller:8776/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne   volume internal http://controller:8776/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne   volume admin http://controller:8776/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne   volumev2 public http://controller:8776/v2/%\(tenant_id\)s

openstack endpoint create --region RegionOne   volumev2 internal http://controller:8776/v2/%\(tenant_id\)s

openstack endpoint create --region RegionOne   volumev2 admin http://controller:8776/v2/%\(tenant_id\)s

安装和配置Cinder服务组件

yum install openstack-cinder

修改配置文件sudo vi /etc/cinder/cinder.conf

connection = mysql+pymysql://cinder:cinder@controller/cinder

[oslo_messaging_rabbit]

rabbit_host = controller
rabbit_userid = openstack

rabbit_password = openstack

[DEFAULT]
...
auth_strategy = keystone

[keystone_authtoken]
...
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = cinder

password = cinder

[DEFAULT]
...
my_ip = 10.0.0.11

[oslo_concurrency]

lock_path = /var/lib/cinder/tmp

su -s /bin/sh -c "cinder-manage db sync" cinder

配置计算服务调用块存储服务

修改配置文件sudo vi /etc/nova/nova.conf ，添加如下信息：

[cinder]

os_region_name = RegionOne

systemctl restart openstack-nova-api.service

systemctl start openstack-cinder-api.service openstack-cinder-scheduler.service

systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service

部署节点：BlockStorage Node

[root@blockstorage ~]# yum install lvm2

systemctl enable lvm2-lvmetad.service

systemctl start lvm2-lvmetad.service

[root@blockstorage ~]# pvcreate /dev/sdb

Physical volume "/dev/sdb" successfully created

# vgcreate cinder-volumes /dev/sdb
Volume group "cinder-volumes" successfully created

配置只有OpenStack实例才可以访问块存储卷

修改配置文件sudo vi /etc/lvm/lvm.conf ，在devices 处添加一个过滤器，使OpenStack实例只允许访

问/dev/sdb 。

devices {
...
filter = [ "a/sdb/", "r/.*/"]

安装配置块存储服务组件

yum install openstack-cinder targetcli python-keystone

修改配置文件sudo vi /etc/cinder/cinder.conf

[database]

connection = mysql+pymysql://cinder:cinder@controller/cinder

[DEFAULT]

rpc_backend = rabbit

[oslo_messaging_rabbit]

rabbit_host = controller

rabbit_userid = openstack

rabbit_password = openstack

[DEFAULT]

auth_strategy = keystone

[keystone_authtoken]

auth_uri = http://controller:5000

auth_url = http://controller:35357

memcached_servers = controller:11211

auth_type = password

project_domain_name = default

user_domain_name = default

project_name = service

username = cinder

password = cinder

[DEFAULT]

my_ip = 10.0.0.41

[lvm]

volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver

volume_group = cinder-volumes

iscsi_protocol = iscsi

iscsi_helper = tgtadm

[DEFAULT]

enabled_backends = lvm

[DEFAULT]

glance_api_servers = http://controller:9292

[oslo_concurrency]

lock_path = /var/lib/cinder/tmp

systemctl start openstack-cinder-volume.service target.service

systemctl enable openstack-cinder-volume.service target.service

[root@controller ~]# cinder service-list

+------------------+------------------+------+---------+-------+----------------------------+-----------------+

|      Binary      |       Host       | Zone |  Status | State |         Updated_at         | Disabled Reason |

+------------------+------------------+------+---------+-------+----------------------------+-----------------+

| cinder-scheduler |    controller    | nova | enabled |   up  | 2016-09-03T14:19:51.000000 |        -        |

|  cinder-volume   | blockstorage@lvm | nova | enabled |   up  | 2016-09-03T14:19:27.000000 |        -        |

+------------------+------------------+------+---------+-------+----------------------------+-----------------+

---

4.9 对象存储服务配置（Object Storage Service Swift）

通过REST API 提供对象存储和检索服务。

部署节点：Controller Node

openstack user create --domain default --password-prompt swift

openstack role add --project service --user swift admin

openstack service create --name swift   --description "OpenStack Object Storage" object-store

openstack endpoint create --region RegionOne   object-store public http://controller:8080/v1/AUTH_%\(tenant_id\)s

openstack endpoint create --region RegionOne   object-store admin http://controller:8080/v1

yum install openstack-swift-proxy python-swiftclient   python-keystoneclient python-keystonemiddleware   memcached

从对象存储软件源仓库下载对象存储代理服务配置文件

curl -o /etc/swift/proxy-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/proxy-server.conf-sample?h=stable/mitaka

修改配置文件sudo vi /etc/swift/proxy‐server.conf 。

[DEFAULT]
...
bind_port = 8080
user = swift

swift_dir = /etc/swift

在[pipeline:main] 处移除tempurl 和tempauth 模块，并添加authtoken 和keystoneauth 模块

[pipeline:main]

pipeline = catch_errors gatekeeper healthcheck proxy-logging cache container_sync bulk ratelimit authtoken keystoneauth container-quotas account-quotas slo dlo versioned_writes proxy-logging proxy-server

[app:proxy-server]

use = egg:swift#proxy

account_autocreate = True

[filter:keystoneauth]

use = egg:swift#keystoneauth

operator_roles = admin,user

[filter:authtoken]
paste.filter_factory = keystonemiddleware.auth_token:filter_factory
...
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = swift
password = SWIFT_PASS
delay_auth_decision = True

[filter:cache]
use = egg:swift#memcache
...
memcache_servers = controller:11211

部署节点：ObjectStorage Node

注：每个对象存储节点都需执行以下步骤

yum install xfsprogs rsync -y

# mkfs.xfs /dev/sdb

# mkfs.xfs /dev/sdc

# mkdir -p /srv/node/sdb

# mkdir -p /srv/node/sdc

/dev/sdb /srv/node/sdb xfs noatime,nodiratime,nobarrier,logbufs=8 0 2

/dev/sdc /srv/node/sdc xfs noatime,nodiratime,nobarrier,logbufs=8 0 2

# mount /srv/node/sdb

# mount /srv/node/sdc

vim  /etc/rsyncd.conf

uid = swift

gid = swift

log file = /var/log/rsyncd.log

pid file = /var/run/rsyncd.pid

address = MANAGEMENT_INTERFACE_IP_ADDRESS

[account]

max connections = 2

path = /srv/node/

read only = False

lock file = /var/lock/account.lock

[container]

max connections = 2

path = /srv/node/

read only = False

lock file = /var/lock/container.lock

[object]

max connections = 2

path = /srv/node/

read only = False

lock file = /var/lock/object.lock

# systemctl enable rsyncd.service

# systemctl start rsyncd.service

yum install openstack-swift-account openstack-swift-container  openstack-swift-object

curl -o /etc/swift/account-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/account-server.conf-sample?h=stable/mitaka

curl -o /etc/swift/container-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/container-server.conf-sample?h=stable/mitaka

curl -o /etc/swift/object-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/object-server.conf-sample?h=stable/mitaka

修改配置文件sudo vi /etc/swift/account‐server.conf 。

在[DEFAULT] 处配置绑定IP地址、绑定端口、用户、目录和挂载点：

注：将下面MANAGEMENT_INTERFACE_IP_ADDRESS 替换为对象存储节点Management Network 网络接口地

址10.0.0.51 或10.0.0.52

[DEFAULT]

bind_ip = MANAGEMENT_INTERFACE_IP_ADDRESS

bind_port = 6002

user = swift

swift_dir = /etc/swift

devices = /srv/node

mount_check = True

[pipeline:main]

pipeline = healthcheck recon account‐server

[filter:recon]

use = egg:swift#recon

recon_cache_path = /var/cache/swift

修改配置文件sudo vi /etc/swift/container‐server.conf

在[DEFAULT] 处配置绑定IP地址、绑定端口、用户、目录和挂载点：

注：将下面MANAGEMENT_INTERFACE_IP_ADDRESS 替换为对象存储节点Management Network 网络接口地

址10.0.0.51 或10.0.0.52

[DEFAULT]

bind_ip = MANAGEMENT_INTERFACE_IP_ADDRESS

bind_port = 6001

user = swift

swift_dir = /etc/swift

devices = /srv/node

mount_check = True

[pipeline:main]

pipeline = healthcheck recon container‐server

[filter:recon]

use = egg:swift#recon

recon_cache_path = /var/cache/swift

修改配置文件sudo vi /etc/swift/object‐server.conf

在[DEFAULT] 处配置绑定IP地址、绑定端口、用户、目录和挂载点：

注：将下面MANAGEMENT_INTERFACE_IP_ADDRESS 替换为对象存储节点Management Network 网络接口地

址10.0.0.51 或10.0.0.52

[DEFAULT]

bind_ip = MANAGEMENT_INTERFACE_IP_ADDRESS

bind_port = 6000

user = swift

swift_dir = /etc/swift

devices = /srv/node

mount_check = True

[pipeline:main]

pipeline = healthcheck recon object‐server

[filter:recon]

use = egg:swift#recon

recon_cache_path = /var/cache/swift

recon_lock_path = /var/lock

chown -R swift:swift /srv/node

mkdir -p /var/cache/swift

chown -R root:swift /var/cache/swift

chmod -R 775 /var/cache/swift

部署节点：Controller Node

创建和分发初始环

cd /etc/swift

创建基础的account.builder 文件：

[root@controller swift]# swift-ring-builder account.builder create 10 3 1

将每个对象存储节点设备添加到账户环：

swift-ring-builder account.builder  add --region 1 --zone 1 --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS --port 6002  --device DEVICE_NAME --weight DEVICE_WEIGHT

注：将STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS 替换为对象存储节点Management Network 网络接

口地址，将DEVICE_NAME 替换为对应的对象存储节点上的存储设备名称，将DEVICE_WEIGHT 替换为实际权重

值。

注：重复以上命令，将每个存储节点上的每个存储设备添加到账户环。

例如，本文采用如下命令将每个存储节点上的每个存储设备添加到账户环：

swift-ring-builder  account.builder add --region 1 --zone 1 --ip 10.0.0.51  --port 6002 --device sdb --weight 100

swift-ring-builder  account.builder add --region 1 --zone 1 --ip 10.0.0.51  --port 6002 --device sdc --weight 100

swift-ring-builder  account.builder add --region 1 --zone 2 --ip 10.0.0.52  --port 6002 --device sdb --weight 100

swift-ring-builder  account.builder add --region 1 --zone 2 --ip 10.0.0.52  --port 6002 --device sdc --weight 100

验证

swift-ring-builder account.builder

平衡账户环：

[root@controller swift]# swift-ring-builder account.builder rebalance

Reassigned 3072 (300.00%) partitions. Balance is now 0.00.  Dispersion is now 0.00

swift-ring-builder container.builder create 10 3 1

swift-ring-builder  container.builder add --region 1 --zone 1 --ip 10.0.0.51  --port 6001 --device sdb --weight 100

swift-ring-builder  container.builder add --region 1 --zone 1 --ip 10.0.0.51  --port 6001 --device sdc --weight 100

swift-ring-builder  container.builder add --region 1 --zone 2 --ip 10.0.0.52  --port 6001 --device sdb --weight 100

swift-ring-builder  container.builder add --region 1 --zone 2 --ip 10.0.0.52  --port 6001 --device sdc --weight 100

swift-ring-builder container.builder

swift-ring-builder container.builder rebalance

swift-ring-builder object.builder create 10 3 1

swift-ring-builder  object.builder add --region 1 --zone 1 --ip 10.0.0.51  --port 6000 --device sdb --weight 100

swift-ring-builder  object.builder add --region 1 --zone 1 --ip 10.0.0.51  --port 6000 --device sdc --weight 100

swift-ring-builder  object.builder add --region 1 --zone 2 --ip 10.0.0.52  --port 6000 --device sdb --weight 100

swift-ring-builder  object.builder add --region 1 --zone 2 --ip 10.0.0.52  --port 6000 --device sdc --weight 100

swift-ring-builder object.builder

swift-ring-builder object.builder rebalance

分发环配置文件

将环配置文件account.ring.gz 、container.ring.gz 和object.ring.gz 拷贝到每个对象存储节点以及代理

服务节点的/etc/swift 目录。在每个存储节点或代理服务节点执行以下命令：

scp root@controller:/etc/swift/*.ring.gz /etc/swift

本文将swift‐proxy 部署到controller节点，因此无需再讲环配置文件拷贝到代理服务节点的/etc/swift

目录。若对象存储代理服务swift‐proxy 部署在其他节点，则需将环配置文件拷贝到该代理服务节

点/etc/swift 目录下。

添加、分发swift 配置文件

① 从对象存储软件源仓库下载配置文件/etc/swift/swift.conf

curl -o /etc/swift/swift.conf  https://git.openstack.org/cgit/openstack/swift/plain/etc/swift.conf-sample?h=stable/mitaka

② 修改配置文件sudo vi /etc/swift/swift.conf

在[swift‐hash] 处哈希路径前缀和后缀

注：将HASH_PATH_PREFIX 和HASH_PATH_SUFFIX 替换为前面设计的唯一值。

[swift-hash]
...
swift_hash_path_suffix = HASH_PATH_SUFFIX

swift_hash_path_prefix = HASH_PATH_PREFIX

[storage‐policy:0]

name = Policy‐0

default = yes

③ 分发swift 配置文件

将/etc/swift/swift.conf 拷贝到每个对象存储节点以及代理服务节点的/etc/swift 目录。在每个存储节点

或代理服务节点执行以下命令：

scp root@controller:/etc/swift/swift.conf /etc/swift

④ 在所有存储节点和代理服务节点上设置swift配置目录所有权

chown  -R root:swift /etc/swift

在Controller节点和其他Swift代理服务节点上执行

systemctl enable openstack-swift-proxy.service memcached.service

systemctl start openstack-swift-proxy.service memcached.service

在所有对象存储节点上执行

systemctl enable openstack-swift-account.service openstack-swift-account-auditor.service openstack-swift-account-reaper.service openstack-swift-account-replicator.service

systemctl start openstack-swift-account.service openstack-swift-account-auditor.service openstack-swift-account-reaper.service openstack-swift-account-replicator.service

systemctl enable openstack-swift-container.service openstack-swift-container-auditor.service openstack-swift-container-replicator.service  openstack-swift-container-updater.service

systemctl start openstack-swift-container.service openstack-swift-container-auditor.service openstack-swift-container-replicator.service  openstack-swift-container-updater.service

systemctl enable openstack-swift-object.service openstack-swift-object-auditor.service openstack-swift-object-replicator.service openstack-swift-object-updater.service

systemctl start openstack-swift-object.service openstack-swift-object-auditor.service openstack-swift-object-replicator.service openstack-swift-object-updater.service

swift stat

---

实验到次，，后期改正此博客。。。
