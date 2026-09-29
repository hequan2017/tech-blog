---
title: "k8s-ingress nginx Deployment Example: DaemonSet+HostNetwork(+nodeSelector)"
date: "2022-09-06 18:57:08"
category: "cluster"
source: "https://blog.51cto.com/hequan/5656475"
lang: "en"
---
> **About this post**
>
> This post provides a complete example of using ingress-nginx in Kubernetes: it creates an nginx Deployment (3 replicas) and a Service (port 8000), then routes the `www.xxxx.com/web` path to that Service through an Ingress. It is intended to be used with an ingress-controller deployed in DaemonSet + HostNetwork mode.
>
> **Technical notes**
>
> The Ingress API has been migrated from `extensions/v1beta1` to `networking.k8s.io/v1` in Kubernetes 1.22+. The `apiVersion: /v1` in this post is a typo; the correct value should be `networking.k8s.io/v1`. The `kubernetes.io/ingress.class` annotation is deprecated; it is recommended to use the `ingressClassName` field uniformly.

---

kubectl create ns test

nginx-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: test
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-web
  template:
    metadata:
      name: nginx-test
      labels:
        app: nginx-web
    spec:
      containers:
      - image: nginx
        name: nginx1
        imagePullPolicy: IfNotPresent

nginx-server.yaml

apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: test
spec:
  selector:
    app: nginx-web
  ports:
  - port: 8000
    protocol: TCP
    targetPort: 80

nginx-ingress.yaml

apiVersion: /v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: test
  annotations:
    kubernetes.io/ingress.class: nginx
    /rewrite-target: /
    /ssl-redirect: 'false'
spec:
  ingressClassName: nginx
  rules:
    - host: www.xxxx.com
      http:
        paths:
          - path: /web
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 8000
