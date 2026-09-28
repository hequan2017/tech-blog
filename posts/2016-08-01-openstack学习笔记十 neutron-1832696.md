---
title: "openstack学习笔记十 neutron"
date: "2016-08-01 03:21:45"
category: "openstack"
source: "https://blog.51cto.com/hequan/1832696"
---

[![openstack学习笔记十 neutron_OpenStack](assets/1832696/01_wKioL1eeT0fxFYT-AAHb7WtHzMg434.png)](http://s3.51cto.com/wyfs02/M01/85/40/wKioL1eeT0fxFYT-AAHb7WtHzMg434.png-wh_500x0-wm_3-wmp_4-s_1196143743.png)

[![openstack学习笔记十 neutron_neutron_02](assets/1832696/02_wKiom1eeT0eTF6jxAABR2D6JZ5o109.png)](http://s3.51cto.com/wyfs02/M02/85/40/wKiom1eeT0eTF6jxAABR2D6JZ5o109.png-wh_500x0-wm_3-wmp_4-s_3743352585.png)

[![openstack学习笔记十 neutron_OpenStack_03](assets/1832696/03_wKioL1eeT0fDFl1dAAAiOKTrt8g528.png)](http://s3.51cto.com/wyfs02/M02/85/40/wKioL1eeT0fDFl1dAAAiOKTrt8g528.png-wh_500x0-wm_3-wmp_4-s_3071133047.png)

[![openstack学习笔记十 neutron_neutron_04](assets/1832696/04_wKiom1eeT0jylquOAAAokICe8eY326.png)](http://s5.51cto.com/wyfs02/M00/85/40/wKiom1eeT0jylquOAAAokICe8eY326.png-wh_500x0-wm_3-wmp_4-s_1226585640.png)

---

网络节点           为虚拟机提供DHCP    路由功能

quantum--->nova-network 早期版本  linux 桥接--flatDHCP

网络节点            外网--eht1--br-ex  -------br-int--透明eth0=====eht0--内网

计算节点            虚拟机qbr-xxxxx--br-int-----------phy-eth0-----透明eth0=====eht0

虚拟机互联         br-tun------vpn------br-tun        vxlan

实现不同租户之间网络隔离的几种技术：

vlan                   4096个

gre                     一种××× 隧道  每个虚拟主机都要互相建立×××

vxlan（默认）    1600万个

---

3台机器，h1是控制节点      h1安装了rabbitmq+keystone+swift+cinder+glance  ，可以看前面的写的博客

h2是网络节点

```bash
[root@h1 ~(key)]# keystone user-create  --name neutron  --pass  hequan
[root@h1 ~(key)]# keystone  user-role-add  --user neutron --role admin  --tenant  services
[root@h1 ~(key)]# keystone service-create  --name neutron  --type network  --description "neutron"
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
| description |             neutron              |
|   enabled   |               True               |
|      id     | 6e0c0784195f40658f725f796a35bc44 |
|     name    |             neutron              |
|     type    |             network              |
+-------------+----------------------------------+
keystone  endpoint-create  --service-id  6e0c0784195f40658f725f796a35bc44  --publicurl  'http://192.168.1.5:9696'  --internalurl  'http://192.168.1.5:9696'  --adminurl  'http://192.168.1.5:9696'   #控制节点的地址
+-------------+----------------------------------+
|   Property  |              Value               |
+-------------+----------------------------------+
|   adminurl  |     http://192.168.1.5:9696      |
|      id     | 85c82c7119a04f7cb2a95614e078c3c2 |
| internalurl |     http://192.168.1.5:9696      |
|  publicurl  |     http://192.168.1.5:9696      |
|    region   |            regionOne             |
|  service_id | 6e0c0784195f40658f725f796a35bc44 |
+-------------+----------------------------------+
```

```bash
[root@h1 ~(key)]# yum  install  openstack-neutron.noarch   openstack-neutron-ml2.noarch     ##在控制节点上安装
ml2是  网络核心插件,不同租户隔离    作用：实用 VLNA 还是VXLAN  分配
[root@h1 neutron(key)]# ls
conf.d          metadata_agent.ini  plugins
dhcp_agent.ini  neutron.conf        policy.json
l3_agent.ini    neutron.conf.bak    rootwrap.conf
[root@h1 neutron(key)]# mv neutron.conf neutron.conf.bak

vim neutron.conf      ###修改配置文件
[DEFAULT]
verbose = True
router_distributed = False
debug = False
state_path = /var/lib/neutron
use_syslog = False
use_stderr = True
log_dir =/var/log/neutron
bind_host = 0.0.0.0
bind_port = 9696
core_plugin =neutron.plugins.ml2.plugin.Ml2Plugin
service_plugins =router
auth_strategy = keystone
base_mac = fa:16:3e:00:00:00
mac_generation_retries = 16
dhcp_lease_duration = 86400
dhcp_agent_notification = True
allow_bulk = True
allow_pagination = False
allow_sorting = False
allow_overlapping_ips = True
advertise_mtu = False
agent_down_time = 75
router_scheduler_driver = neutron.scheduler.l3_agent_scheduler.ChanceScheduler
allow_automatic_l3agent_failover = False
dhcp_agents_per_network = 1
l3_ha = False
api_workers = 1
rpc_workers = 1
use_ssl = False
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
nova_url = http://192.168.1.5:8774/v2
nova_region_name =RegionOne
nova_admin_username =nova
nova_admin_tenant_name =services
nova_admin_password =hequan
nova_admin_auth_url =http://192.168.1.5:5000/v2.0
send_events_interval = 2
rpc_response_timeout=60
rpc_backend=rabbit
control_exchange=neutron
lock_path=/var/lib/neutron/lock
[matchmaker_redis]
[matchmaker_ring]
[quotas]
[agent]
root_helper = sudo neutron-rootwrap /etc/neutron/rootwrap.conf
report_interval = 30
[keystone_authtoken]
auth_uri = http://192.168.1.5:5000/v2.0
identity_uri = http://192.168.1.5:35357
admin_tenant_name = services
admin_user = neutron
admin_password = hequan
[database]
connection = mysql://neutron:hequan@192.168.1.5/neutron
max_retries = 10
retry_interval = 10
min_pool_size = 1
max_pool_size = 10
idle_timeout = 3600
max_overflow = 20
[nova]
[oslo_concurrency]
[oslo_policy]
[oslo_messaging_amqp]
[oslo_messaging_qpid]
[oslo_messaging_rabbit]
kombu_reconnect_delay = 1.0
rabbit_host = 192.168.1.5
rabbit_port = 5672
rabbit_hosts = 192.168.1.5:5672
rabbit_use_ssl = False
rabbit_userid = guest
rabbit_password = guest
rabbit_virtual_host = /
rabbit_ha_queues = False
heartbeat_rate=2
heartbeat_timeout_threshold=0
[qos]
[root@h1 ml2(key)]# pwd
/etc/neutron/plugins/ml2
[root@h1 ml2(key)]# grep  -vE "^$|^#" ml2_conf.ini      ##修改此配置文件
[ml2]
type_drivers = vxlan
tenant_network_types = vxlan
mechanism_drivers =openvswitch
path_mtu = 0
[ml2_type_flat]
[ml2_type_vlan]
[ml2_type_gre]
[ml2_type_vxlan]
vni_ranges =10:100
vxlan_group =224.0.0.1
[ml2_type_geneve]
[securitygroup]
enable_security_group = True

[root@h1 neutron(key)]# ln -s  /etc/neutron/plugins/ml2/ml2_conf.ini  plugin.ini                 ##创建快捷链接，在neutron目录下
[root@h1 ~(key)]# openstack-db --init  --service  neutron  --password hequan  --rootpw  123456  ##创建数据库
ERROR 1146 (42S02) at line 1: Table 'neutron.migrate_version' doesn't exist                     ###这个报错忽略
Final sanity check failed.
Please file a bug report on  against the openstack-neutron package.
[root@h1 neutron(key)]# systemctl   start  neutron-server.service
[root@h1 neutron(key)]# systemctl   enable  neutron-server.service 

网络节点
[root@h2 ~]# hostname
h2.hequan.lol
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500          ##做内网
        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255
eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500          ##绑定到外网了
        inet 192.168.2.2  netmask 255.255.255.0  broadcast 192.168.1.255
[root@h2 ~]# systemctl  stop NetworkManager.service
[root@h2 ~]# systemctl  disable NetworkManager.service

配置好  yum  可参考前面的博客
[root@h2 ~]# yum install openstack-neutron.noarch openstack-neutron-openvswitch.noarch -y
[root@h2 ~]# systemctl start openvswitch
[root@h2 ~]# systemctl enable openvswitch

[root@h2 ~]# ovs-vsctl  add-br br-ex
[root@h2 ~]# ovs-vsctl  add-br br-int
[root@h2 ~]# ovs-vsctl  add-br br-tun
[root@h2 ~]# ovs-vsctl  add-br eth0

[root@h2 ~]# ovs-vsctl list-br   
br-ex
br-int
br-tun
eth0

[root@h2 neutron]# mv neutron.conf neutron.conf.bak

##把上面写的  neutron.conf 复制到 这里
[root@h2 neutron]# chown root.neutron  neutron.conf

[root@h2 neutron]# vim dhcp_agent.ini    #dhcp服务
[DEFAULT]
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
ovs_integration_bridge = br-int
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
use_namespaces = True
force_metadata = False
enable_isolated_metadata = False
enable_metadata_network = False
[AGENT]
[root@h2 neutron]# vim l3_agent.ini    ##路由
[DEFAULT]
debug = False
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
use_namespaces = True
external_network_bridge = br-ex
metadata_port = 9697
agent_mode = legacy
[AGENT]

[root@h2 neutron]#  vim   metadata_agent.ini  ##
[DEFAULT]
auth_url = http://192.168.1.5:5000/v2.0
auth_region = regionOne
admin_tenant_name = service
admin_user = neutron
admin_password = hequan
nova_metadata_ip = 192.168.1.5
nova_metadata_port = 8775
nova_metadata_protocol = http
nova_metadata_insecure = False
cache_url = memory://?default_ttl=5
[AGENT]
[root@h2 network-scripts]# cat ifcfg-br-ex
DEVICE=br-ex
DEVICETYPE=ovs
TYPE=OVSBridge
ONBOOT=yes
BOOTPROTO=none
IPADDR=192.168.2.2
NETMASK=255.255.255.0
GATEWAY=192.168.2.1
DNS1=202.106.0.20

[root@h2 network-scripts]# cat ifcfg-eth1
DEVICE=eth1
DEVICETYPE=ovs
TYPE=OVSPort
OVS_BRIDGE=br-ex
ONBOOT=yes
BOOTPROTO=none

[root@h2 network-scripts]# systemctl  restart network

[root@h2 ml2]# vim  openvswitch_agent.ini
[ovs]
[agent]
[securitygroup]
3. With VXLAN tunneling.
[ovs]
integration_bridge = br-int
tunnel_bridge = br-tun
local_ip = 192.168.1.10  ##本地ip
bridge_mappings = physnet1:eth0
[agent]
tunnel_types = vxlan

[root@h2 ml2]# systemctl start neutron-dhcp-agent.service  neutron-l3-agent.service  neutron-metadata-agent.service   neutron-openvswitch-agent.service
systemctl enable neutron-dhcp-agent.service  neutron-l3-agent.service  neutron-metadata-agent.service   neutron-openvswitch-agent.service

[root@h1 ~(key)]# neutron agent-list
+--------------------------------------+--------------------+---------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host          | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+---------------+-------+----------------+---------------------------+
| 1264da88-1570-445f-ab9a-a3fb0dcc4743 | DHCP agent         | h2.hequan.lol | :-)   | True           | neutron-dhcp-agent        |
| 5503e449-9373-430a-9f8f-9714d2ad1af6 | Linux bridge agent | h2.hequan.lol | :-)   | True           | neutron-linuxbridge-agent |
| 797a7b92-f62f-4e01-b075-b1fe5868618b | Metadata agent     | h2.hequan.lol | :-)   | True           | neutron-metadata-agent    |
| 8c5cd9c4-3ded-4eb5-91a2-fa420a3501a5 | L3 agent           | h2.hequan.lol | :-)   | True           | neutron-l3-agent          |
+--------------------------------------+--------------------+---------------+-------+----------------+---------------------------+
```
