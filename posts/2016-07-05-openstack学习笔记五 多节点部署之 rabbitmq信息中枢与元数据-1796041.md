---
title: "openstack学习笔记五 多节点部署之 rabbitmq信息中枢与元数据"
date: "2016-07-05 18:01:09"
category: "openstack"
source: "https://blog.51cto.com/hequan/1796041"
---
> **内容介绍**
>
> 本文是OpenStack 私有云部署与运维笔记,记录了「openstack学习笔记五 多节点部署之 rabbitmq信息中枢与元数据」的相关内容。主要涉及:- 元数据 - **rabbitmq信息中枢** ---…

> **技术备注**
>
> OpenStack 各版本迭代较快,部署时请以官方文档对应版本为准;生产中也可考虑 Kolla-Ansible 等容器化部署方案。

---

- 元数据
- **rabbitmq信息中枢**

---

**rabbitmq信息中枢**

所有组件通信的时候 实用 AMQP 高级消息队列

qpid

rabbitmq    端口5672       sll加密 5671

```bash
192.168.1.201            h1
192.168.1.202            h2
192.168.1.203            h3
```

在h3上操作  配置YUM源   把openstack软件包上传到openstack目录下

```bash
[openstack]
name=openstack
baseurl=file:///openstack
enabled=1
gpgcheck=0
yum clean all
yum makecache
[root@h1 yum.repos.d]# yum  install -y rabbitmq-server.noarch
```

```bash
[root@h3 ~]# systemctl   start rabbitmq-server.service
[root@h3 ~]# systemctl   enable rabbitmq-server.service      
 [root@h3 ~]# netstat -lntup | grep  5672
tcp        0      0 0.0.0.0:25672           0.0.0.0:*               LISTEN      1354/beam.smp       
tcp6       0      0 :::5672                 :::*                    LISTEN      1354/beam.smp  #使用这个
```

```bash
[root@h1 keystone]# egrep  -v  '^$|^#'  keystone.conf  | grep rabbit
[oslo_messaging_rabbit]
rabbit_host = localhost
rabbit_port = 5672
rabbit_hosts = localhost:5672
rabbit_use_ssl = False
rabbit_userid = guest    #默认用户
rabbit_password = guest
rabbit_virtual_host = /
rabbit_ha_queues = False
[root@h3 ~]# cd /etc/rabbitmq/
[root@h3 rabbitmq]# ls
rabbitmq.config             ##配置文件
[root@h1 rabbitmq]# cat rabbitmq-env.conf
NODE_PORT=5672
```

可以用web管理

```bash
[root@h3 rabbitmq]# rabbitmq-plugins  list   ##查看插件
[root@h3 rabbitmq]# rabbitmq-plugins   enable   rabbitmq_management  ##启用管理插件
The following plugins have been enabled:
  mochiweb
  webmachine
  rabbitmq_web_dispatch
  amqp_client
  rabbitmq_management_agent
  rabbitmq_management
Plugin configuration has changed. Restart RabbitMQ for changes to take effect.
[root@h3 rabbitmq]# systemctl  restart rabbitmq-server.service
[root@h3 rabbitmq]# netstat -lntup | grep 15672
tcp        0      0 0.0.0.0:15672     0.0.0.0:*               LISTEN      1976/beam.smp
```

http://192.168.1.203:15672/              用户guest  密码guest

[![openstack学习笔记五 多节点部署之 rabbitmq信息中枢与元数据_信息](assets/1796041/01_wKioL1d7hRPh4w6AAAAShd6x7Zw822.png)](http://s4.51cto.com/wyfs02/M00/83/C3/wKioL1d7hRPh4w6AAAAShd6x7Zw822.png)

---

**元数据**  metadata

查看控制节点 网卡设置是否有问题

```bash
[root@h1 ~]# ovs-vsctl show
c34056d1-7b80-437f-b73c-5bf05258d303
    Bridge br-ex
        Port "qg-c4dff563-63"
            Interface "qg-c4dff563-63"
                type: internal
        Port "qg-62a3088b-40"
            Interface "qg-62a3088b-40"
                type: internal
        Port "qg-df2db69c-60"
            Interface "qg-df2db69c-60"
                type: internal
        Port "eth0"
            Interface "eth0"
        Port br-ex
            Interface br-ex
                type: internal
[root@h1 ~]# cat /proc/sys/net/ipv4/ip_forward           ##转发功能
1
```

[![openstack学习笔记五 多节点部署之 rabbitmq信息中枢与元数据_信息_02](assets/1796041/02_wKiom1d7hSXwj1mVAAAQLlKyWX4805.png)](http://s5.51cto.com/wyfs02/M01/83/C4/wKiom1d7hSXwj1mVAAAQLlKyWX4805.png)

[![openstack学习笔记五 多节点部署之 rabbitmq信息中枢与元数据_中枢_03](assets/1796041/03_wKioL1d7hSbTug-WAAGDLh0x_JY828.png)](http://s5.51cto.com/wyfs02/M02/83/C3/wKioL1d7hSbTug-WAAGDLh0x_JY828.png)

```bash
[root@h2 ~]# cd /etc/nova/
[root@h2 nova]# grep metadata nova.conf
# Number of metadata items allowed per instance (integer value)
#quota_metadata_items=128
#enabled_apis=ec2,osapi_compute,metadata
# OpenStack metadata service manager (string value)
#metadata_manager=nova.api.manager.MetadataManager
# The IP address on which the metadata API will listen. (string value)
#metadata_listen=0.0.0.0
# The port on which the metadata API will listen. (integer value)
#metadata_listen_port=8775
# Number of workers for metadata service. The default will be the number of
#metadata_workers=<None>
# List of metadata versions to skip placing into the config drive (string
#vendordata_driver=nova.api.metadata.vendordata_json.JsonFileVendorData
# Time in seconds to cache metadata; 0 to disable metadata caching entirely
# metadata API when under heavy load. Higher values may increase memoryusage
# and result in longer times for host metadata changes to take effect. (integer
#metadata_cache_expiration=15
# The IP address for the metadata API server (string value)
#metadata_host=$my_ip
metadata_host=192.168.1.201                 ################主机
# The port for the metadata API port (integer value)
#metadata_port=8775
# Set flag to indicate Neutron will proxy metadata requests and resolve
#service_metadata_proxy=false
# Shared secret to validate proxies Neutron metadata requests (string value)
#metadata_proxy_shared_secret =
```

实例云主机

可以查看metadate的设置数据

```bash
curl  htt://169.254.169.254/2009-04-04/meta-data/
hostname        
local-ipv4
public-ipv4
seruity-groups   安全组
```
