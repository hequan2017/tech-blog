---
title: "failed to get sandbox image 'k8s.gcr.io/pause:3.6': failed to pull image 'k8s.gcr.io/pause:3.6'"
date: "2022-09-06 11:36:38"
category: "集群"
source: "https://blog.51cto.com/hequan/5654959"
---
> **内容介绍**
>
> 本文是服务器集群与高可用架构实践,记录了「failed to get sandbox image 'k8s.gcr.io/pause:3.6': failed to pull image 'k8s.gcr.io/pause:3.6'」的相关内容。

---

```shellFailed to create pod sandbox: rpc error: code = Unknown desc = failed to get sandbox image "/pause:3.6": failed to pull image "/pause:3.6": failed to pull and unpack image "/pause:3.6": failed to resolve reference "/pause:3.6": failed to do request: Head "https:///v2/pause/manifests/3.6": dial tcp 74.125.23.82:443: connect: connection refused

crictl pull /google_containers/pause:3.6
ctr -n k8s.io i tag /google_containers/pause:3.6 /pause:3.6
```
