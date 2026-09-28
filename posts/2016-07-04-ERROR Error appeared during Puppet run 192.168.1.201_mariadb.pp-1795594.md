---
title: "ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp"
date: "2016-07-04 14:44:50"
category: "openstack"
source: "https://blog.51cto.com/hequan/1795594"
---
> **内容介绍**
>
> 本文是OpenStack 私有云部署与运维笔记,记录了「ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp」的相关内容。主要涉及:RDO模式安装报错 怀疑是软件问题，查看 一个是5.5.44 一个是5.5.47…

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

RDO模式安装报错

```bas
h
ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp
Error: Execution of '/usr/bin/yum -d 0 -e 0 -y install mariadb' returned 1: Error: Package: 1:mariadb-5.5.44-2.el7.centos.x86_64 (dvd)
You will find full trace in log /var/tmp/packstack/20160704-142958-_jXSqZ/manifests/192.168.1.201_mariadb.pp.log
```

怀疑是软件问题，查看

```bas
h
[root@h1 ~]# yum -d 0 -e 0 -y install mariadb-5.5.44-2.el7.centos.x86_64
错误：软件包：1:mariadb-5.5.44-2.el7.centos.x86_64 (dvd)
          需要：mariadb-libs(x86-64) = 1:5.5.44-2.el7.centos
          已安装: 1:mariadb-libs-5.5.47-1.el7_2.x86_64 (@updates)
              mariadb-libs(x86-64) = 1:5.5.47-1.el7_2
          可用: 1:mariadb-libs-5.5.44-2.el7.centos.x86_64 (dvd)
              mariadb-libs(x86-64) = 1:5.5.44-2.el7.centos
 您可以尝试添加 --skip-broken 选项来解决该问题
 您可以尝试执行：rpm -Va --nofiles --nodigest
```

一个是5.5.44  一个是5.5.47

```bas
h
[root@h1 Packages]# rpm -e --nodeps mariadb-libs-5.5.47-1.el7_2.x86_64
[root@h1 Packages]# rpm -qa mariadb-libs                              
[root@h1 Packages]# rpm -ivh mariadb-libs-5.5.44-2.el7.centos.x86_64.rpm
准备中...                          ################################# [100%]
正在升级/安装...
   1:mariadb-libs-1:5.5.44-2.el7.cento################################# [100%]
[root@h1 Packages]# rpm -qa mariadb-libs                              
mariadb-libs-5.5.44-2.el7.centos.x86_64
```

重新测试，

正常过

最好是用centos源，防止安装包出问题
