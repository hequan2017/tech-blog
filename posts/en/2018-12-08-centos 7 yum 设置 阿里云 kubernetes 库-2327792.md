---
title: "Configure the Alibaba Cloud Kubernetes yum Repository on CentOS 7"
date: "2018-12-08 00:02:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327792"
lang: "en"
---
> **About this post**
>
> This post shows how to configure the Alibaba Cloud Kubernetes yum repository on CentOS 7: write the repo definition to
> /etc/yum.repos.d/kubernetes.repo, pointing to the kubernetes-el7-x86_64 repository on the Alibaba Cloud mirror site
> mirrors.aliyun.com, enable the repository, and turn on
> GPG signature verification at both the RPM package and repository metadata levels. Afterwards, you can use yum to install
> cluster components such as kubelet / kubeadm.

> **Technical notes**
>
> CentOS 7 reached end of life (EOL) on June 30, 2024; it is recommended to migrate to Rocky Linux 9 / AlmaLinux 9 or the domestic openEuler.
> The Alibaba Cloud el7 repository has stopped updating along with the upstream (it stalled around the v1.28 series); for newer Kubernetes versions, use the
> el9 repository instead. Cluster deployments nowadays have also mostly switched to the kubeadm + containerd approach.

---

## 1. Configure the repo file

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
