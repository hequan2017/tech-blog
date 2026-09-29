---
title: "kubernetes dashboard v2.6.1版本部署"
date: "2022-09-02 16:21:41"
category: "cluster"
source: "https://blog.51cto.com/hequan/5645421"
---
> **内容介绍**
>
> 本文记录 Kubernetes Dashboard v2.6.1 的部署与访问配置：通过官方 recommended.yaml 一键安装，将 Service 改为 NodePort 暴露 443 端口，创建 ServiceAccount 与 Secret 并绑定 cluster-admin ClusterRole，最后通过 describe secret 获取登录 Token。
>
> **技术备注**
>
> Dashboard v2.6.1 发布于 2022 年，仅支持较旧 Kubernetes；当前最新 v3.x 采用独立 chart 部署。另外，为安全起见，生产环境不建议直接绑定 cluster-admin，应使用最小权限 RBAC。

---

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.1/aio/deploy/recommended.yaml

kubectl edit svc -n kubernetes-dashboard kubernetes-dashboard

  type: ClusterIP  -->  type: NodePort

kubectl get svc,node  -n kubernetes-dashboard
kubernetes-dashboard        NodePort    10.200.215.169   <none>        443:30780/TCP   15m

1.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hequan
  namespace: kubernetes-dashboard
---
apiVersion: v1
kind: Secret
metadata:
  name: hequan
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/service-account.name: hequan
type: kubernetes.io/service-account-token
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: hequan
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: hequan
  namespace: kubernetes-dashboard

kubectl apply -f 1.yaml

kubectl -n kubernetes-dashboard describe secret hequan
```
