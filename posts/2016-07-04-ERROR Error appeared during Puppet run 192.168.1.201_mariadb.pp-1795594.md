---
title: "ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp"
date: "2016-07-04 14:44:50"
category: "openstack"
source: "https://blog.51cto.com/hequan/1795594"
---
> **内容介绍**
>
> 用 packstack（RDO 模式）安装 OpenStack 时，Puppet 在部署 mariadb 这一步报错退出。排查发现原因是 yum 本地源（DVD 光盘）里的 mariadb 是 5.5.44，而系统此前通过 updates 源已经装过更高版本的 mariadb-libs 5.5.47，两者版本不一致导致依赖冲突。解决办法是卸载高版本 mariadb-libs、换装与 DVD 源一致的 5.5.44 版本后重新安装。

> **技术备注**
>
> MariaDB 5.5 已于 2020 年 4 月 EOL，CentOS 7 本身也已于 2024 年 6 月 EOL，packstack/RDO 方式在 2026 年基本只用于教学演示。现今部署 OpenStack 主流方案是 Kolla-Ansible 或 OpenStack-Ansible（基于容器/虚拟环境隔离，不会再遇到这类系统 RPM 版本冲突）；若仍在 EL 系系统上装 MariaDB，应使用 dnf 并启用官方 MariaDB 仓库（如 10.11 LTS）。

---

## 1. 报错现象

RDO（packstack）模式安装 OpenStack，执行到数据库节点时报错：

```shell
ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp
Error: Execution of '/usr/bin/yum -d 0 -e 0 -y install mariadb' returned 1: Error: Package: 1:mariadb-5.5.44-2.el7.centos.x86_64 (dvd)
You will find full trace in log /var/tmp/packstack/20160704-142958-_jXSqZ/manifests/192.168.1.201_mariadb.pp.log
```

## 2. 排查：版本不一致导致依赖冲突

怀疑是安装包问题，手动执行 yum 安装指定版本验证：

```shell
[root@h1 ~]# yum -d 0 -e 0 -y install mariadb-5.5.44-2.el7.centos.x86_64
错误：软件包：1:mariadb-5.5.44-2.el7.centos.x86_64 (dvd)
          需要：mariadb-libs(x86-64) = 1:5.5.44-2.el7.centos
          已安装: 1:mariadb-libs-5.5.47-1.el7_2.x86_64 (@updates)
              mariadb-libs(x86-64) = 1:5.5.47-1.el7_2
          可用: 1:mariadb-libs-5.5.44-2.el7.centos.x86_64 (dvd)
              mariadb-libs(x86-64) = 1:5.5.44-2.el7.centos
 您可以尝试添加 --skip-broken 选项来解决该问题
 您可以尝试执行：rpm -Va --nofiles --nodigest
```

问题很清楚：DVD 源里的 mariadb 是 **5.5.44**，而系统里已装的 mariadb-libs 是 updates 源里的 **5.5.47**，版本对不上，mariadb 主包装不上。

## 3. 解决：统一 mariadb-libs 版本

卸载高版本的 mariadb-libs，换装与 DVD 源一致的 5.5.44：

```shell
# 强制卸载高版本（注意 --nodeps 有风险，这里因依赖它的 mariadb 主包还没装上，所以可行）
[root@h1 Packages]# rpm -e --nodeps mariadb-libs-5.5.47-1.el7_2.x86_64
[root@h1 Packages]# rpm -qa mariadb-libs     # 确认已卸载干净
[root@h1 Packages]# rpm -ivh mariadb-libs-5.5.44-2.el7.centos.x86_64.rpm
准备中...                          ################################# [100%]
正在升级/安装...
   1:mariadb-libs-1:5.5.44-2.el7.cento################################# [100%]
[root@h1 Packages]# rpm -qa mariadb-libs     # 确认版本已换成 5.5.44
mariadb-libs-5.5.44-2.el7.centos.x86_64
```

重新执行 packstack 安装，mariadb 这一步正常通过。

## 4. 经验总结

部署时最好统一使用同一个 yum 源（比如全部走 CentOS 官方源或全部走 DVD 本地源），不要让部分包来自 updates 源、部分来自 DVD 源，否则容易出现这种"同软件不同版本"的依赖冲突。
