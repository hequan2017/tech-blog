---
title: "k8s StatefulSet Ingress Example"
date: "2019-09-12 11:52:40"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2437663"
lang: "en"
---
> **About this post**
>
> This article uses an Nginx example to demonstrate the typical pattern of a Kubernetes StatefulSet:
> first define a Headless Service (clusterIP: None), then create a web application with two replicas;
> use volumeClaimTemplates to give each Pod its own NFS storage (1Gi);
> finally, add an Ingress that forwards external requests to the service.

> **Technical notes**
>
> Looking back from a 2026 perspective: the apps/v1 StatefulSet is still the standard API and needs no changes.
> However, the extensions/v1beta1 Ingress was removed in Kubernetes v1.22; use networking.k8s.io/v1 instead:
> the backend must be written as service.name + service.port.number, and paths must explicitly specify pathType (e.g. Prefix).
> The example's storageClassName: "nfs" requires a StorageClass of the same name to already exist in the cluster; nowadays it is usually provided by an NFS CSI driver.

---

## 1. k8s StatefulSet Example

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
  clusterIP: None            # Headless Service: no ClusterIP allocated, for stable addressing by the StatefulSet
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
  serviceName: "nginx"     # ties to the Headless Service of the same name above
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
  volumeClaimTemplates:    # automatically creates a separate PVC for each Pod
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "nfs"
      resources:
        requests:
          storage: 1Gi
```

## 2. Ingress Example

```yaml
apiVersion: extensions/v1beta1   # deprecated: use networking.k8s.io/v1 from v1.22 on
kind: Ingress
metadata:
  name: ingress-web
  namespace: default
spec:
  rules:
  - host:                        # empty: matches all hosts
    http:
      paths:
      - path:                    # empty: matches all paths
        backend:
          serviceName: nginx
          servicePort: 80
```
