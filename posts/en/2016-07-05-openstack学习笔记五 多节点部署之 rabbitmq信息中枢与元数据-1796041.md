---
title: "OpenStack Study Notes (Part 5): RabbitMQ Message Hub and Metadata in a Multi-Node Deployment"
date: "2016-07-05 18:01:09"
category: "openstack"
source: "https://blog.51cto.com/hequan/1796041"
lang: "en"
---
> **About this post**
>
> This post covers two parts of my multi-node OpenStack deployment notes. Part one introduces RabbitMQ, the message hub: OpenStack components communicate with one another over AMQP, the Advanced Message Queuing Protocol (qpid is another option). On h3 (192.168.1.203) we configure a local yum repository to install rabbitmq-server, confirm that port 5672 is listening after startup, and enable the rabbitmq_management plugin so the service can be managed through the web UI on port 15672. Part two covers metadata (metadata): checking the controller node's OVS bridge and ip_forward forwarding, setting metadata_host in the compute node's nova.conf to point at the controller node, and finally querying instance metadata from inside a cloud host with `curl http://169.254.169.254/`.

> **Technical notes**
>
> RabbitMQ is still OpenStack's default message queue today, but the configuration options have changed: the old style such as `rabbit_host` has been unified into `transport_url = rabbit://user:pass@host:5672/` under `[oslo_messaging_rabbit]`. The default guest/guest account can only log in from localhost; production environments must create a dedicated account. The metadata service at 169.254.169.254 works the same way today (AWS uses the same address), and current versions additionally recommend security enhancements such as config-drive or IMDSv2-style hardening.

---

## 1. RabbitMQ Message Hub

All components communicate using AMQP, the Advanced Message Queuing Protocol. Optional implementations include qpid and RabbitMQ (OpenStack uses RabbitMQ by default).

- RabbitMQ port: 5672
- SSL encrypted port: 5671

Node plan:

```text
192.168.1.201            h1
192.168.1.202            h2
192.168.1.203            h3
```

### 1.1 Install RabbitMQ on h3

Configure a yum repository on h3 and upload the OpenStack packages into the openstack directory:

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

### 1.2 Start the Service and Verify the Port

```shell
[root@h3 ~]# systemctl start rabbitmq-server.service
[root@h3 ~]# systemctl enable rabbitmq-server.service
[root@h3 ~]# netstat -lntup | grep 5672
tcp        0      0 0.0.0.0:25672           0.0.0.0:*               LISTEN      1354/beam.smp
tcp6       0      0 :::5672                 :::*                    LISTEN      1354/beam.smp   # port used by clients
```

Default rabbit-related settings in keystone.conf (each component uses them to connect to the message queue):

```shell
[root@h1 keystone]# egrep -v '^$|^#' keystone.conf | grep rabbit
[oslo_messaging_rabbit]
rabbit_host = localhost
rabbit_port = 5672
rabbit_hosts = localhost:5672
rabbit_use_ssl = False
rabbit_userid = guest    # default user
rabbit_password = guest
rabbit_virtual_host = /
rabbit_ha_queues = False
```

RabbitMQ's own configuration files:

```shell
[root@h3 ~]# cd /etc/rabbitmq/
[root@h3 rabbitmq]# ls
rabbitmq.config            # configuration file
[root@h3 rabbitmq]# cat rabbitmq-env.conf
NODE_PORT=5672
```

### 1.3 Enable the Web Management Plugin

```shell
[root@h3 rabbitmq]# rabbitmq-plugins list    # list plugins
[root@h3 rabbitmq]# rabbitmq-plugins enable rabbitmq_management   # enable the management plugin
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

Open `http://192.168.1.203:15672/` in a browser and log in with username guest and password guest:

![RabbitMQ web management login page](../assets/1796041/01_wKioL1d7hRPh4w6AAAAShd6x7Zw822.png)

## 2. Metadata

### 2.1 Check the Controller Node's Network

Check whether the controller node's NIC/OVS bridge settings have any problems, and confirm that forwarding is enabled:

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
[root@h1 ~]# cat /proc/sys/net/ipv4/ip_forward    # IP forwarding
1
```

![Instance list of the cloud hosts: IP and floating IP of centos7](../assets/1796041/02_wKiom1d7hSXwj1mVAAAQLlKyWX4805.png)

![Hand-drawn diagram: metadata is associated from the controller node to the compute node's configuration file](../assets/1796041/03_wKioL1d7hSbTug-WAAGDLh0x_JY828.png)

### 2.2 Configure metadata_host on the Compute Node

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
metadata_host=192.168.1.201                 # points to the controller node
#  The port for the metadata API port (integer value)
#metadata_port=8775
#  Set flag to indicate Neutron will proxy metadata requests and resolve
#service_metadata_proxy=false
#  Shared secret to validate proxies Neutron metadata requests (string value)
#metadata_proxy_shared_secret =
```

### 2.3 View Metadata from Inside the Instance

Log in to the instance (cloud host) to view the data provided by the metadata service:

```shell
curl http://169.254.169.254/2009-04-04/meta-data/
hostname
local-ipv4
public-ipv4
security-groups    # security groups
```
