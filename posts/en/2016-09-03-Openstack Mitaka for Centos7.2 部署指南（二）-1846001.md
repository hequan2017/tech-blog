---
title: "OpenStack Mitaka Deployment Guide for CentOS 7.2 (Part 2)"
date: "2016-09-03 21:43:24"
category: "openstack"
source: "https://blog.51cto.com/hequan/1846001"
lang: "en"
---
> **About this post**
>
> This is the second part of the CentOS 7.2 OpenStack Mitaka deployment series, covering the complete configuration of three components: the nova compute service (the control node runs api/conductor/scheduler/novncproxy and the compute node runs nova-compute, including VNC and hardware acceleration detection), the neutron networking service (a Self-Service network architecture based on Linux Bridge + VXLAN, covering control, network, and compute nodes), and the horizon dashboard (key local_settings settings).

> **Technical notes**
>
> This post is based on Mitaka: the nova consoleauth service has been removed in later releases; the standalone neutron CLI (agent-list/ext-list) has been merged into the `openstack` command; `auth_plugin` has been renamed to `auth_type`; the `rpc_backend` option has been superseded by `transport_url`; and horizon's `vnc_auto.html` has been replaced by `vnc_lite.html`. In the "configure the compute node to use networking" step in section 4.5, the hostname controller1 in `auth_url = http://controller1:35357` appears to be a typo (it should be controller) and has been corrected according to context.

---

## 4.4 Compute Service Configuration (Nova)

### Control node

On the Controller node, you need to install nova-api, nova-conductor, nova-consoleauth, nova-novncproxy, and nova-scheduler.

Create the nova databases:

```sql
mysql -u root -p123456
CREATE DATABASE nova_api;
CREATE DATABASE nova;
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' IDENTIFIED BY 'novaapi';
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' IDENTIFIED BY 'novaapi';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY 'nova';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'nova';
```

Create the user, service, and endpoints:

```bash
openstack user create --domain default --password-prompt nova
openstack role add --project service --user nova admin
openstack service create --name nova --description "OpenStack Compute" compute
openstack endpoint create --region RegionOne compute public http://controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute internal http://controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute admin http://controller:8774/v2.1/%\(tenant_id\)s
```

Install the Nova components:

```bash
yum install openstack-nova-api openstack-nova-conductor openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler
```

Edit the configuration file `sudo vi /etc/nova/nova.conf`.

In the [DEFAULT] section, enable only the compute and metadata APIs:

```ini
enabled_apis = osapi_compute,metadata
```

In the [api_database] and [database] sections, configure database access (add these two section markers manually if they do not exist; replace NOVA_DBPASS with the actual password):

```ini
[api_database]
...
connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova_api
[database]
...
connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova
```

In the [DEFAULT] and [oslo_messaging_rabbit] sections, configure RabbitMQ message queue access (replace RABBIT_PASS with the actual password):

```ini
[DEFAULT]
...
rpc_backend = rabbit

[oslo_messaging_rabbit]
...
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = RABBIT_PASS
```

In the [DEFAULT] and [keystone_authtoken] sections, configure Identity service access (replace NOVA_PASS with the actual password; comment out or remove anything else in the [keystone_authtoken] section):

```ini
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
username = nova
password = NOVA_PASS
```

In the [DEFAULT] section, set my_ip to the Management Network interface IP of the Controller node:

```ini
my_ip = 10.0.0.11
```

In the [DEFAULT] section, enable support for the Networking service (by default the compute service uses an internal firewall driver, so the firewall driver in the OpenStack Networking service must be disabled):

```ini
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver
```

In the [vnc] section, configure the VNC proxy to use the Management Network interface IP of the Controller node:

```ini
[vnc]
...
vncserver_listen = $my_ip
vncserver_proxyclient_address = $my_ip
```

In the [glance] section, configure the location of the Image Service API:

```ini
[glance]
...
api_servers = http://controller:9292
```

In the [oslo_concurrency] section, configure lock_path:

```ini
[oslo_concurrency]
...
lock_path = /var/lib/nova/tmp
```

Populate the compute service database:

```bash
su -s /bin/sh -c "nova-manage api_db sync" nova
su -s /bin/sh -c "nova-manage db sync" nova
```

Start the compute services:

```bash
systemctl enable openstack-nova-api.service openstack-nova-consoleauth.service openstack-nova-scheduler.service openstack-nova-conductor.service openstack-nova-novncproxy.service
systemctl start openstack-nova-api.service openstack-nova-consoleauth.service openstack-nova-scheduler.service openstack-nova-conductor.service openstack-nova-novncproxy.service
```

### Compute node

On the Compute node, you need to install nova-compute (the following steps are performed on the Compute node).

Install the nova-compute component:

```bash
yum install openstack-nova-compute
```

Edit the configuration file `sudo vi /etc/nova/nova.conf`.

In the [DEFAULT] and [oslo_messaging_rabbit] sections, configure RabbitMQ message queue access:

```ini
[DEFAULT]
...
rpc_backend = rabbit
[oslo_messaging_rabbit]
...
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = RABBIT_PASS
```

In the [DEFAULT] and [keystone_authtoken] sections, configure Identity service access:

```ini
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
username = nova
password = NOVA_PASS
```

In the [DEFAULT] section, set my_ip to the Management Network interface IP of the Compute node:

```ini
my_ip=10.0.0.31
```

In the [DEFAULT] section, enable support for the Networking service:

```ini
[DEFAULT]
...
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver
```

In the [vnc] section, configure remote console access:

```ini
[vnc]
...
enabled = True
vncserver_listen = 0.0.0.0
vncserver_proxyclient_address = $my_ip
novncproxy_base_url = http://controller:6080/vnc_auto.html
```

Note: the VNC server listens on all addresses, the VNC proxy client uses only the Management Network interface IP of the Compute node, and the base URL sets the browser access address for the Compute node's remote console (if the browser cannot resolve controller, replace it with the corresponding IP address).

In the [glance] section, configure the Image Service API:

```ini
api_servers = http://controller:9292
```

In the [oslo_concurrency] section, configure lock_path:

```ini
lock_path = /var/lib/nova/tmp
```

Finish the installation and start the compute service. First check whether the node supports hardware acceleration for virtual machines:

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
```

If the return value is 1 or greater, it is supported and no extra configuration is needed; if it returns 0, hardware acceleration is not supported, and you must modify the libvirt settings in the configuration file `/etc/nova/nova-compute.conf` to use QEMU instead of KVM:

```ini
[libvirt]
virt_type = qemu
```

```bash
systemctl enable libvirtd.service openstack-nova-compute.service
systemctl start libvirtd.service openstack-nova-compute.service
```

### Verify the compute service

The following steps must be performed on the Controller node:

```bash
source admin-openrc
```

List the service components to verify that each process launched and registered successfully:

```bash
[root@controller ~]# openstack compute service list
+----+------------------+------------+----------+---------+-------+----------------------------+
| Id | Binary           | Host       | Zone     | Status  | State | Updated At                 |
+----+------------------+------------+----------+---------+-------+----------------------------+
|  1 | nova-consoleauth | controller | internal | enabled | up    | 2016-09-03T09:29:56.000000 |
|  2 | nova-conductor   | controller | internal | enabled | up    | 2016-09-03T09:29:56.000000 |
|  3 | nova-scheduler   | controller | internal | enabled | up    | 2016-09-03T09:29:56.000000 |
|  7 | nova-compute     | compute    | nova     | enabled | up    | 2016-09-03T09:29:56.000000 |
+----+------------------+------------+----------+---------+-------+----------------------------+
```

## 4.5 Networking Service Configuration (Neutron)

### Control node

Create the neutron database in MariaDB (MySQL):

```sql
mysql -u root -p
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY 'neutron';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'neutron';
```

Create the Networking service credentials and API endpoints:

```bash
openstack user create --domain default --password-prompt neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking" network
openstack endpoint create --region RegionOne network public http://controller:9696
openstack endpoint create --region RegionOne network internal http://controller:9696
openstack endpoint create --region RegionOne network admin http://controller:9696
```

Install and configure the neutron-server service component:

```bash
yum install openstack-neutron openstack-neutron-ml2
vi /etc/neutron/neutron.conf
```

```ini
[database]
connection = mysql://neutron:neutron@controller/neutron
[DEFAULT]
core_plugin = ml2
service_plugins = router
allow_overlapping_ips = True
rpc_backend = rabbit
auth_strategy = keystone
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
verbose = True
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = openstack
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = neutron
password = neutron
[nova]
auth_url = http://controller:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
region_name = RegionOne
project_name = service
username = nova
password = nova
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
```

Configure the ML2 plugin: it uses the Linux bridge mechanism to build the layer-2 virtual networking infrastructure (bridging and switching) for OpenStack instances. Edit the configuration file `/etc/neutron/plugins/ml2/ml2_conf.ini`:

```ini
[ml2]
type_drivers = flat,vlan,vxlan   # removing this after ML2 is configured causes database inconsistency
tenant_network_types = vxlan
mechanism_drivers = linuxbridge,l2population
extension_drivers = port_security   ## enable the port security extension driver
[ml2_type_flat]
flat_networks = public   ## the provider virtual network is a flat network
[ml2_type_vxlan]
vni_ranges = 1:1000
[securitygroup]
enable_ipset = True   ## enable ipset to improve the efficiency of security group rules
```

Populate the neutron database:

```bash
su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
```

Configure the compute node to use networking; edit `vi /etc/nova/nova.conf`:

```ini
[neutron]
url = http://controller:9696
auth_url = http://controller:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
region_name = RegionOne
project_name = service
username = neutron
password = neutron
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata
```

Create the file link:

```bash
ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
```

Start the services:

```bash
systemctl restart openstack-nova-api.service
systemctl restart neutron-server.service
systemctl start neutron-metadata-agent.service
systemctl enable neutron-server.service
systemctl enable neutron-metadata-agent.service
```

### Network node

There are two deployment architecture options for the Networking service: Provider Networks and Self-Service Networks. This post deploys it in the Self-Service Networks mode.

```bash
yum install openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables
```

Configure the common service components (authentication mechanism and message queue); edit `/etc/neutron/neutron.conf`:

```ini
[DEFAULT]
rpc_backend = rabbit
auth_strategy = keystone
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = openstack
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = neutron
```

Configure the Linux bridge agent. The Linux bridge agent builds the layer-2 virtual networking infrastructure for instances and can also manage security groups. Edit the configuration file `/etc/neutron/plugins/ml2/linuxbridge_agent.ini`:

```ini
[linux_bridge]
physical_interface_mappings = public:eth0   # note the name of the bridged interface
[vxlan]
enable_vxlan = True
local_ip = 10.0.0.21   # IP address of the physical public network interface
l2_population = True
[agent]
prevent_arp_spoofing = True
[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
```

Configure the layer-3 agent. The L3 (Layer-3) agent provides routing and NAT services for self-service networks. Edit the configuration file `/etc/neutron/l3_agent.ini`; in the [DEFAULT] section, configure the Linux bridge interface driver and the external network bridge:

```ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
external_network_bridge =    #### note: deliberately left blank so that one agent can serve multiple external networks
verbose = True
```

Edit the configuration file `/etc/neutron/dhcp_agent.ini`; in the [DEFAULT] section, configure the Linux bridge interface driver and the Dnsmasq DHCP driver, and enable isolated metadata so that instances on provider networks can access the virtual network metadata:

```ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
enable_isolated_metadata = True
verbose = True
```

Configure the metadata agent. The metadata agent provides configuration information such as credentials. Edit the configuration file `/etc/neutron/metadata_agent.ini`; in the [DEFAULT] section, configure the metadata host and the shared secret (replace METADATA_SECRET with the actual password):

```ini
[DEFAULT]
nova_metadata_ip = controller
metadata_proxy_shared_secret = metadata
```

Start the services:

```bash
systemctl start neutron-linuxbridge-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
systemctl enable neutron-linuxbridge-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
```

### Compute node

Install the networking service components:

```bash
[root@compute ~]# yum install openstack-neutron-linuxbridge
```

Configure the common components (authentication mechanism, message queue, and plugin):

```ini
[root@compute ~]# cat /etc/neutron/neutron.conf
[DEFAULT]
rpc_backend = rabbit
auth_strategy = keystone
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = openstack
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = neutron
```

Configure the Linux bridge agent; edit the configuration file `/etc/neutron/plugins/ml2/linuxbridge_agent.ini`:

```ini
[linux_bridge]
physical_interface_mappings = provider:eth0
[vxlan]
enable_vxlan = True
local_ip = 10.0.0.31
l2_population = True
[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
```

Configure the compute service to use networking; edit the configuration file `/etc/nova/nova.conf`:

```ini
[neutron]
url = http://controller:9696
auth_url = http://controller:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = neutron
```

Restart the services:

```bash
systemctl restart openstack-nova-compute.service
systemctl restart neutron-linuxbridge-agent.service
systemctl enable neutron-linuxbridge-agent.service
```

Verification:

```bash
[root@controller ~]# neutron ext-list
[root@controller ~]# neutron agent-list
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host       | availability_zone | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
| 0e1c9f6f-a56b-40d1-b43e-91754cabcf75 | Metadata agent     | network    |                   | :-)   | True           | neutron-metadata-agent    |
| 24c8daec-b495-48ba-b70d-f7d103c8cda1 | Linux bridge agent | compute    |                   | :-)   | True           | neutron-linuxbridge-agent |
| 2e93bf03-e095-444d-8f74-0b832db4a0be | Linux bridge agent | network    |                   | :-)   | True           | neutron-linuxbridge-agent |
| 456c754a-d2c0-4ce5-8d9b-b0089fb77647 | Metadata agent     | controller |                   | :-)   | True           | neutron-metadata-agent    |
| 8a1c7895-fc44-407f-b74b-55bb1b4519d8 | DHCP agent         | network    | nova              | :-)   | True           | neutron-dhcp-agent        |
| 93ad18bf-d961-4d00-982c-6c617dbc0a5e | L3 agent           | network    | nova              | :-)   | True           | neutron-l3-agent          |
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
```

## 4.6 Dashboard Service Configuration (Horizon)

The dashboard is a web interface that allows cloud administrators and users to manage the various OpenStack resources and services. This post deploys the Dashboard service with the Apache Web Server.

Deployment node: Controller Node

```bash
yum install openstack-dashboard
```

Edit the configuration file `sudo vim /etc/openstack-dashboard/local_settings`:

```python
OPENSTACK_HOST = "controller"

ALLOWED_HOSTS = ['*', ]

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'controller:11211',
    }
}

OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST

OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True

OPENSTACK_API_VERSIONS = {
    "identity": 3,
    "image": 2,
    "volume": 2,
}

OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "default"

OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"

OPENSTACK_NEUTRON_NETWORK = {
    ...
    'enable_router': False,
    'enable_quotas': False,
    'enable_distributed_router': False,
    'enable_ha_router': False,
    'enable_lb': False,
    'enable_firewall': False,
    'enable_vpn': False,
    'enable_fip_topology_check': False,
}

TIME_ZONE = "TIME_ZONE"
```

Note: the value of `TIME_ZONE` is a placeholder copied from the official documentation; in practice it should be set to your own time zone, e.g. `Asia/Shanghai`.

```bash
systemctl restart httpd.service memcached.service
```
