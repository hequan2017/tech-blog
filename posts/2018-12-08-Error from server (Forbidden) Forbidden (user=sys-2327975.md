---
title: "Error from server (Forbidden): Forbidden (user=sys"
date: "2018-12-08 21:44:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327975"
---
> **内容介绍**
>
> 本文处理 Kubernetes 访问报错 Error from server (Forbidden):
> Forbidden (user=system:anonymous, verb=get, resource=nodes,
> subresource=proxy)——请求以匿名用户身份发出且无任何权限。给出的临时
> 解法是为 system:anonymous 匿名用户绑定 cluster-admin 集群角色，让匿名
> 请求获得管理员权限，从而绕过 403。

> **技术备注**
>
> 这条命令等于向所有未认证请求开放集群最高权限，只能用于隔离的测试
> 环境；生产环境应配置正确的 kubeconfig 证书与 RBAC 最小权限，并在
> apiserver 上以 --anonymous-auth=false 关闭匿名访问。

---

## 1. 报错

```shell
Error from server (Forbidden): Forbidden (user=system:anonymous, verb=get, resource=nodes, subresource=proxy)
```

## 2. 暂时解决办法

绑定一个 cluster-admin 的权限：

```shell
kubectl create clusterrolebinding system:anonymous --clusterrole=cluster-admin --user=system:anonymous
```
