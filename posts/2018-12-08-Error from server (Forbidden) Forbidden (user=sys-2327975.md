---
title: "Error from server (Forbidden): Forbidden (user=sys"
date: "2018-12-08 21:44:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327975"
---
> **内容介绍**
>
> 本文是Kubernetes 云原生容器编排实践,记录了「Error from server (Forbidden): Forbidden (user=sys」的相关内容。主要涉及:### 报错 ### 暂时解决办法 绑定一个cluster-admin的权限。…

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

### 报错

```shellError from server (Forbidden): Forbidden (user=system:anonymous, verb=get, resource=nodes, subresource=proxy)
```

### 暂时解决办法

绑定一个cluster-admin的权限。

```shellkubectl create clusterrolebinding system:anonymous   --clusterrole=cluster-admin   --user=system:anonymous
```
