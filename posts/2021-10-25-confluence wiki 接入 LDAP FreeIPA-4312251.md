---
title: "confluence  wiki 接入 LDAP FreeIPA"
date: "2021-10-25 15:06:03"
category: "集群"
source: "https://blog.51cto.com/hequan/4312251"
---
> **内容介绍**
>
> 本文是服务器集群与高可用架构实践,记录了「confluence  wiki 接入 LDAP FreeIPA」的相关内容。主要涉及:### 搭建freeipa > 3个ok 就可以。 >…

> **技术备注**
>
> Docker 与 Kubernetes 生态演进较快,新版 K8s 默认运行时为 containerd,请注意适配。

---

### 搭建freeipa

```bash
  
 	docker run --name dev-freeipa -ti -h  --read-only \
 -v /sys/fs/cgroup:/sys/fs/cgroup:ro  \
 -v /var/lib/ipa-data:/data:Z \
 -e PASSWORD=xxxxxxxxxxxxxxxx \
 -p 80:80 -p 389:389 -p 443:443 \
 --sysctl net.ipv6.conf.all.disable_ipv6=0 \
 freeipa/freeipa-server:centos-8-4.8.7 \
 ipa-server-install -U -r XXXX.COM   --no-ntp

 进入容器
 kinit admin
 ipa user-find --all
```

![1.png](assets/4312251/01_1635145418782228.png)
![2.png](assets/4312251/02_1635145423624278.png)![3.png](assets/4312251/03_1635145427149881.png)
![4.png](assets/4312251/04_1635145432284316.png)
![5.png](assets/4312251/05_1635145437863325.png)

> 3个ok 就可以。
> ![6.png](assets/4312251/06_1635145507860136.png)
