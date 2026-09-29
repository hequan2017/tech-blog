---
title: "Deploying Kubernetes Dashboard v2.6.1"
date: "2022-09-02 16:21:41"
category: "cluster"
source: "https://blog.51cto.com/hequan/5645421"
lang: "en"
---
> **About this post**
>
> This post records the deployment and access configuration of Kubernetes Dashboard v2.6.1: a one-click install via the official recommended.yaml, changing the Service to NodePort to expose port 443, creating a ServiceAccount and a Secret and binding them to the cluster-admin ClusterRole, and finally obtaining the login token with describe secret.
>
> **Technical notes**
>
> Dashboard v2.6.1 was released in 2022 and only supports older Kubernetes versions; the latest v3.x is deployed with a standalone chart. Also, for security reasons, binding cluster-admin directly is not recommended in production; use least-privilege RBAC instead.

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
