---
title: "OpenStack Mitaka Deployment Guide for CentOS 7.2 (Part 3)"
date: "2016-09-04 14:20:27"
category: "openstack"
source: "https://blog.51cto.com/hequan/1846096"
lang: "en"
---
> **About this post**
>
> This is part three of deploying OpenStack Mitaka on CentOS 7.2: Section 4.7, the Cinder block
> storage service — creating the database on the controller node, registering both the
> volume/volumev2 services and their endpoints, editing cinder.conf, and pointing Nova at the
> block storage service; on the storage node, installing LVM, creating the cinder-volumes volume
> group with pvcreate/vgcreate, configuring the lvm.conf filter, and starting cinder-volume with
> LVM+iSCSI (tgtadm) as the backend, then verifying. Section 4.9, the Swift object storage
> service — configuring the proxy-server on the controller node (switching the pipeline to
> authtoken/keystoneauth); on the storage nodes, formatting disks as XFS and mounting them under
> /srv/node, and configuring rsync plus the account/container/object servers; on the controller
> node, using swift-ring-builder to create and rebalance the three rings, distributing the
> ring.gz and swift.conf files, starting the full set of services, and verifying with swift stat.
> The closing note states that the experiment ends here and the blog will be revised later.

> **Technical notes**
>
> Both OpenStack Mitaka and CentOS 7 have reached end of life. Cinder's v1 `volume` API and CLIs
> such as `cinder service-list` are deprecated; volumev3 and `openstack volume service list` are
> used instead today. The `git.openstack.org/cgit` configuration download source used in this
> post no longer works following the retirement of the OpenStack infrastructure; use the
> corresponding paths on opendev.org to fetch the same-version samples. Swift's
> swift-ring-builder ring-building workflow remains the standard practice to this day; production
> object storage nowadays more commonly uses Ceph RGW (S3-compatible) in place of a standalone
> Swift cluster.

---

## 1. Block Storage Service Configuration (Section 4.7 in the original: Block Storage Service — Cinder)

### Controller Node

Create the database:

```bash
mysql -u root -p123456
```

```sql
CREATE DATABASE cinder;
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'localhost' IDENTIFIED BY 'cinder';
GRANT ALL PRIVILEGES ON cinder.* TO 'cinder'@'%' IDENTIFIED BY 'cinder';
```

Register the user, services, and API endpoints (both the v1 and v2 sets):

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

Install and configure the Cinder service components:

```bash
yum install openstack-cinder
```

Edit the configuration file `/etc/cinder/cinder.conf` (the original omitted the `[database]`
section header for the database connection; it is added here):

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

Populate the database:

```bash
su -s /bin/sh -c "cinder-manage db sync" cinder
```

Configure the Compute service to use the Block Storage service. Edit the configuration file
`/etc/nova/nova.conf` and add the following:

```ini
[cinder]
os_region_name = RegionOne
```

```bash
systemctl restart openstack-nova-api.service
systemctl start openstack-cinder-api.service openstack-cinder-scheduler.service
systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service
```

### Storage Node (BlockStorage Node)

Install LVM and create the physical volume/volume group:

```bash
[root@blockstorage ~]# yum install lvm2
systemctl enable lvm2-lvmetad.service
systemctl start lvm2-lvmetad.service
[root@blockstorage ~]# pvcreate /dev/sdb
# Physical volume "/dev/sdb" successfully created
[root@blockstorage ~]# vgcreate cinder-volumes /dev/sdb
# Volume group "cinder-volumes" successfully created
```

Configure the node so that only OpenStack instances can access block storage volumes. Edit the
configuration file `/etc/lvm/lvm.conf` and add a filter in the devices section so that OpenStack
instances are only allowed to access `/dev/sdb`:

```ini
devices {
...
filter = [ "a/sdb/", "r/.*/" ]
```

Install and configure the block storage service components:

```bash
yum install openstack-cinder targetcli python-keystone
```

Edit the configuration file `/etc/cinder/cinder.conf`:

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

### Verification

```text
[root@controller ~]# cinder service-list
+------------------+------------------+------+---------+-------+----------------------------+-----------------+
|      Binary      |       Host       | Zone |  Status | State |         Updated_at         | Disabled Reason |
+------------------+------------------+------+---------+-------+----------------------------+-----------------+
| cinder-scheduler |    controller    | nova | enabled |   up  | 2016-09-03T14:19:51.000000 |        -        |
|  cinder-volume   | blockstorage@lvm | nova | enabled |   up  | 2016-09-03T14:19:27.000000 |        -        |
+------------------+------------------+------+---------+-------+----------------------------+-----------------+
```

## 2. Object Storage Service Configuration (Section 4.9 in the original: Object Storage Service — Swift)

Provides object storage and retrieval services over the REST API.

### Controller Node: Proxy Server

Deployment node: Controller Node.

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

Download the object storage proxy service configuration file from the object storage source
repository (the original git.openstack.org link is no longer valid):

```bash
curl -o /etc/swift/proxy-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/proxy-server.conf-sample?h=stable/mitaka
```

Edit the configuration file `/etc/swift/proxy-server.conf`:

```ini
[DEFAULT]
...
bind_port = 8080
user = swift
swift_dir = /etc/swift
```

In `[pipeline:main]`, remove the tempurl and tempauth modules and add the authtoken and
keystoneauth modules:

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

### Object Storage Node (ObjectStorage Node)

Note: perform the following steps on every object storage node.

Format and mount the storage devices:

```bash
yum install xfsprogs rsync -y
mkfs.xfs /dev/sdb
mkfs.xfs /dev/sdc
mkdir -p /srv/node/sdb
mkdir -p /srv/node/sdc
```

Append to `/etc/fstab`:

```text
/dev/sdb /srv/node/sdb xfs noatime,nodiratime,nobarrier,logbufs=8 0 2
/dev/sdc /srv/node/sdc xfs noatime,nodiratime,nobarrier,logbufs=8 0 2
```

```bash
mount /srv/node/sdb
mount /srv/node/sdc
```

Edit `/etc/rsyncd.conf`:

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

Install the packages and download the configuration templates for the account/container/object
servers:

```bash
yum install openstack-swift-account openstack-swift-container openstack-swift-object

curl -o /etc/swift/account-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/account-server.conf-sample?h=stable/mitaka
curl -o /etc/swift/container-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/container-server.conf-sample?h=stable/mitaka
curl -o /etc/swift/object-server.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/object-server.conf-sample?h=stable/mitaka
```

Edit the configuration file `/etc/swift/account-server.conf`. In `[DEFAULT]`, configure the bind
IP address, bind port, user, directory, and mount point.
Note: replace MANAGEMENT_INTERFACE_IP_ADDRESS below with the object storage node's Management
Network interface address, 10.0.0.51 or 10.0.0.52.

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

Edit the configuration file `/etc/swift/container-server.conf`, again replacing the management
network IP:

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

Edit the configuration file `/etc/swift/object-server.conf`, again replacing the management
network IP:

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

Set the directory ownership and permissions:

```bash
chown -R swift:swift /srv/node
mkdir -p /var/cache/swift
chown -R root:swift /var/cache/swift
chmod -R 775 /var/cache/swift
```

### Creating and Distributing the Initial Rings (Controller Node)

Deployment node: Controller Node.

```bash
cd /etc/swift
```

Create the base account.builder file:

```bash
[root@controller swift]# swift-ring-builder account.builder create 10 3 1
```

Add each object storage node's devices to the account ring:

```bash
swift-ring-builder account.builder add --region 1 --zone 1 \
  --ip STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS --port 6002 \
  --device DEVICE_NAME --weight DEVICE_WEIGHT
```

Note: replace STORAGE_NODE_MANAGEMENT_INTERFACE_IP_ADDRESS with the object storage node's
Management Network interface address, DEVICE_NAME with the name of the storage device on the
corresponding object storage node, and DEVICE_WEIGHT with the actual weight value. Repeat the
command above to add every storage device on every storage node to the account ring.

For example, this post uses the following commands to add each storage device on each storage
node to the account ring:

```bash
swift-ring-builder account.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6002 --device sdb --weight 100
swift-ring-builder account.builder add --region 1 --zone 1 --ip 10.0.0.51 --port 6002 --device sdc --weight 100
swift-ring-builder account.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6002 --device sdb --weight 100
swift-ring-builder account.builder add --region 1 --zone 2 --ip 10.0.0.52 --port 6002 --device sdc --weight 100
```

Verify:

```bash
swift-ring-builder account.builder
```

Rebalance the account ring:

```bash
[root@controller swift]# swift-ring-builder account.builder rebalance
# Reassigned 3072 (300.00%) partitions. Balance is now 0.00.  Dispersion is now 0.00
```

The container ring (port 6001) and the object ring (port 6000) follow the same procedure:

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

Distribute the ring configuration files. Copy the ring files account.ring.gz, container.ring.gz,
and object.ring.gz to the `/etc/swift` directory on every object storage node and on the proxy
service node. Run the following command on each storage node or proxy service node:

```bash
scp root@controller:/etc/swift/*.ring.gz /etc/swift
```

In this post, swift-proxy is deployed on the controller node, so there is no need to copy the
ring files to a separate proxy service node's `/etc/swift` directory (the original wording
contains a typo). If the object storage proxy service swift-proxy is deployed on another node,
the ring files must be copied to that proxy service node's `/etc/swift` directory.

### Adding and Distributing the swift Configuration File

1. Download the configuration file `/etc/swift/swift.conf` from the object storage source
repository:

```bash
curl -o /etc/swift/swift.conf https://git.openstack.org/cgit/openstack/swift/plain/etc/swift.conf-sample?h=stable/mitaka
```

2. Edit the configuration file `/etc/swift/swift.conf` and configure the hash path prefix and
suffix under `[swift-hash]`. Note: replace HASH_PATH_PREFIX and HASH_PATH_SUFFIX with the unique
values designed earlier.

```ini
[swift-hash]
...
swift_hash_path_suffix = HASH_PATH_SUFFIX
swift_hash_path_prefix = HASH_PATH_PREFIX

[storage-policy:0]
name = Policy-0
default = yes
```

3. Distribute the swift configuration file. Copy `/etc/swift/swift.conf` to the `/etc/swift`
directory on every object storage node and on the proxy service node. Run the following command
on each storage node or proxy service node:

```bash
scp root@controller:/etc/swift/swift.conf /etc/swift
```

4. Set ownership of the swift configuration directory on all storage nodes and proxy service
nodes:

```bash
chown -R root:swift /etc/swift
```

### Starting the Services and Verification

Run the following on the controller node and any other Swift proxy service nodes:

```bash
systemctl enable openstack-swift-proxy.service memcached.service
systemctl start openstack-swift-proxy.service memcached.service
```

Run the following on all object storage nodes:

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

Verify:

```bash
swift stat
```

---

> Original closing note: the experiment ends here, and this blog will be revised later (the
> original text contains a typo).
