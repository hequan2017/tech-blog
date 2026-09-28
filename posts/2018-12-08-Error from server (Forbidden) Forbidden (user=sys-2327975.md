---
title: "Error from server (Forbidden): Forbidden (user=sys"
date: "2018-12-08 21:44:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327975"
---

### 报错

```
Error from server (Forbidden): Forbidden (user=system:anonymous, verb=get, resource=nodes, subresource=proxy)
```

### 暂时解决办法

绑定一个cluster-admin的权限。

```
kubectl create clusterrolebinding system:anonymous   --clusterrole=cluster-admin   --user=system:anonymous
```
