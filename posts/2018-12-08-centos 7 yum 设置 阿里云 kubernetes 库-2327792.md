---
title: "centos 7  yum 设置 阿里云 kubernetes  库"
date: "2018-12-08 00:02:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327792"
---
> **内容介绍**
>
> 本文是Kubernetes 云原生容器编排实践,记录了「centos 7  yum 设置 阿里云 kubernetes  库」的相关内容。

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

```shell
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
       https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
```
