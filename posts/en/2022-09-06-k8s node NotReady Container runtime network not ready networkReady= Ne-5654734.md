---
title: "k8s node NotReady: Container runtime network not ready"
date: "2022-09-06 10:58:01"
category: "cluster"
source: "https://blog.51cto.com/hequan/5654734"
lang: "en"
---
> **About this post**
>
> This post resolves the `Container runtime network not ready` error reported by kubelet when adding a new Kubernetes node. The root cause is that Calico was deployed first, so the newly joined node is missing the CNI configuration and certificates; simply scp the files under `/etc/cni/net.d/` on the master node to the new node, and it will return to Ready.
>
> **Technical notes**
>
> Normally the Calico DaemonSet distributes the CNI configuration automatically; manual copying is a stopgap for scenarios such as image pull failures or a calico-node Pod that is not ready. Recent Calico versions already support automatic retries, so checking the calico-node logs first is recommended.

---

```shell
Container runtime network not ready" networkReady="NetworkRe

Solution:

Calico was deployed first, and the node joined later without the Calico certificates being synced

cd /etc/cni/net.d/
scp *  root@k8s-node1:/etc/cni/net.d/
```
