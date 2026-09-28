---
title: "failed to get sandbox image 'k8s.gcr.io/pause:3.6': failed to pull image 'k8s.gcr.io/pause:3.6'"
date: "2022-09-06 11:36:38"
category: "集群"
source: "https://blog.51cto.com/hequan/5654959"
---
> **内容介绍**
>
> 本文解决 kubeadm 集群节点启动 Pod 时报错 `failed to get sandbox image 'k8s.gcr.io/pause:3.6'` 的问题。原因是国内无法直接访问 k8s.gcr.io，通过 crictl 从阿里云镜像拉取 pause:3.6，再用 ctr 重打 tag 为 k8s.gcr.io/pause:3.6 即可恢复。
>
> **技术备注**
>
> k8s.gcr.io 自 2023 年起已全面迁移至 registry.k8s.io，旧地址已下线；现在应直接修改 containerd 配置 `sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.6"` 或使用 kubeadm `--image-repository` 指定国内源。

---

```shell
Failed to create pod sandbox: rpc error: code = Unknown desc = failed to get sandbox image "/pause:3.6": failed to pull image "/pause:3.6": failed to pull and unpack image "/pause:3.6": failed to resolve reference "/pause:3.6": failed to do request: Head "https:///v2/pause/manifests/3.6": dial tcp 74.125.23.82:443: connect: connection refused

crictl pull /google_containers/pause:3.6
ctr -n k8s.io i tag /google_containers/pause:3.6 /pause:3.6
```
