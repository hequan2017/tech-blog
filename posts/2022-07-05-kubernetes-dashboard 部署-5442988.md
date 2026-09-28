---
title: "kubernetes-dashboard  部署"
date: "2022-07-05 10:15:57"
category: "python"
source: "https://blog.51cto.com/hequan/5442988"
---

```
 kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.0/aio/deploy/recommended.yaml
 
 
 kubectl get svc,pods  -n kubernetes-dashboard

kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')

kubectl port-forward -n kubernetes-dashboard --address 0.0.0.0 service/kubernetes-dashboard 8080:443

https://访问
```
