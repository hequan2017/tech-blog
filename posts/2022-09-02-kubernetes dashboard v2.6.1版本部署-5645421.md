---
title: "kubernetes dashboard v2.6.1版本部署"
date: "2022-09-02 16:21:41"
category: "集群"
source: "https://blog.51cto.com/hequan/5645421"
---

```
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
