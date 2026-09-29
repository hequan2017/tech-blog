---
title: "OpenStack Deployment in Practice, 2nd Edition: Open vSwitch"
date: "2016-07-25 21:59:47"
category: "openstack"
source: "https://blog.51cto.com/hequan/1829871"
lang: "en"
---
> **About this post**
>
> This post is an excerpt from the lab manual of OpenStack Deployment in Practice, 2nd Edition; the environment is Alibaba Cloud CentOS 7.2. It has three parts. First, building Open vSwitch 2.5.0 from source: download the source tarball as the regular user ovswitch, strip the kmod dependency from the spec with sed, build the RPM with rpmbuild, then install and start the service. Second, hands-on bridging: stop NetworkManager, create bridge br0 and add eth1 as a port, then rewrite ifcfg-eth1 (OVSPort) and ifcfg-br0 (OVSBridge) to move the IP onto the bridge; after restarting the network, external connectivity still works. Third, a preview of the VXLAN experiment, demonstrating how to add a type=vxlan tunnel port to br0 with remote_ip pointing at the peer.

> **Technical notes**
>
> Open vSwitch 2.5.0 is long obsolete (the mainstream in 2026 is 3.x LTS); on newer CentOS/Rocky you can simply run `dnf install openvswitch` — no need to build RPMs from source. The chkconfig and ifcfg script system has likewise been superseded by systemd and NetworkManager keyfiles; OVS bridges can be configured with the `nmcli connection add type ovs-bridge` family of commands. The VXLAN tunnel syntax shown here is still valid today, but in production it is mostly managed automatically by Neutron/OVN, so manual ovs-vsctl is rarely necessary.

---

## 1. Build and Install Open vSwitch 2.5.0 from Source

Lab environment:

```shell
[root@hequan ~]# uname -r
3.10.0-327.22.2.el7.x86_64
[root@hequan ~]# cat /etc/redhat-release
CentOS Linux release 7.2.1511 (Core)
```

Install the build dependencies, then build the RPM as a regular user (dropping the kmod kernel module dependency so the datapath built into the system kernel is used directly):

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

## 2. Hands-On Bridging: Attaching eth1 to br0

First stop NetworkManager (it conflicts with OVS bridges), create the bridge, and add the physical port:

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

### Before the change

```shell
[root@hequan ~]# cat /etc/sysconfig/network-scripts/ifcfg-eth1
DEVICE=eth1
ONBOOT=yes
BOOTPROTO=static
IPADDR=115.29.107.17
NETMASK=255.255.252.0
```

### After the change

eth1 becomes an OVS port and the IP moves onto br0:

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

Restart the network and OVS:

```shell
[root@hequan ~]# systemctl restart network.service
[root@hequan ~]# systemctl restart openvswitch.service    # after the restart, the host is reachable over the external network again
```

The configuration still takes effect after the restart.

## 3. VXLAN Tunnel (to be tested)

VXLAN (Virtual Extensible LAN), as the name suggests, is an extended version of VLAN, mainly used to boost network scalability in cloud computing environments (VLAN offers only 4096 IDs, while VXLAN offers 16 million VNIs).

Add a VXLAN tunnel port to br0 with remote_ip pointing at the peer host:

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
