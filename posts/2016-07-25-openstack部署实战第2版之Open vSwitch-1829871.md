---
title: "openstack部署实战第2版之Open vSwitch"
date: "2016-07-25 21:59:47"
category: "openstack"
source: "https://blog.51cto.com/hequan/1829871"
---

本文是openstack部署实战第2版的实验手册，环境是阿里云上的，系统用得是centos7.2。

Open vSwitch    开放的软件虚拟机交换机

安装步骤

```bash
[root@hequan ~]# uname -r
3.10.0-327.22.2.el7.x86_64
[root@hequan ~]# cat /etc/redhat-release
CentOS Linux release 7.2.1511 (Core)
yum -y install wget openssl-devel kernel-devel
yum groupinstall "Development Tools"
[root@hequan ~]# adduser ovswitch
[root@hequan ~]# su - ovswitch
[ovswitch@hequan ~]$  wget http://openvswitch.org/releases/openvswitch-2.5.0.tar.gz
[ovswitch@hequan ~]$ tar zxvf openvswitch-2.5.0.tar.gz
[ovswitch@hequan ~]$ mkdir -p ~/rpmbuild/SOURCES
[ovswitch@hequan ~]$ sed 's/openvswitch-kmod, //g' openvswitch-2.5.0/rhel/openvswitch.spec > openvswitch-2.5.0/rhel/openvswitch_no_kmod.spec
[ovswitch@hequan ~]$ cp openvswitch-2.5.0.tar.gz  rpmbuild/SOURCES/
[ovswitch@hequan ~]$ rpmbuild -bb --without check ~/openvswitch-2.5.0/rhel/openvswitch_no_kmod.spec
[ovswitch@hequan ~]$ exit
[root@hequan ~]# yum localinstall /home/ovswitch/rpmbuild/RPMS/x86_64/openvswitch-2.5.0-1.x86_64.rpm
[root@hequan ~]# systemctl  start openvswitch.service
[root@hequan ~]# systemctl  status openvswitch.service -l
[root@hequan ~]# chkconfig  openvswitch  on
```

---

测试网桥

```bash
systemctl stop NetworkManager.service
systemctl disable NetworkManager.service
ovs-vsctl add-br  br0
ovs-vsctl add-port br0 eth1
ovs-vsctl show
d8fb371e-5b17-40af-a358-9a207b4e44e0
    Bridge "br0"
        Port "br0"
            Interface "br0"
                type: internal
        Port "eth1"
            Interface "eth1"
    ovs_version: "2.5.0"
```

##修改前

```bash
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-eth1  
DEVICE=eth1
ONBOOT=yes
BOOTPROTO=static
IPADDR=115.29.107.17
NETMASK=255.255.252.0
```

##修改后

```bash
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-eth1  
DEVICE=eth1
DEVICETYPE=ovs
TYPE=OVSPort
OVS_BRIDGE=br0
ONBOOT=yes
BOOTPROTO=nono
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-br0
DEVICE=br0
DEVICETYPE=ovs
TYPE=OVSBridge
ONBOOT=yes
BOOTPROTO=none
IPADDR=115.29.107.17
NETMASK=255.255.252.0
```

重启

```bash
[root@hequan ~]# systemctl restart network.service 
[root@hequan ~]# /etc/init.d/openvswitch restart    ##可以用外网连接了
```

重启后，还是可以生效的

---

VXLAN，Virtual Extensible LAN，顾名思义，是VLAN的扩展版本。VXLAN技术主要用来增强在云计算环境下网络的扩展能力。

待测试

```bash
[root@lamp ~]# ovs-vsctl  add-port  br0  vx1 -- set interface vx1 type=vxlan   options:remote_ip=192.168.10.12
[root@lamp ~]# ovs-vsctl show
1bb23a58-98a5-479e-bc4a-7638aeb8408d
    Bridge "br0"
        Port "br0"
            Interface "br0"
                type: internal
        Port "eth0"
            Interface "eth0"
        Port "vx1"
            Interface "vx1"
                type: vxlan
                options: {remote_ip="192.168.10.12"}
    ovs_version: "2.5.0"
```
