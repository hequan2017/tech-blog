---
title: "k8s node NotReady Container runtime network not ready' networkReady='NetworkRe"
date: "2022-09-06 10:58:01"
category: "集群"
source: "https://blog.51cto.com/hequan/5654734"
---
> **内容介绍**
>
> 本文解决新增 Kubernetes 节点时 kubelet 报错 `Container runtime network not ready` 的问题。根本原因是先部署了 Calico，新加入的 node 缺少 CNI 配置与证书，只需将 master 节点 `/etc/cni/net.d/` 下的文件 scp 到新节点即可恢复 Ready。
>
> **技术备注**
>
> 正常情况下 Calico DaemonSet 会自动下发 CNI 配置；手动复制适用于镜像拉取失败或 calico-node Pod 未就绪的应急场景。当前 Calico 新版本已支持自动重试，建议优先排查 calico-node 日志。

---

```shell
Container runtime network not ready" networkReady="NetworkRe

报错解决：

先部署了calico，后加入node节点，没有同步 calico认证

cd /etc/cni/net.d/
scp *  root@k8s-node1:/etc/cni/net.d/
```
