---
title: "ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp"
date: "2016-07-04 14:44:50"
category: "openstack"
source: "https://blog.51cto.com/hequan/1795594"
lang: "en"
---
> **About this post**
>
> When installing OpenStack with packstack (RDO mode), Puppet exits with an error at the mariadb deployment step. Investigation showed that the mariadb in the local yum repo (the DVD) is 5.5.44, while the system already had a higher-version mariadb-libs 5.5.47 installed earlier from the updates repo; the version mismatch causes a dependency conflict. The fix is to remove the higher-version mariadb-libs, install 5.5.44 to match the DVD repo, and run the installation again.

> **Technical notes**
>
> MariaDB 5.5 reached EOL in April 2020, and CentOS 7 itself reached EOL in June 2024; by 2026 the packstack/RDO method is essentially used only for teaching demos. Today the mainstream ways to deploy OpenStack are Kolla-Ansible or OpenStack-Ansible (based on container/venv isolation, so this kind of system-level RPM version conflict no longer occurs); if you still need to install MariaDB on an EL-family system, use dnf and enable the official MariaDB repository (e.g., 10.11 LTS).

---

## 1. The Error

When installing OpenStack in RDO (packstack) mode, the installation fails with an error when it reaches the database node:

```shell
ERROR : Error appeared during Puppet run: 192.168.1.201_mariadb.pp
Error: Execution of '/usr/bin/yum -d 0 -e 0 -y install mariadb' returned 1: Error: Package: 1:mariadb-5.5.44-2.el7.centos.x86_64 (dvd)
You will find full trace in log /var/tmp/packstack/20160704-142958-_jXSqZ/manifests/192.168.1.201_mariadb.pp.log
```

## 2. Troubleshooting: Version Mismatch Causes a Dependency Conflict

Suspecting a package problem, I ran yum manually to install the specific version and verify:

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

The problem is clear: the mariadb in the DVD repo is **5.5.44**, while the mariadb-libs already installed on the system is **5.5.47** from the updates repo. The versions do not match, so the mariadb main package cannot be installed.

## 3. Fix: Align the mariadb-libs Version

Remove the higher-version mariadb-libs and install 5.5.44 to match the DVD repo:

```shell
# Force-remove the higher version (--nodeps is risky; it works here because the mariadb main package that depends on these libs is not installed yet)
[root@h1 Packages]# rpm -e --nodeps mariadb-libs-5.5.47-1.el7_2.x86_64
[root@h1 Packages]# rpm -qa mariadb-libs     # confirm it is fully removed
[root@h1 Packages]# rpm -ivh mariadb-libs-5.5.44-2.el7.centos.x86_64.rpm
准备中...                          ################################# [100%]
正在升级/安装...
   1:mariadb-libs-1:5.5.44-2.el7.cento################################# [100%]
[root@h1 Packages]# rpm -qa mariadb-libs     # confirm the version is now 5.5.44
mariadb-libs-5.5.44-2.el7.centos.x86_64
```

Rerunning the packstack installation, the mariadb step passed without problems.

## 4. Lessons Learned

When deploying, it is best to stick to a single yum source consistently (for example, all packages from the official CentOS repos, or all from the local DVD repo). Do not let some packages come from the updates repo and others from the DVD repo; otherwise you can easily run into this kind of "same software, different versions" dependency conflict.
