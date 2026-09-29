---
title: "Deploying kubernetes-dashboard"
date: "2022-07-05 10:15:57"
category: "python"
source: "https://blog.51cto.com/hequan/5442988"
lang: "en"
---
> **About this post**
>
> This post demonstrates a quick deployment of Kubernetes Dashboard v2.6.0 and how to access it: install it via the official recommended.yaml, map the Dashboard service to local port 8080 with port-forward, and obtain the login token from the admin-user Secret.
>
> **Technical notes**
>
> Dashboard v2.6.0 only supports Kubernetes 1.21-1.25; the latest releases have moved to a standalone Helm chart. The port-forward approach is suitable only for local debugging; in production, use Ingress + TLS or NodePort combined with firewall rules.

---

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.0/aio/deploy/recommended.yaml


 kubectl get svc,pods  -n kubernetes-dashboard

kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')

kubectl port-forward -n kubernetes-dashboard --address 0.0.0.0 service/kubernetes-dashboard 8080:443

https://access
```
