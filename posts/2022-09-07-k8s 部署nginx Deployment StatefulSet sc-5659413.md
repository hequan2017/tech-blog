---
title: "k8s  部署nginx    Deployment/StatefulSet    sc"
date: "2022-09-07 16:59:43"
category: "集群"
source: "https://blog.51cto.com/hequan/5659413"
---
> **内容介绍**
>
> 本文是服务器集群与高可用架构实践,记录了「k8s  部署nginx    Deployment/StatefulSet    sc」的相关内容。

> **技术备注**
>
> Nginx 配置在不同大版本间略有差异,建议以当前稳定版(1.24+/1.26+)官方文档为准。

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
