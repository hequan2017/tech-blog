---
title: "Openstack Mitaka for  Centos7.2 部署指南（三）"
date: "2016-09-04 14:20:27"
category: "openstack"
source: "https://blog.51cto.com/hequan/1846096"
---
> **内容介绍**
>
> 本篇是 CentOS 7.2 部署 OpenStack Mitaka 的第三部分：4.7 块存储服务 Cinder——
> 控制节点建库、注册 volume/volumev2 双服务与 endpoint、修改 cinder.conf 并让
> nova 调用块存储；存储节点安装 LVM、pvcreate/vgcreate 建立 cinder-volumes 卷组、
> 配置 lvm.conf 过滤器，以 LVM+iSCSI（tgtadm）作后端启动 cinder-volume 并验证。
> 4.9 对象存储服务 Swift——控制节点配置 proxy-server（pipeline 换用
> authtoken/keystoneauth）；存储节点用 XFS 格式化磁盘挂到 /srv/node、配置 rsync
> 与 account/container/object 三个 server；控制节点用 swift-ring-builder 创建并
> rebalance 三个环，分发 ring.gz 与 swift.conf 后启动全套服务，swift stat 验证。
> 文末注明实验到此、博客后期再修订。

> **技术备注**
>
> OpenStack Mitaka 与 CentOS 7 均已停止维护。Cinder 的 v1 `volume` API 与
> `cinder service-list` 等 CLI 已废弃，现用 volumev3 与 `openstack volume service
> list`；文中 `git.openstack.org/cgit` 配置文件下载源已随 OpenStack 基础设施
> 退役而失效，可改用 opendev.org 对应路径获取同版本 sample。Swift 的
> swift-ring-builder 建环流程至今仍是标准做法；生产环境对象存储如今更常用
> Ceph RGW（S3 兼容）替代独立 Swift 集群。

---

## 1. 块存储服务配置（原文 4.7，Block Storage Service — Cinder）

### 控制节点（Controller Node）

创建数据库：

```bash
mysql -u root -p123456
```

```sql
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'cinder';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'cinder';
```

注册用户、服务与 API 路径（v1/v2 两套）：

```bash
openstack user create --domain default --password-prompt cinder
openstack role add --project service --user cinder admin
openstack service create --name cinder --description "OpenStack Block Storage" volume
openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2
openstack endpoint create --region RegionOne volume public http://controller:8776/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne volume internal http://controller:8776/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne volume admin http://controller:8776/v1/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev2 public http://controller:8776/v2/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev2 internal http://controller:8776/v2/%\(tenant_id\)s
openstack endpoint create --region RegionOne volumev2 admin http://controller:8776/v2/%\(tenant_id\)s
```

安装和配置 Cinder 服务组件：

```bash
yum install openstack-cinder
```

修改配置文件 `/etc/cinder/cinder.conf`（数据库连接原文漏了 `[database]` 段名，
此处补上）：

```ini
[database]
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
```

将配置信息写入数据库：

```bash
su -s /bin/sh -c "cinder-manage db sync" cinder
```

配置计算服务调用块存储服务。修改配置文件 `/etc/nova/nova.conf`，添加如下信息：

```ini
[cinder]
os_region_name = RegionOne
```

```bash
systemctl restart openstack-nova-api.service
systemctl start openstack-cinder-api.service openstack-cinder-scheduler.service
systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service
```

### 存储节点（BlockStorage Node）

安装 LVM 并创建物理卷/卷组：

```bash
[root@blockstorage ~]# yum install lvm2
systemctl enable lvm2-lvmetad.service
systemctl start lvm2-lvmetad.service
[root@blockstorage ~]# pvcreate /dev/sdb
# Physical volume "/dev/sdb" successfully created
[root@blockstorage ~]# vgcreate cinder-volumes /dev/sdb
# Volume group "cinder-volumes" successfully created
```

配置只有 OpenStack 实例才可以访问块存储卷。修改配置文件 `/etc/lvm/lvm.conf`，
在 devices 处添加一个过滤器，使 OpenStack 实例只允许访问 `/dev/sdb`：

```ini
devices {
...
filter = [ "a/sdb/", "r/.*/" ]
```

安装配置块存储服务组件：

```bash
yum install openstack-cinder targetcli python-keystone
```

修改配置文件 `/etc/cinder/cinder.conf`：

```ini
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
```

```bash
systemctl start openstack-cinder-volume.service target.service
systemctl enable openstack-cinder-volume.service target.service
```

### 验证

```text
[root@controller ~]# cinder service-list
+------------------+------------------+------+---------+-------+----------------------------+-----------------+
|      Binary      |       Host       | Zone |  Status | State |         Updated_at         | Disabled Reason |
+------------------+------------------+------+---------+-------+----------------------------+-----------------+
| cinder-scheduler |    controller    | nova | enabled |   up  | 2016-09-03T14:19:51.000000 |        -        |
|  cinder-volume   | blockstorage@lvm | nova | enabled |   up  | 2016-09-03T14:19:27.000000 |        -        |
+------------------+------------------+------+---------+-------+----------------------------+-----------------+
```

## 2. 对象存储服务配置（原文 4.9，Object Storage Service — Swift）

通过 REST API 提供对象存储和检索服务。

### 控制节点：代理服务（Proxy Server）

部署节点：Controller Node。

```bash
openstack user create --domain default --password-prompt swift
openstack role add --project service --user swift admin
openstack service create --name swift --description "OpenStack Object Storage" object-store
openstack endpoint create --region RegionOne object-store public http://controller:8080/v1/AUTH_%\(tenant_id\)s
openstack endpoint create --region RegionOne object-store admin http://controller:8080/v1
```

```bash
yum install openstack-swift-proxy python-swiftclient python-keystoneclient \
    python-keystonemiddleware memcached
```

从对象存储软件源仓库下载对象存储代理服务配置文件（原 git.openstack.org
链接已失效）：

```bash
curl -o /etc/swift/proxy-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/proxy-server.conf-sample?h=stable/mitaka
```

修改配置文件 `/etc/swift/proxy-server.conf`：

```ini
[DEFAULT]
...
bind_port = 8080
user = swift
swift_dir = /etc/swift
```

在 `[pipeline:main]` 处移除 tempurl 和 tempauth 模块，并添加 authtoken 和
keystoneauth 模块：

```ini
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
```

### 对象存储节点（ObjectStorage Node）

注：每个对象存储节点都需执行以下步骤。

格式化并挂载存储设备：

```bash
yum install xfsprogs rsync -y
mkfs.xfs /dev/sdb
mkfs.xfs /dev/sdc
mkdir -p /srv/node/sdb
mkdir -p /srv/node/sdc
```

`/etc/fstab` 追加：

```text
/dev/sdb /srv/node/sdb xfs noatime,nodiratime,nobarrier,logbufs=8 0 2
/dev/sdc /srv/node/sdc xfs noatime,nodiratime,nobarrier,logbufs=8 0 2
```

```bash
mount /srv/node/sdb
mount /srv/node/sdc
```

编辑 `/etc/rsyncd.conf`：

```ini
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
```

```bash
systemctl enable rsyncd.service
systemctl start rsyncd.service
```

安装并下载 account/container/object 三个 server 的配置模板：

```bash
yum install openstack-swift-account openstack-swift-container openstack-swift-object

curl -o /etc/swift/account-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/account-server.conf-sample?h=stable/mitaka
curl -o /etc/swift/container-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/container-server.conf-sample?h=stable/mitaka
curl -o /etc/swift/object-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/object-server.conf-sample?h=stable/mitaka
```

修改配置文件 `/etc/swift/account-server.conf`。在 `[DEFAULT]` 处配置绑定 IP
地址、绑定端口、用户、目录和挂载点。
注：将下面 MANAGEMENT_INTERFACE_IP_ADDRESS 替换为对象存储节点 Management
Network 网络接口地址 10.0.0.51 或 10.0.0.52。

```ini
[DEFAULT]
bind_ip = MANAGEMENT_INTERFACE_IP_ADDRESS
bind_port = 6002
user = swift
swift_dir = /etc/swift
devices = /srv/node
mount_check = True

[pipeline:main]
pipeline = healthcheck recon account-server

[filter:recon]
use = egg:swift#recon
recon_cache_path = /var/cache/swift
```

修改配置文件 `/etc/swift/container-server.conf`，同样替换管理网 IP：

```ini
[DEFAULT]
bind_ip = MANAGEMENT_INTERFACE_IP_ADDRESS
bind_port = 6001
user = swift
swift_dir = /etc/swift
devices = /srv/node
mount_check = True

[pipeline:main]
pipeline = healthcheck recon container-server

[filter:recon]
use = egg:swift#recon
recon_cache_path = /var/cache/swift
```

修改配置文件 `/etc/swift/object-server.conf`，同样替换管理网 IP：

```ini
[DEFAULT]
bind_ip = MANAGEMENT_INTERFACE_IP_ADDRESS
bind_port = 6000
user = swift
swift_dir = /etc/swift
devices = /srv/node
mount_check = True

[pipeline:main]
pipeline = healthcheck recon object-server

[filter:recon]
use = egg:swift#recon
recon_cache_path = /var/cache/swift
recon_lock_path = /var/lock
```

设置目录属主与权限：

```bash
chown -R swift:swift /srv/node
mkdir -p /var/cache/swift
chown -R root:swift /var/cache/swift
chmod -R 775 /var/cache/swift
```

### 创建和分发初始环（Controller Node）

部署节点：Controller Node。

```bash
cd /etc/swift
```

创建基础的 account.builder 文件：

```bash
[root@controller swift]# swift-ring-builder account.builder create 10 3 1
```

将每个对象存储节点设备添加到账户环：

```bash
swift-ring-builder account.builder add --region 1 --zone 1 \
  --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS --port 6002 \
  --device DEVICE_NAME --weight DEVICE_WEIGHT
```

注：将 STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS 替换为对象存储节点
Management Network 网络接口地址，将 DEVICE_NAME 替换为对应的对象存储节点上的
存储设备名称，将 DEVICE_WEIGHT 替换为实际权重值。重复以上命令，将每个存储节点
上的每个存储设备添加到账户环。

例如，本文采用如下命令将每个存储节点上的每个存储设备添加到账户环：

```bash
swift-ring-builder account.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6002 --device sdb --weight 100
swift-ring-builder account.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6002 --device sdc --weight 100
swift-ring-builder account.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6002 --device sdb --weight 100
swift-ring-builder account.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6002 --device sdc --weight 100
```

验证：

```bash
swift-ring-builder account.builder
```

平衡账户环：

```bash
[root@controller swift]# swift-ring-builder account.builder rebalance
# Reassigned 3072 (300.00%) partitions. Balance is now 0.00.  Dispersion is now 0.00
```

container 环（端口 6001）与 object 环（端口 6000）同理：

```bash
swift-ring-builder container.builder create 10 3 1
swift-ring-builder container.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6001 --device sdb --weight 100
swift-ring-builder container.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6001 --device sdc --weight 100
swift-ring-builder container.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6001 --device sdb --weight 100
swift-ring-builder container.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6001 --device sdc --weight 100
swift-ring-builder container.builder
swift-ring-builder container.builder rebalance

swift-ring-builder object.builder create 10 3 1
swift-ring-builder object.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6000 --device sdb --weight 100
swift-ring-builder object.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6000 --device sdc --weight 100
swift-ring-builder object.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6000 --device sdb --weight 100
swift-ring-builder object.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6000 --device sdc --weight 100
swift-ring-builder object.builder
swift-ring-builder object.builder rebalance
```

分发环配置文件。将环配置文件 account.ring.gz、container.ring.gz 和
object.ring.gz 拷贝到每个对象存储节点以及代理服务节点的 `/etc/swift` 目录。
在每个存储节点或代理服务节点执行以下命令：

```bash
scp root@controller:/etc/swift/*.ring.gz /etc/swift
```

本文将 swift-proxy 部署到 controller 节点，因此无需再将环配置文件拷贝到代理
服务节点的 `/etc/swift` 目录（原文「再讲」为笔误）。若对象存储代理服务
swift-proxy 部署在其他节点，则需将环配置文件拷贝到该代理服务节点 `/etc/swift`
目录下。

### 添加、分发 swift 配置文件

① 从对象存储软件源仓库下载配置文件 `/etc/swift/swift.conf`：

```bash
curl -o /etc/swift/swift.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/swift.conf-sample?h=stable/mitaka
```

② 修改配置文件 `/etc/swift/swift.conf`，在 `[swift-hash]` 处配置哈希路径前缀
和后缀。注：将 HASH_PATH_PREFIX 和 HASH_PATH_SUFFIX 替换为前面设计的唯一值。

```ini
[swift-hash]
...
swift_hash_path_suffix = HASH_PATH_SUFFIX
swift_hash_path_prefix = HASH_PATH_PREFIX

[storage-policy:0]
name = Policy-0
default = yes
```

③ 分发 swift 配置文件。将 `/etc/swift/swift.conf` 拷贝到每个对象存储节点以及
代理服务节点的 `/etc/swift` 目录。在每个存储节点或代理服务节点执行以下命令：

```bash
scp root@controller:/etc/swift/swift.conf /etc/swift
```

④ 在所有存储节点和代理服务节点上设置 swift 配置目录所有权：

```bash
chown -R root:swift /etc/swift
```

### 启动服务与验证

在 Controller 节点和其他 Swift 代理服务节点上执行：

```bash
systemctl enable openstack-swift-proxy.service memcached.service
systemctl start openstack-swift-proxy.service memcached.service
```

在所有对象存储节点上执行：

```bash
systemctl enable openstack-swift-account.service openstack-swift-account-auditor.service \
    openstack-swift-account-reaper.service openstack-swift-account-replicator.service
systemctl start openstack-swift-account.service openstack-swift-account-auditor.service \
    openstack-swift-account-reaper.service openstack-swift-account-replicator.service

systemctl enable openstack-swift-container.service openstack-swift-container-auditor.service \
    openstack-swift-container-replicator.service openstack-swift-container-updater.service
systemctl start openstack-swift-container.service openstack-swift-container-auditor.service \
    openstack-swift-container-replicator.service openstack-swift-container-updater.service

systemctl enable openstack-swift-object.service openstack-swift-object-auditor.service \
    openstack-swift-object-replicator.service openstack-swift-object-updater.service
systemctl start openstack-swift-object.service openstack-swift-object-auditor.service \
    openstack-swift-object-replicator.service openstack-swift-object-updater.service
```

验证：

```bash
swift stat
```

---

> 原文结语：实验到此，后期再修订此博客（原文「实验到次」为笔误）。
