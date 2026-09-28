---
title: "k8s  StatefulSet ingress 例子"
date: "2019-09-12 11:52:40"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2437663"
---
> **内容介绍**
>
> 本文是Kubernetes 云原生容器编排实践,记录了「k8s  StatefulSet ingress 例子」的相关内容。主要涉及:### k8s StatefulSet例子…

> **技术备注**
>
> Nginx 配置在不同大版本间略有差异,建议以当前稳定版(1.24+/1.26+)官方文档为准。

---

### k8s  StatefulSet例子

```shell
api Version: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
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
  serviceName: "nginx"
  replicas: 2        # by default is 1
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
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "nfs"
      resources:
        requests:
          storage: 1Gi
```

```shell
api Version: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-web
  namespace: default
spec:
  rules:
  - host:
    http:
     paths:
     - path:
       backend:
        serviceName: nginx
        servicePort: 80
```
