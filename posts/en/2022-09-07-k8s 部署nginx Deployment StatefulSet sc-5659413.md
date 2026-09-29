---
title: "Deploying Nginx on k8s with Deployment/StatefulSet and a StorageClass"
date: "2022-09-07 16:59:43"
category: "cluster"
source: "https://blog.51cto.com/hequan/5659413"
lang: "en"
---
> **About this post**
>
> This post demonstrates how to dynamically provision PVs in Kubernetes through an NFS StorageClass and deploy an Nginx application. It includes a complete YAML example with a PVC requesting 1000Mi of shared storage, plus a Deployment (replaceable with a StatefulSet) mounting that PVC at `/usr/share/nginx/html`.
>
> **Technical notes**
>
> NFS dynamic provisioning requires nfs-subdir-external-provisioner to be deployed in advance; the ReadWriteMany access mode depends on NFS server support. In this scenario, the difference between a StatefulSet and a Deployment is minor; a StatefulSet is only necessary when stable network identities or ordered scaling are required.

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
kind: Deployment  ## StatefulSet also works here
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
