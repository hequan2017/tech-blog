---
title: "openstack部署实战第2版之Open vSwitch"
date: "2016-07-25 21:59:47"
category: "openstack"
source: "https://blog.51cto.com/hequan/1829871"
---
> **内容介绍**
>
> 本文是《OpenStack 部署实战第 2 版》的实验手册节选，环境为阿里云 CentOS 7.2。内容分三部分：一是从源码构建 Open vSwitch 2.5.0——以普通用户 ovswitch 下载源码、用 sed 去掉 spec 里的 kmod 依赖后 rpmbuild 打 RPM 包再安装启动；二是网桥实操——停掉 NetworkManager，创建 br0 网桥并把 eth1 加为端口，再改写 ifcfg-eth1（OVSPort）与 ifcfg-br0（OVSBridge）把 IP 迁移到网桥上，重启网络后外网仍通；三是预告 VXLAN 实验，演示给 br0 添加一个 type=vxlan、remote_ip 指向对端的隧道端口。

> **技术备注**
>
> Open vSwitch 2.5.0 早已过时（2026 年主流为 3.x LTS），新版 CentOS/Rocky 可直接 `dnf install openvswitch`，无需源码打 RPM；chkconfig 与 ifcfg 脚本体系也已被 systemd、NetworkManager keyfile 取代，配置 OVS 网桥可用 `nmcli connection add type ovs-bridge` 系列命令。VXLAN 隧道的写法至今通用，但生产环境多由 Neutron/OVN 自动管理，不必手工 ovs-vsctl。

---

## 1. 源码构建安装 Open vSwitch 2.5.0

实验环境：

```shell
[root@hequan ~]# uname -r
3.10.0-327.22.2.el7.x86_64
[root@hequan ~]# cat /etc/redhat-release
CentOS Linux release 7.2.1511 (Core)
```

安装编译依赖，以普通用户构建 RPM（去掉 kmod 内核模块依赖，直接使用系统内核自带的 datapath）：

```shell
yum -y install wget openssl-devel kernel-devel
yum groupinstall "Development Tools"
[root@hequan ~]# adduser ovswitch
[root@hequan ~]# su - ovswitch
[ovswitch@hequan ~]$ wget http://openvswitch.org/releases/openvswitch-2.5.0.tar.gz
[ovswitch@hequan ~]$ tar zxvf openvswitch-2.5.0.tar.gz
[ovswitch@hequan ~]$ mkdir -p ~/rpmbuild/SOURCES
[ovswitch@hequan ~]$ sed 's/openvswitch-kmod, //g' openvswitch-2.5.0/rhel/openvswitch.spec > openvswitch-2.5.0/rhel/openvswitch_no_kmod.spec
[ovswitch@hequan ~]$ cp openvswitch-2.5.0.tar.gz rpmbuild/SOURCES/
[ovswitch@hequan ~]$ rpmbuild -bb --without check ~/openvswitch-2.5.0/rhel/openvswitch_no_kmod.spec
[ovswitch@hequan ~]$ exit
[root@hequan ~]# yum localinstall /home/ovswitch/rpmbuild/RPMS/x86_64/openvswitch-2.5.0-1.x86_64.rpm
[root@hequan ~]# systemctl start openvswitch.service
[root@hequan ~]# systemctl status openvswitch.service -l
[root@hequan ~]# systemctl enable openvswitch.service
```

## 2. 网桥实操：把 eth1 桥接到 br0

先停掉 NetworkManager（与 OVS 网桥冲突），创建网桥并添加物理端口：

```shell
systemctl stop NetworkManager.service
systemctl disable NetworkManager.service
ovs-vsctl add-br br0
ovs-vsctl add-port br0 eth1
ovs-vsctl show
d8fb371e-5b17-40af-a358-9a207b4e44e0
    Bridge "br0"
        Port "br0"
            Interface "br0"
                type: internal
        Port "eth1"
            Interface "eth1"
    ovs_version: "2.5.0"
```

### 修改前

```shell
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-eth1
DEVICE=eth1
ONBOOT=yes
BOOTPROTO=static
IPADDR=115.29.107.17
NETMASK=255.255.252.0
```

### 修改后

eth1 改为 OVS 端口，IP 移到 br0 上：

```shell
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-eth1
DEVICE=eth1
DEVICETYPE=ovs
TYPE=OVSPort
OVS_BRIDGE=br0
ONBOOT=yes
BOOTPROTO=none
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-br0
DEVICE=br0
DEVICETYPE=ovs
TYPE=OVSBridge
ONBOOT=yes
BOOTPROTO=none
IPADDR=115.29.107.17
NETMASK=255.255.252.0
```

重启网络与 OVS：

```shell
[root@hequan ~]# systemctl restart network.service
[root@hequan ~]# systemctl restart openvswitch.service    # 重启后可以用外网连接了
```

重启后配置仍然生效。

## 3. VXLAN 隧道（待测试）

VXLAN（Virtual Extensible LAN）顾名思义是 VLAN 的扩展版本，主要用来增强云计算环境下网络的扩展能力（VLAN 只有 4096 个 ID，VXLAN 有 1600 万个 VNI）。

给 br0 添加一个 VXLAN 隧道端口，remote_ip 指向对端主机：

```shell
[root@lamp ~]# ovs-vsctl add-port br0 vx1 -- set interface vx1 type=vxlan options:remote_ip=192.168.10.12
[root@lamp ~]# ovs-vsctl show
1bb23a58-98a5-479e-bc4a-7638aeb8408d
    Bridge "br0"
        Port "br0"
            Interface "br0"
                type: internal
        Port "eth0"
            Interface "eth0"
        Port "vx1"
            Interface "vx1"
                type: vxlan
                options: {remote_ip="192.168.10.12"}
    ovs_version: "2.5.0"
```
