---
title: "Deploying the Latest k8s ingress-nginx 0.25.1 with Examples"
date: "2019-08-26 14:27:23"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2432608"
lang: "en"
---
> **About this post**
>
> This post documents the process and examples for deploying ingress-nginx
> 0.25.1 on a Kubernetes cluster: downloading the official mandatory.yaml and
> using sed to replace image references with a China-based registry, exposing
> ports 32080/32443 through a NodePort Service, and scaling up controller
> replicas; it then demonstrates Layer-7 routing with the myapp
> Deployment + Service + Ingress trio, verifying access via the NodePort after
> pointing the client hosts file to the node IP.

> **Technical notes**
>
> - ingress-nginx 0.25.1 dates from 2019, and `mandatory.yaml` is now
>   obsolete: newer versions (controller v1.x) use the official `deploy.yaml`
>   or a Helm installation instead.
> - The Ingress in this post uses `extensions/v1beta1`, an API deprecated in
>   Kubernetes 1.16 and removed since 1.22; new clusters should use
>   `networking.k8s.io/v1` instead.
> - quay.io images are hard to pull from within China. The registry prefix in
>   the sed replacement was truncated in the original text and has been
>   completed as `registry.aliyuncs.com/google_containers`, following common
>   practice in China.

---

## 1. Overview

Official deployment documentation: https://github.com/kubernetes/ingress-nginx/blob/master/docs/deploy/
(the domain was missing in the original; completed with github.com)

Ingress adds Layer-7 awareness to the cluster, allowing routing and forwarding
based on HTTP headers, paths, and more.

## 2. Deployment

Download and replace the image registry (the sed target prefix was truncated
in the original and completed per common usage):

```shell
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml

sed -i 's#quay.io/kubernetes-ingress-controller/nginx-ingress-controller#registry.aliyuncs.com/google_containers/nginx-ingress-controller#g' mandatory.yaml
```

service-nodeport.yaml (the label prefix `app.kubernetes.io` was missing in the
original and has been completed):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: 80
      protocol: TCP
      nodePort: 32080  # http
    - name: https
      port: 443
      targetPort: 443
      protocol: TCP
      nodePort: 32443  # https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
```

Create the resources:

```shell
kubectl create -f mandatory.yaml
kubectl create -f service-nodeport.yaml
```

## 3. Verification

```shell
kubectl get pod -n ingress-nginx -o wide

# scale to 2 replicas
kubectl scale --replicas=2 deploy/nginx-ingress-controller -n ingress-nginx
```

## 4. Example: the myapp trio

deploy-demo.yaml (the original had broken indentation mixed with full-width
spaces, fixed as valid YAML):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: default
spec:
  selector:
    app: myapp
    release: stable
  ports:
  - name: myapp
    port: 80
    targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: default
spec:
  selector:
    matchLabels:
      app: myapp
      release: stable
  replicas: 3
  template:
    metadata:
      labels:
        app: myapp
        release: stable
    spec:
      containers:
      - name: myapp
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - name: myapp
          containerPort: 80
```

ingress-myapp.yaml (the host and path values were missing in the original,
completed per the example):

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: myapp.hequan.com
    http:
      paths:
      - path: /
        backend:
          serviceName: myapp
          servicePort: 80
```

Create and verify:

```shell
kubectl create -f deploy-demo.yaml
kubectl create -f ingress-myapp.yaml
```

Modify the client hosts file (node IP):

```shell
192.168.100.112    myapp.hequan.com
```

Browse to `http://myapp.hequan.com:32080`
