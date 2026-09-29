---
title: "k8s-ingress nginx 部署例子  DaemonSet+HostNetwork(+nodeSelector)"
date: "2022-09-06 18:57:08"
category: "cluster"
source: "https://blog.51cto.com/hequan/5656475"
---
> **内容介绍**
>
> 本文给出 ingress-nginx 在 Kubernetes 中的完整应用示例：创建 nginx Deployment（3 副本）与 Service（8000 端口），再通过 Ingress 将 `www.xxxx.com/web` 路径路由到该 Service。适用于配合 DaemonSet + HostNetwork 模式的 ingress-controller 使用。
>
> **技术备注**
>
> Ingress API 在 Kubernetes 1.22+ 已从 `extensions/v1beta1` 迁移至 `networking.k8s.io/v1`，文中 `apiVersion: /v1` 存在拼写错误，正确应为 `networking.k8s.io/v1`；`kubernetes.io/ingress.class` 注解已废弃，建议统一使用 `ingressClassName` 字段。

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
