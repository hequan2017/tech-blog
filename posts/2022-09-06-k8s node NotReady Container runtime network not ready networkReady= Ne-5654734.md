---
title: "k8s node NotReady Container runtime network not ready' networkReady='NetworkRe"
date: "2022-09-06 10:58:01"
category: "集群"
source: "https://blog.51cto.com/hequan/5654734"
---

```
Container runtime network not ready" networkReady="NetworkRe
```

报错解决：

先部署了calico，后加入node节点，没有同步 calico认证

```
#报错解决
cd /etc/cni/net.d/
scp *  root@k8s-node1:/etc/cni/net.d/
```
