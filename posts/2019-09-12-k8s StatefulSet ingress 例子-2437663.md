---
title: "k8s  StatefulSet ingress 例子"
date: "2019-09-12 11:52:40"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2437663"
---
> **内容介绍**
>
> 本文用 Nginx 示例演示 Kubernetes StatefulSet 的典型写法：
> 先定义 Headless Service（clusterIP: None），再创建两个副本的 web 应用；
> 通过 volumeClaimTemplates 为每个 Pod 分配独立的 NFS 存储（1Gi）；
> 最后附一个 Ingress，把外部请求转发到该服务。

> **技术备注**
>
> 以 2026 年视角回看：StatefulSet 的 apps/v1 至今仍是标准 API，写法无需改动。
> 但 Ingress 的 extensions/v1beta1 已在 Kubernetes v1.22 移除，需改用 networking.k8s.io/v1：
> backend 要写成 service.name + service.port.number，paths 还必须显式指定 pathType（如 Prefix）。
> 示例中 storageClassName: "nfs" 要求集群已存在同名 StorageClass，如今多由 NFS CSI 驱动提供。

---

## 1. k8s StatefulSet 例子

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None            # Headless Service：不分配 ClusterIP，供 StatefulSet 稳定寻址
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx           # has to match .spec.template.metadata.labels
  serviceName: "nginx"     # 关联上面同名的 Headless Service
  replicas: 2              # by default is 1
  template:
    metadata:
      labels:
        app: nginx        # has to match .spec.selector.matchLabels
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:    # 为每个 Pod 自动创建一份独立 PVC
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "nfs"
      resources:
        requests:
          storage: 1Gi
```

## 2. Ingress 例子

```yaml
apiVersion: extensions/v1beta1   # 已废弃：v1.22 起改用 networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-web
  namespace: default
spec:
  rules:
  - host:                        # 留空：匹配所有域名
    http:
      paths:
      - path:                    # 留空：匹配所有路径
        backend:
          serviceName: nginx
          servicePort: 80
```
