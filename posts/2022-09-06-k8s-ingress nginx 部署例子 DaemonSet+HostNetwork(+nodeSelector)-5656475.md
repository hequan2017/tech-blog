---
title: "k8s-ingress nginx 部署例子  DaemonSet+HostNetwork(+nodeSelector)"
date: "2022-09-06 18:57:08"
category: "集群"
source: "https://blog.51cto.com/hequan/5656475"
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
