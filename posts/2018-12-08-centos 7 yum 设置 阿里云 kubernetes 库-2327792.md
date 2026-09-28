---
title: "centos 7  yum 设置 阿里云 kubernetes  库"
date: "2018-12-08 00:02:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327792"
---
> **内容介绍**
>
> 本文给出 CentOS 7 配置阿里云 Kubernetes yum 源的方法：向
> /etc/yum.repos.d/kubernetes.repo 写入 repo 定义，指向阿里云镜像站
> mirrors.aliyun.com 的 kubernetes-el7-x86_64 仓库，启用仓库并开启
> rpm 包与仓库元数据两级 GPG 签名校验，之后即可用 yum 安装
> kubelet / kubeadm 等集群组件。

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。
> 阿里云 el7 仓库已随上游停止更新（约停在 v1.28 系），新版本 k8s 请改用
> el9 仓库；如今集群部署也多改为 kubeadm + containerd 方案。

---

## 1. 配置 repo 文件

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
