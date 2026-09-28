---
title: "Openstack Mitaka for  Centos7.2 部署指南（二）"
date: "2016-09-03 21:43:24"
category: "openstack"
source: "https://blog.51cto.com/hequan/1846001"
---

4.4 计算服务配置（Compute Service Nova）

部署节点：Controller Node

在Controller节点上需要安装novaapi  novaconductor  novaconsoleauth  novanovncproxy  novascheduler

```bash
mysql -u root  -p123456
CREATE DATABASE nova_api;
CREATE DATABASE nova;
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' IDENTIFIED BY 'novaapi';
GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' IDENTIFIED BY 'novaapi';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY 'nova';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY 'nova';
```

```bash
openstack user create --domain default   --password-prompt nova
openstack role add --project service --user nova admin
openstack service create --name nova   --description "OpenStack Compute" compute
openstack endpoint create --region RegionOne   compute public http://controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne   compute internal http://controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne   compute admin http://controller:8774/v2.1/%\(tenant_id\)s
```

安装计算服务组件

① 安装Nova组件

```bash
yum install openstack-nova-api openstack-nova-conductor   openstack-nova-console openstack-nova-novncproxy   openstack-nova-scheduler
```

② 修改配置文件sudo vi /etc/nova/nova.conf 。

在[DEFAULT] 处只启用compute 和metadata APIs，将

```bash
267 #enabled_apis=osapi_compute,metadata
改为
enabled_apis = osapi_compute,metadata
```

在[api_database] 和[database] 处配置数据库访问连接（若没有[api_database] 和[database] 标记，则

手动添加）

注：将NOVA_DBPASS 替换为前面设计的实际密码

```bash
[api_database]
...
connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova_api
[database]
...
connection = mysql+pymysql://nova:NOVA_DBPASS@controller/nova
```

在[DEFAULT] 和[oslo_messaging_rabbit] 处配置RabbitMQ消息队里访问

注：将RABBIT_PASS 替换为前面设计的实际密码

[DEFAULT]
...
rpc_backend = rabbit

[oslo_messaging_rabbit]
...
rabbit_host = controller
rabbit_userid = openstack

rabbit_password = RABBIT_PASS

在[DEFAULT] 和[keystone_authtoken] 处配置身份服务访问

注：将NOVA_PASS 替换为前面设计的实际密码

注：注释或删除[keystone_authtoken] 处其他内容

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

password = nova

在[DEFAULT] 处配置my_ip 为Controller节点Management Network网口地址

my_ip = 10.0.0.11

在[DEFAULT] 处启用网络服务支持

注：默认情况下，计算服务使用主机内部防火墙驱动，因此必须禁用OpenStack网络服务中的防火墙驱动。

use_neutron = True

firewall_driver = nova.virt.firewall.NoopFirewallDriver

在[vnc] 处，使用Controller节点Management Network网口地址配置VNC代理（VNC proxy）。

[vnc]
...
vncserver_listen = $my_ip

vncserver_proxyclient_address = $my_ip

在[glance] 处配置镜像服务API位置

[glance]
...

api_servers = [http://controller:9292](http://controller:9292)

在[oslo_concurrency] 处配置lock_path

[oslo_concurrency]
...

lock_path = /var/lib/nova/tmp

将配置信息写入计算服务数据库nova

```bash
# su -s /bin/sh -c "nova-manage api_db sync" nova
# su -s /bin/sh -c "nova-manage db sync" nova
```

重启计算服务

```bash
 systemctl enable openstack-nova-api.service   openstack-nova-consoleauth.service openstack-nova-scheduler.service   openstack-nova-conductor.service openstack-nova-novncproxy.service
 systemctl start openstack-nova-api.service   openstack-nova-consoleauth.service openstack-nova-scheduler.service   openstack-nova-conductor.service openstack-nova-novncproxy.service
```

部署节点：Compute Node

在Compute节点上需要安装novacompute

。

注：以下步骤在Compute节点上执行

安装配置计算服务组件

安装nova‐compute 组件

```bash
yum install openstack-nova-compute
```

修改配置文件sudo vi /etc/nova/nova.conf

① 在[DEFAULT] 和[oslo_messaging_rabbit] 处配置RabbitMQ消息队列访问

注：将RABBIT_PASS 替换为前面设计的实际密码

```bash
[DEFAULT]
...
rpc_backend = rabbit
[oslo_messaging_rabbit]
...
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = RABBIT_PASS
```

② 在[DEFAULT] 和[keystone_authtoken] 处配置身份服务访问

注：将NOVA_PASS 替换为前面设计的实际密码

注：注释或删除[keystone_authtoken] 处其他内容

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

在[DEFAULT] 处配置my_ip 为Compute节点Management Network网口地址

my_ip=10.0.0.31

在[DEFAULT] 处启用网络服务支持

```bash
[DEFAULT]
...
use_neutron = True
firewall_driver = nova.virt.firewall.NoopFirewallDriver
```

在[vnc] 处配置远程控制访问

```bash
[vnc]
...
enabled = True
vncserver_listen = 0.0.0.0
vncserver_proxyclient_address = $my_ip
novncproxy_base_url = http://controller:6080/vnc_auto.html
```

注： VNC服务器端监听所有地址，VNC代理客户端只监听Compute节点Management Network网口地址，

base URL设置Compute节点远程控制台浏览器访问地址（若浏览无法解析controller，则需替换为相应IP地

址）。

在[glance] 处配置镜像服务API

```bash
api_servers = http://controller:9292
```

在[oslo_concurrency] 处配置lock_path

```bash
lock_path = /var/lib/nova/tmp
```

完成安装，重启计算服务

① 检测是否支持虚拟机硬件加速

```bash
egrep ‐c '(vmx|svm)' /proc/cpuinfo
```

若返回结果大于等于1，则支持，无需做额外配置；

若返回结果0，则不支持硬件加速，需要做以下额外配置：修改配置文件sudo vi /etc/nova/novacompute.

conf 中的libvirt 设置项，使用QEMU 代替KVM 。

[libvirt]

virt_type = qemu

```bash
systemctl enable libvirtd.service openstack-nova-compute.service
systemctl start libvirtd.service openstack-nova-compute.service
```

验证计算服务是否安装正确

注：以下步骤需在Controller节点执行

① 设置OpenStack admin 用户环境变量

source admin-openrc

② 打印服务组件列表，验证每个成功启动和注册的进程。

```bash
[root@controller ~]# openstack compute service list
+----+-----------------+------------+----------+---------+-------+------------------+
| Id | Binary          | Host       | Zone     | Status  | State | Updated At       |
+----+-----------------+------------+----------+---------+-------+------------------+
|  1 | nova-           | controller | internal | enabled | up    | 2016-09-03T09:29 |
|    | consoleauth     |            |          |         |       | :56.000000       |
|  2 | nova-conductor  | controller | internal | enabled | up    | 2016-09-03T09:29 |
|    |                 |            |          |         |       | :56.000000       |
|  3 | nova-scheduler  | controller | internal | enabled | up    | 2016-09-03T09:29 |
|    |                 |            |          |         |       | :56.000000       |
|  7 | nova-compute    | compute    | nova     | enabled | up    | 2016-09-03T09:29 |
|    |                 |            |          |         |       | :56.000000       |
+----+-----------------+------------+----------+---------+-------+------------------+
```

---

4.5 网络服务配置（Networking Service Neutron）

部署节点：Controller Node

在MariaDB（MySQL）中创建neutron 数据库

```bash
mysql -u root -p
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost'  IDENTIFIED BY 'neutron';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%'   IDENTIFIED BY 'neutron';
```

创建网络服务证书和API路径

```bash
openstack user create --domain default --password-prompt neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron   --description "OpenStack Networking" network
openstack endpoint create --region RegionOne   network public http://controller:9696
openstack endpoint create --region RegionOne   network internal http://controller:9696
openstack endpoint create --region RegionOne   network admin http://controller:9696
```

安装配置neutron‐server 服务组件

yum install openstack-neutron openstack-neutron-ml2

修改配置文件sudo vi /etc/neutron/neutron.conf

```bash
vi /etc/neutron/neutron.conf
[database]
connection = mysql://neutron:neutron@controller/neutron
[DEFAULT] 
core_plugin = ml2
service_plugins = router
allow_overlapping_ips = True
[DEFAULT]
rpc_backend = rabbit
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = openstack
[DEFAULT]
auth_strategy = keystone
[keystone_authtoken]  
auth_uri = http://controller:5000
auth_url = http://controller:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
project_name = service
username = neutron
password = neutron
[DEFAULT]
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
[nova]
auth_url = http://controller:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
region_name = RegionOne
project_name = service
username = nova
password = nova
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
[DEFAULT]
verbose = True
```

配置ML2插件   配置LINUX桥接代理 配置元数据代理

```bash
ML2 plugin
使用Linux网桥机制为OpenStack实例建立layer2
虚拟网络设施（桥接和交换）。修改配置文件sudo vi /etc/neutron/plugins/ml2/ml2_conf.ini
vi /etc/neutron/plugins/ml2/ml2_conf.ini
[ml2]
type_drivers = flat,vlan,vxlan   #配置ML2后如果移除此项目会引起数据库不一致
[ml2]
tenant_network_types = vxlan
[ml2]
mechanism_drivers = linuxbridge,l2population
[ml2]
extension_drivers = port_security  ##启用端口安全扩展驱动
[ml2_type_flat]
flat_networks = public  ##运营商虚拟网络为flat network
[ml2_type_vxlan]
vni_ranges = 1:1000
[securitygroup]
enable_ipset = True  ##启用ipset 来增强安全组规则的效率
```

将配置信息写入neutron 数据库

```bash
su ‐s /bin/sh ‐c "neutron‐db‐manage ‐‐config‐file /etc/neutron/neutron.conf ‐‐config‐file
/etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
```

配置计算节点使用网络

```bash
vi /etc/nova/nova.conf
[neutron]
url = http://controller:9696
auth_url = http://controller1:35357
auth_plugin = password
project_domain_id = default
user_domain_id = default
region_name = RegionOne
project_name = service
username = neutron
password = neutron
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata
```

创建文件连接

ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini

重启服务

```bash
systemctl restart openstack-nova-api.service
systemctl restart neutron-server.service
systemctl  start  neutron-metadata-agent.service
systemctl enable neutron-server.service
systemctl  enable neutron-metadata-agent.service
```

**部署节点：Network Node**

在Network 节点上部署组件：

网络服务部署架构有两种方式Provider Networks 和Self‐Service Networks ，在本文开头作了简要介绍。本文采

用Self‐Service Networks 方式部署。

参考文档：Deploy Networking Service using the Architecture of SelfService

Networks

```bash
yum install  openstack-neutron-ml2   openstack-neutron-linuxbridge   ebtables
```

配置公共服务组件

公共组件配置包括认证机制、消息队列。修改配置文件sudo vi /etc/neutron/neutron.conf

```bash
[DEFAULT]
rpc_backend = rabbit
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = openstack
[DEFAULT]
auth_strategy = keystone
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = neutron
配置Linux网桥代理
Linux bridge agent为实例建立了二层虚拟网络设施，而且可以管理安全组。
修改配置文件sudo vi /etc/neutron/plugins/ml2/linuxbridge_agent.ini
vim /etc/neutron/plugins/ml2/linuxbridge_agent.ini   #注意桥接的网卡名称
[linux_bridge]
physical_interface_mappings = public:eth0
[vxlan]
enable_vxlan = True
local_ip = 10.0.0.21  #物理公共网络接口地址(controller)
l2_population = True
[agent]
prevent_arp_spoofing = True
[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
```

配置三层网络代理

L3(Layer‐3) Agent 位自服务网络提供了路由和NAT服务。

修改配置文件sudo vi /etc/neutron/l3_agent.ini ，在[DEFAULT] 处配置Linux网桥接口驱动（Linux BridgeInterface Driver）和外网网桥。

```bash
 vi /etc/neutron/l3_agent.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
external_network_bridge =   ####注： external_network_bridge 值故意空缺，这样可使多个外部网络共用一个代理。
[DEFAULT]
verbose = True
```

修改配置文件sudo vi /etc/neutron/dhcp_agent.ini ，在[DEFAULT] 处配置Linux bridge interface

driver 和Dnsmasq DHCP driver ，启用独立的metadata 使运营商网络实例可以访问虚拟网络元信息。

```bash
vi /etc/neutron/dhcp_agent.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
enable_isolated_metadata = True
[DEFAULT]
verbose = True
```

配置元数据代理

元数据代理提供一些诸如证书之类的配置信息。

修改配置文件sudo vi /etc/neutron/metadata_agent.ini ，在[DEFAULT] 处配置元数据主机和共享密钥。

注：将METADATA_SECRET 替换为前面设计的实际密码

```bash
[DEFAULT]
nova_metadata_ip = controller
metadata_proxy_shared_secret = metadata
```

```bash
systemctl start neutron-linuxbridge-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
systemctl enable neutron-linuxbridge-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
```

部署节点：Compute Node

安装网络服务组件

[root@compute ~]# yum install openstack-neutron-linuxbridge

配置公共组件

公共组件配置包括认证机制、消息队列、插件。

```bash
[root@compute ~]# cat /etc/neutron/neutron.conf
[DEFAULT]
rpc_backend = rabbit
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = openstack
[DEFAULT]
auth_strategy = keystone
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = neutron
```

配置网络设置

配置Linux网桥代理，修改配置文件sudo vi /etc/neutron/plugins/ml2/linuxbridge_agent.ini

```bash
[root@compute ~]# cat   /etc/neutron/plugins/ml2/linuxbridge_agent.ini
[linux_bridge]
physical_interface_mappings = provider:eth0
[vxlan]
enable_vxlan = True
local_ip = 10.0.0.31
l2_population = True
[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
```

配置计算服务访问网络

修改配置文件sudo vi /etc/nova/nova.conf

```bash
[root@compute ~]# vi /etc/nova/nova.conf
[neutron]
url = http://controller:9696
auth_url = http://controller:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = neutron
```

重启服务

```bash
 systemctl  restart openstack-nova-compute.service
systemctl restart neutron-linuxbridge-agent.service
systemctl enable  neutron-linuxbridge-agent.service
```

验证

```bash
[root@controller ~]# neutron  ext-list
[root@controller ~]# neutron  agent-list                   
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host       | availability_zone | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
| 0e1c9f6f-a56b-40d1-b43e-91754cabcf75 | Metadata agent     | network    |                   | :-)   | True           | neutron-metadata-agent    |
| 24c8daec-b495-48ba-b70d-f7d103c8cda1 | Linux bridge agent | compute    |                   | :-)   | True           | neutron-linuxbridge-agent |
| 2e93bf03-e095-444d-8f74-0b832db4a0be | Linux bridge agent | network    |                   | :-)   | True           | neutron-linuxbridge-agent |
| 456c754a-d2c0-4ce5-8d9b-b0089fb77647 | Metadata agent     | controller |                   | :-)   | True           | neutron-metadata-agent    |
| 8a1c7895-fc44-407f-b74b-55bb1b4519d8 | DHCP agent         | network    | nova              | :-)   | True           | neutron-dhcp-agent        |
| 93ad18bf-d961-4d00-982c-6c617dbc0a5e | L3 agent           | network    | nova              | :-)   | True           | neutron-l3-agent          |
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
```

---

4.6 仪表盘服务配置（Dashboard Service Horizon）

仪表盘是一个Web接口，可使云管理员和用户管理各种各样的OpenStack资源和服务。本文采用Apache Web

Server 部署Dashboard 服务。

部署节点：Controller Node

```bash
yum install openstack-dashboard
```

修改配置文件sudo vim /etc/openstack‐dashboard/local_settings

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
    "p_w_picpath": 2,
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

systemctl restart httpd.service memcached.service
