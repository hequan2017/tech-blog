---
title: "openstack学习笔记五 多节点部署之 rabbitmq信息中枢与元数据"
date: "2016-07-05 18:01:09"
category: "openstack"
source: "https://blog.51cto.com/hequan/1796041"
---
> **内容介绍**
>
> 本文是多节点 OpenStack 部署笔记的两部分：第一部分介绍消息中枢 RabbitMQ——OpenStack 各组件间通过 AMQP 高级消息队列通信（也可选 qpid），在 h3（192.168.1.203）上配置本地 yum 源安装 rabbitmq-server，启动后确认 5672 端口监听，并启用 rabbitmq_management 插件通过 15672 端口的 Web 界面管理；第二部分讲元数据（metadata），包括检查控制节点 OVS 网桥与 ip_forward 转发，在计算节点 nova.conf 中配置 metadata_host 指向控制节点，最后在云主机内通过 `curl http://169.254.169.254/` 查看实例元数据。

> **技术备注**
>
> RabbitMQ 作为 OpenStack 默认消息队列至今未变，但新版配置项已从 `rabbit_host` 等旧写法统一为 `[oslo_messaging_rabbit]` 下的 `transport_url = rabbit://user:pass@host:5672/`；guest/guest 默认账号仅限 localhost 登录，生产环境必须新建专用账号。元数据服务 169.254.169.254 的机制沿用至今（AWS 也相同），现版本还推荐使用 config-drive 或 IMDSv2 风格的安全增强。

---

## 1. RabbitMQ 信息中枢

所有组件通信的时候使用 AMQP 高级消息队列协议，可选实现有 qpid 和 RabbitMQ（OpenStack 默认用 RabbitMQ）。

- RabbitMQ 端口：5672
- SSL 加密端口：5671

节点规划：

```text
192.168.1.201            h1
192.168.1.202            h2
192.168.1.203            h3
```

### 1.1 在 h3 上安装 RabbitMQ

在 h3 上配置 yum 源，把 OpenStack 软件包上传到 openstack 目录下：

```ini
# /etc/yum.repos.d/openstack.repo
[openstack]
name=openstack
baseurl=file:///openstack
enabled=1
gpgcheck=0
```

```shell
yum clean all
yum makecache
[root@h3 yum.repos.d]# yum install -y rabbitmq-server.noarch
```

### 1.2 启动并确认端口

```shell
[root@h3 ~]# systemctl start rabbitmq-server.service
[root@h3 ~]# systemctl enable rabbitmq-server.service
[root@h3 ~]# netstat -lntup | grep 5672
tcp        0      0 0.0.0.0:25672           0.0.0.0:*               LISTEN      1354/beam.smp
tcp6       0      0 :::5672                 :::*                    LISTEN      1354/beam.smp   # 客户端使用这个端口
```

keystone.conf 中 rabbit 相关默认配置（各组件通过它连接消息队列）：

```shell
[root@h1 keystone]# egrep -v '^$|^#' keystone.conf | grep rabbit
[oslo_messaging_rabbit]
rabbit_host = localhost
rabbit_port = 5672
rabbit_hosts = localhost:5672
rabbit_use_ssl = False
rabbit_userid = guest    # 默认用户
rabbit_password = guest
rabbit_virtual_host = /
rabbit_ha_queues = False
```

RabbitMQ 自身的配置文件：

```shell
[root@h3 ~]# cd /etc/rabbitmq/
[root@h3 rabbitmq]# ls
rabbitmq.config            # 配置文件
[root@h3 rabbitmq]# cat rabbitmq-env.conf
NODE_PORT=5672
```

### 1.3 启用 Web 管理插件

```shell
[root@h3 rabbitmq]# rabbitmq-plugins list    # 查看插件
[root@h3 rabbitmq]# rabbitmq-plugins enable rabbitmq_management   # 启用管理插件
The following plugins have been enabled:
  mochiweb
  webmachine
  rabbitmq_web_dispatch
  amqp_client
  rabbitmq_management_agent
  rabbitmq_management
Plugin configuration has changed. Restart RabbitMQ for changes to take effect.
[root@h3 rabbitmq]# systemctl restart rabbitmq-server.service
[root@h3 rabbitmq]# netstat -lntup | grep 15672
tcp        0      0 0.0.0.0:15672   0.0.0.0:*               LISTEN      1976/beam.smp
```

浏览器访问 `http://192.168.1.203:15672/`，用户名 guest，密码 guest：

![RabbitMQ Web 管理界面登录页](assets/1796041/01_wKioL1d7hRPh4w6AAAAShd6x7Zw822.png)

## 2. 元数据（metadata）

### 2.1 检查控制节点网络

查看控制节点网卡/OVS 网桥设置是否有问题，并确认开启了转发功能：

```shell
[root@h1 ~]# ovs-vsctl show
c34056d1-7b80-437f-b73c-5bf05258d303
    Bridge br-ex
        Port "qg-c4dff563-63"
            Interface "qg-c4dff563-63"
                type: internal
        Port "qg-62a3088b-40"
            Interface "qg-62a3088b-40"
                type: internal
        Port "qg-df2db69c-60"
            Interface "qg-df2db69c-60"
                type: internal
        Port "eth0"
            Interface "eth0"
        Port br-ex
            Interface br-ex
                type: internal
[root@h1 ~]# cat /proc/sys/net/ipv4/ip_forward    # 转发功能
1
```

![元数据服务网络路径示意图一](assets/1796041/02_wKiom1d7hSXwj1mVAAAQLlKyWX4805.png)

![元数据服务网络路径示意图二](assets/1796041/03_wKioL1d7hSbTug-WAAGDLh0x_JY828.png)

### 2.2 计算节点配置 metadata_host

```shell
[root@h2 ~]# cd /etc/nova/
[root@h2 nova]# grep metadata nova.conf
#  Number of metadata items allowed per instance (integer value)
#quota_metadata_items=128
#enabled_apis=ec2,osapi_compute,metadata
#  OpenStack metadata service manager (string value)
#metadata_manager=nova.api.manager.MetadataManager
#  The IP address on which the metadata API will listen. (string value)
#metadata_listen=0.0.0.0
#  The port on which the metadata API will listen. (integer value)
#metadata_listen_port=8775
#  Number of workers for metadata service. The default will be the number of
#metadata_workers=<None>
#  List of metadata versions to skip placing into the config drive (string
#vendordata_driver=nova.api.metadata.vendordata_json.JsonFileVendorData
#  Time in seconds to cache metadata; 0 to disable metadata caching entirely
#  metadata API when under heavy load. Higher values may increase memory usage
#  and result in longer times for host metadata changes to take effect. (integer
#metadata_cache_expiration=15
#  The IP address for the metadata API server (string value)
#metadata_host=$my_ip
metadata_host=192.168.1.201                 # 指向控制节点
#  The port for the metadata API port (integer value)
#metadata_port=8775
#  Set flag to indicate Neutron will proxy metadata requests and resolve
#service_metadata_proxy=false
#  Shared secret to validate proxies Neutron metadata requests (string value)
#metadata_proxy_shared_secret =
```

### 2.3 在云主机内查看元数据

登录实例云主机，可以查看 metadata 服务提供的数据：

```shell
curl http://169.254.169.254/2009-04-04/meta-data/
hostname
local-ipv4
public-ipv4
security-groups    # 安全组
```
