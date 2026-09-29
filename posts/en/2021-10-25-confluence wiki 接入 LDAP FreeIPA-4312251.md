---
title: "Integrating Confluence Wiki with LDAP FreeIPA"
date: "2021-10-25 15:06:03"
category: "cluster"
source: "https://blog.51cto.com/hequan/4312251"
lang: "en"
---
> **About this post**
>
> Quickly deploy FreeIPA with Docker as a centralized authentication center, then configure an LDAP user directory in the Confluence admin console: fill in the FreeIPA server address, Base DN, admin DN, and password, test the connection and sync users, so that the Wiki and FreeIPA share accounts.

> **Technical notes**
>
> The example was written against FreeIPA 4.8.7 (the CentOS 8 image) and Confluence Server; the official FreeIPA image has moved to CentOS Stream / Fedora, and Confluence Server reached end of support in 2024, so consider evaluating a migration to Confluence Data Center or Cloud. For production, use HTTPS/LDAPS and restrict anonymous binds.

---

### Setting up FreeIPA

```shell
docker run --name dev-freeipa -ti -h ipa.example.com --read-only \
  -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
  -v /var/lib/ipa-data:/data:Z \
  -e PASSWORD=xxxxxxxxxxxxxxxx \
  -p 80:80 -p 389:389 -p 443:443 \
  --sysctl net.ipv6.conf.all.disable_ipv6=0 \
  freeipa/freeipa-server:centos-8-4.8.7 \
  ipa-server-install -U -r XXXX.COM --no-ntp

# Enter the container
kinit admin
ipa user-find --all
```

![1.png](../assets/4312251/01_1635145418782228.png)
![2.png](../assets/4312251/02_1635145423624278.png)![3.png](../assets/4312251/03_1635145427149881.png)
![4.png](../assets/4312251/04_1635145432284316.png)
![5.png](../assets/4312251/05_1635145437863325.png)

> Three OKs and it is good to go.
> ![6.png](../assets/4312251/06_1635145507860136.png)
