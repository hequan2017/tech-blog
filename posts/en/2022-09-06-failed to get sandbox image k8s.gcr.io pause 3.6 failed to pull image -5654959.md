---
title: "failed to get sandbox image 'k8s.gcr.io/pause:3.6': failed to pull image 'k8s.gcr.io/pause:3.6'"
date: "2022-09-06 11:36:38"
category: "cluster"
source: "https://blog.51cto.com/hequan/5654959"
lang: "en"
---
> **About this post**
>
> This post resolves the `failed to get sandbox image 'k8s.gcr.io/pause:3.6'` error that appears when a Pod starts on a kubeadm cluster node. The cause is that k8s.gcr.io cannot be accessed directly from mainland China; the fix is to pull pause:3.6 from the Alibaba Cloud mirror with crictl and then re-tag it as k8s.gcr.io/pause:3.6 with ctr.
>
> **Technical notes**
>
> Since 2023, k8s.gcr.io has been fully migrated to registry.k8s.io and the old address has been taken offline; the recommended approach now is to set the containerd configuration `sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.6"` directly, or to specify a China mirror with the kubeadm `--image-repository` flag.

---

```shell
Failed to create pod sandbox: rpc error: code = Unknown desc = failed to get sandbox image "/pause:3.6": failed to pull image "/pause:3.6": failed to pull and unpack image "/pause:3.6": failed to resolve reference "/pause:3.6": failed to do request: Head "https:///v2/pause/manifests/3.6": dial tcp 74.125.23.82:443: connect: connection refused

crictl pull /google_containers/pause:3.6
ctr -n k8s.io i tag /google_containers/pause:3.6 /pause:3.6
```
