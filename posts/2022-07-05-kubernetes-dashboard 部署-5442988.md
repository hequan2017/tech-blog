---
title: "kubernetes-dashboard  部署"
date: "2022-07-05 10:15:57"
category: "python"
source: "https://blog.51cto.com/hequan/5442988"
---
> **内容介绍**
>
> 本文演示 Kubernetes Dashboard v2.6.0 的快速部署与访问：通过官方 recommended.yaml 安装，使用 port-forward 将 Dashboard 服务映射到本地 8080 端口，并通过 admin-user 的 Secret 获取登录 Token。
>
> **技术备注**
>
> Dashboard v2.6.0 仅支持 Kubernetes 1.21-1.25；当前最新版本已迁移至独立 Helm Chart。port-forward 方式仅适合本地调试，生产环境应使用 Ingress + TLS 或 NodePort 配合防火墙规则。

---

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.0/aio/deploy/recommended.yaml


 kubectl get svc,pods  -n kubernetes-dashboard

kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')

kubectl port-forward -n kubernetes-dashboard --address 0.0.0.0 service/kubernetes-dashboard 8080:443

https://访问
```
