---
title: "k8s  部署nginx    Deployment/StatefulSet    sc"
date: "2022-09-07 16:59:43"
category: "cluster"
source: "https://blog.51cto.com/hequan/5659413"
---
> **内容介绍**
>
> 本文演示在 Kubernetes 中通过 NFS StorageClass 动态供给 PV，部署 Nginx 应用。包含一个 PVC 申请 1000Mi 共享存储，以及 Deployment（可替换为 StatefulSet）挂载该 PVC 到 `/usr/share/nginx/html` 的完整 YAML 示例。
>
> **技术备注**
>
> NFS 动态供给需提前部署 nfs-subdir-external-provisioner；ReadWriteMany 模式依赖 NFS 服务端支持。StatefulSet 与 Deployment 在此场景差异不大，仅当需要稳定网络标识或有序扩缩容时才必须使用 StatefulSet。

---

```shell
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: nginx-web-claim
spec:
  storageClassName: nfs-client
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1000Mi
---
apiVersion: apps/v1
kind: Deployment  ## 这里也可以写成 StatefulSet
metadata:
  name: web-1
spec:
  selector:
    matchLabels:
      app: web-1
  replicas: 3
  template:
    metadata:
      labels:
        app: web-1
    spec:
      containers:
      - name: web-1
        image: nginx:1.23
        ports:
          - containerPort: 80
        volumeMounts:
        - name: test-storage
          mountPath: /usr/share/nginx/html
      volumes:
      - name: test-storage
        persistentVolumeClaim:
          claimName: nginx-web-claim
```
