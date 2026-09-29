---
title: "OpenStack Study Notes 10: neutron"
date: "2016-08-01 03:21:45"
category: "openstack"
source: "https://blog.51cto.com/hequan/1832696"
lang: "en"
---
> **About this post**
>
> This post is the networking part of the OpenStack multi-node deployment series. It first explains the past and present of neutron (the evolution involving quantum and nova-network), how the br-ex/br-int/br-tun bridges connect the internal and external networks, and the three tenant isolation technologies: VLAN, GRE, and VXLAN. It then walks through the hands-on steps: registering the neutron service on the control node h1, installing neutron + ml2 with the full neutron.conf and ml2_conf.ini listings, and finally installing the Open vSwitch agent on the network node h2, configuring the dhcp/l3/metadata agents together with the ifcfg-br-ex/ifcfg-eth1 bridge configurations, and using neutron agent-list to verify that every agent is up.

> **Technical notes**
>
> This post is based on Liberty-era components: the standalone neutron CLI has been deprecated and merged into the `openstack` command (agent-list is now `openstack network agent list`); keystone v2.0 authentication and the `admin_tenant_name` style have been removed in favor of the v3 project/domain model; and `rabbit_host` and similar settings in `[oslo_messaging_rabbit]` have been replaced by `transport_url`. Newer neutron releases have moved the default backend from OVS to OVN, and the ifcfg bridge style on CentOS 7 is gone along with network-scripts.

---

![Hand-drawn neutron network architecture diagram, labeling the br-ex and br-int bridges and each node](../assets/1832696/01_wKioL1eeT0fxFYT-AAHb7WtHzMg434.png)

![OpenStack network topology, the public network reaching the 192.168.2.0/24 subnet through a router](../assets/1832696/02_wKiom1eeT0eTF6jxAABR2D6JZ5o109.png)

![OpenStack network topology, the network1 subnet attached to the control node and h1](../assets/1832696/03_wKioL1eeT0fDFl1dAAAiOKTrt8g528.png)

![VM list in the virtualization management platform: h3 control node, h2 network node, and h1](../assets/1832696/04_wKiom1eeT0jylquOAAAokICe8eY326.png)

## 1. The neutron Network Architecture

The network node provides DHCP and routing for virtual machines.

Historical evolution: quantum ---> nova-network; early versions used Linux bridging -- flatDHCP.

Bridge connections between the nodes:

```text
Network node     external net--eth1--br-ex-------br-int--transparent eth0=====eth0--internal net
Compute node     VM qbr-xxxxx--br-int-----------phy-eth0-----transparent eth0=====eth0
VM interconnect  br-tun------tunnel------br-tun     vxlan
```

Several technologies for isolating networks between tenants:

| Technology | Description |
| ---- | ---- |
| VLAN | At most 4096 |
| GRE | A VPN tunnel type; every virtual host has to set up tunnels with one another |
| VXLAN (default) | About 16 million |

## 2. Installing neutron on the Control Node h1

Three machines: h1 is the control node (h1 has rabbitmq+keystone+swift+cinder+glance installed; see the earlier posts), and h2 is the network node.

First register the neutron user, service, and endpoint in keystone:

```bash
[root@h1 ~(key)]# keystone user-create --name neutron --pass hequan
[root@h1 ~(key)]# keystone user-role-add --user neutron --role admin --tenant services
[root@h1 ~(key)]# keystone service-create --name neutron --type network --description "neutron"
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
| description |             neutron              |
|   enabled   |               True               |
|     id      | 6e0c0784195f40658f725f796a35bc44 |
|    name     |             neutron              |
|    type     |             network              |
+-------------+----------------------------------+
[root@h1 ~(key)]# keystone endpoint-create --service-id 6e0c0784195f40658f725f796a35bc44 --publicurl 'http://192.168.1.5:9696' --internalurl 'http://192.168.1.5:9696' --adminurl 'http://192.168.1.5:9696'   # the control node's address
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
|  adminurl   |     http://192.168.1.5:9696      |
|     id      | 85c82c7119a04f7cb2a95614e078c3c2 |
| internalurl |     http://192.168.1.5:9696      |
|  publicurl  |     http://192.168.1.5:9696      |
|   region    |            regionOne             |
| service_id  | 6e0c0784195f40658f725f796a35bc44 |
+-------------+----------------------------------+
```

Install neutron and the ml2 plugin on the control node (ml2 is the core network plugin, responsible for tenant isolation; its role is to decide whether VLAN or VXLAN is used):

```bash
[root@h1 ~(key)]# yum install openstack-neutron.noarch openstack-neutron-ml2.noarch
```

```bash
[root@h1 neutron(key)]# ls
conf.d          metadata_agent.ini  plugins
dhcp_agent.ini  neutron.conf        policy.json
l3_agent.ini    neutron.conf.bak    rootwrap.conf
[root@h1 neutron(key)]# mv neutron.conf neutron.conf.bak
[root@h1 neutron(key)]# vim neutron.conf    ## edit the configuration file
```

The full neutron.conf:

```ini
[DEFAULT]
verbose = True
router_distributed = False
debug = False
state_path = /var/lib/neutron
use_syslog = False
use_stderr = True
log_dir =/var/log/neutron
bind_host = 0.0.0.0
bind_port = 9696
core_plugin =neutron.plugins.ml2.plugin.Ml2Plugin
service_plugins =router
auth_strategy = keystone
base_mac = fa:16:3e:00:00:00
mac_generation_retries = 16
dhcp_lease_duration = 86400
dhcp_agent_notification = True
allow_bulk = True
allow_pagination = False
allow_sorting = False
allow_overlapping_ips = True
advertise_mtu = False
agent_down_time = 75
router_scheduler_driver = neutron.scheduler.l3_agent_scheduler.ChanceScheduler
allow_automatic_l3agent_failover = False
dhcp_agents_per_network = 1
l3_ha = False
api_workers = 1
rpc_workers = 1
use_ssl = False
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
nova_url = http://192.168.1.5:8774/v2
nova_region_name =RegionOne
nova_admin_username =nova
nova_admin_tenant_name =services
nova_admin_password =hequan
nova_admin_auth_url =http://192.168.1.5:5000/v2.0
send_events_interval = 2
rpc_response_timeout=60
rpc_backend=rabbit
control_exchange=neutron
lock_path=/var/lib/neutron/lock
[matchmaker_redis]
[matchmaker_ring]
[quotas]
[agent]
root_helper = sudo neutron-rootwrap /etc/neutron/rootwrap.conf
report_interval = 30
[keystone_authtoken]
auth_uri = http://192.168.1.5:5000/v2.0
identity_uri = http://192.168.1.5:35357
admin_tenant_name = services
admin_user = neutron
admin_password = hequan
[database]
connection = mysql://neutron:hequan@192.168.1.5/neutron
max_retries = 10
retry_interval = 10
min_pool_size = 1
max_pool_size = 10
idle_timeout = 3600
max_overflow = 20
[nova]
[oslo_concurrency]
[oslo_policy]
[oslo_messaging_amqp]
[oslo_messaging_qpid]
[oslo_messaging_rabbit]
kombu_reconnect_delay = 1.0
rabbit_host = 192.168.1.5
rabbit_port = 5672
rabbit_hosts = 192.168.1.5:5672
rabbit_use_ssl = False
rabbit_userid = guest
rabbit_password = guest
rabbit_virtual_host = /
rabbit_ha_queues = False
heartbeat_rate=2
heartbeat_timeout_threshold=0
[qos]
```

Edit the ml2_conf.ini configuration file:

```bash
[root@h1 ml2(key)]# pwd
/etc/neutron/plugins/ml2
[root@h1 ml2(key)]# grep -vE "^$|^#" ml2_conf.ini
```

```ini
[ml2]
type_drivers = vxlan
tenant_network_types = vxlan
mechanism_drivers =openvswitch
path_mtu = 0
[ml2_type_flat]
[ml2_type_vlan]
[ml2_type_gre]
[ml2_type_vxlan]
vni_ranges =10:100
vxlan_group =224.0.0.1
[ml2_type_geneve]
[securitygroup]
enable_security_group = True
```

Create the symlink, initialize the database, and start the service:

```bash
[root@h1 neutron(key)]# ln -s /etc/neutron/plugins/ml2/ml2_conf.ini plugin.ini   ## create a symlink, in the neutron directory
[root@h1 ~(key)]# openstack-db --init --service neutron --password hequan --rootpw 123456   ## create the database
ERROR 1146 (42S02) at line 1: Table 'neutron.migrate_version' doesn't exist    ## ignore this error
Final sanity check failed.
Please file a bug report on  against the openstack-neutron package.
[root@h1 neutron(key)]# systemctl start neutron-server.service
[root@h1 neutron(key)]# systemctl enable neutron-server.service
```

## 3. Configuring the Network Node h2

NICs on the network node: eth0 serves the internal network, and eth1 is attached to the external network.

```bash
[root@h2 ~]# hostname
h2.hequan.lol
```

```text
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500    ## internal network
        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255
eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500    ## attached to the external network
        inet 192.168.2.2  netmask 255.255.255.0  broadcast 192.168.1.255
```

```bash
[root@h2 ~]# systemctl stop NetworkManager.service
[root@h2 ~]# systemctl disable NetworkManager.service
```

After configuring yum (see the earlier posts), install neutron and the Open vSwitch agent:

```bash
[root@h2 ~]# yum install openstack-neutron.noarch openstack-neutron-openvswitch.noarch -y
[root@h2 ~]# systemctl start openvswitch
[root@h2 ~]# systemctl enable openvswitch
```

Create the bridges:

```bash
[root@h2 ~]# ovs-vsctl add-br br-ex
[root@h2 ~]# ovs-vsctl add-br br-int
[root@h2 ~]# ovs-vsctl add-br br-tun

[root@h2 ~]# ovs-vsctl list-br
br-ex
br-int
br-tun
```

Copy the neutron.conf written above on the control node to the network node:

```bash
[root@h2 neutron]# mv neutron.conf neutron.conf.bak
## copy the neutron.conf written above to this directory
[root@h2 neutron]# chown root.neutron neutron.conf
```

Configure dhcp_agent.ini (DHCP service):

```ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
ovs_integration_bridge = br-int
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
use_namespaces = True
force_metadata = False
enable_isolated_metadata = False
enable_metadata_network = False
[AGENT]
```

Configure l3_agent.ini (routing):

```ini
[DEFAULT]
debug = False
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
use_namespaces = True
external_network_bridge = br-ex
metadata_port = 9697
agent_mode = legacy
[AGENT]
```

Configure metadata_agent.ini:

```ini
[DEFAULT]
auth_url = http://192.168.1.5:5000/v2.0
auth_region = regionOne
admin_tenant_name = services
admin_user = neutron
admin_password = hequan
nova_metadata_ip = 192.168.1.5
nova_metadata_port = 8775
nova_metadata_protocol = http
nova_metadata_insecure = False
cache_url = memory://?default_ttl=5
[AGENT]
```

Configure the external network bridge br-ex and eth1:

```bash
[root@h2 network-scripts]# cat ifcfg-br-ex
```

```ini
DEVICE=br-ex
DEVICETYPE=ovs
TYPE=OVSBridge
ONBOOT=yes
BOOTPROTO=none
IPADDR=192.168.2.2
NETMASK=255.255.255.0
GATEWAY=192.168.2.1
DNS1=202.106.0.20
```

```bash
[root@h2 network-scripts]# cat ifcfg-eth1
```

```ini
DEVICE=eth1
DEVICETYPE=ovs
TYPE=OVSPort
OVS_BRIDGE=br-ex
ONBOOT=yes
BOOTPROTO=none
```

```bash
[root@h2 network-scripts]# systemctl restart network
```

Configure openvswitch_agent.ini (VXLAN tunnel mode):

```ini
[ovs]
integration_bridge = br-int
tunnel_bridge = br-tun
local_ip = 192.168.1.10   ## local IP
bridge_mappings = physnet1:eth0
[agent]
tunnel_types = vxlan
[securitygroup]
```

Start the agent services:

```bash
[root@h2 ml2]# systemctl start neutron-dhcp-agent.service neutron-l3-agent.service neutron-metadata-agent.service neutron-openvswitch-agent.service
[root@h2 ml2]# systemctl enable neutron-dhcp-agent.service neutron-l3-agent.service neutron-metadata-agent.service neutron-openvswitch-agent.service
```

## 4. Verifying Agent Status

Check the agent list on the control node:

```bash
[root@h1 ~(key)]# neutron agent-list
+--------------------------------------+--------------------+---------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host          | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+---------------+-------+----------------+---------------------------+
| 1264da88-1570-445f-ab9a-a3fb0dcc4743 | DHCP agent         | h2.hequan.lol | :-)   | True           | neutron-dhcp-agent        |
| 5503e449-9373-430a-9f8f-9714d2ad1af6 | Linux bridge agent | h2.hequan.lol | :-)   | True           | neutron-linuxbridge-agent |
| 797a7b92-f62f-4e01-b075-b1fe5868618b | Metadata agent     | h2.hequan.lol | :-)   | True           | neutron-metadata-agent    |
| 8c5cd9c4-3ded-4eb5-91a2-fa420a3501a5 | L3 agent           | h2.hequan.lol | :-)   | True           | neutron-l3-agent          |
+--------------------------------------+--------------------+---------------+-------+----------------+---------------------------+
```
