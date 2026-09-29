---
title: "Error from server (Forbidden): Forbidden (user=sys"
date: "2018-12-08 21:44:36"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2327975"
lang: "en"
---
> **About this post**
>
> This post deals with the Kubernetes access error Error from server (Forbidden):
> Forbidden (user=system:anonymous, verb=get, resource=nodes,
> subresource=proxy) — the request is issued as the anonymous user with no
> permissions at all. The temporary fix given is to bind the cluster-admin
> cluster role to the system:anonymous anonymous user, so that anonymous
> requests gain administrator privileges and thus bypass the 403.

> **Technical notes**
>
> This command effectively opens the cluster's highest privileges to all
> unauthenticated requests and must only be used in an isolated test
> environment; in production, configure proper kubeconfig certificates with
> least-privilege RBAC, and disable anonymous access on the apiserver with
> --anonymous-auth=false.

---

## 1. The Error

```shell
Error from server (Forbidden): Forbidden (user=system:anonymous, verb=get, resource=nodes, subresource=proxy)
```

## 2. Temporary Workaround

Bind the cluster-admin privileges:

```shell
kubectl create clusterrolebinding system:anonymous --clusterrole=cluster-admin --user=system:anonymous
```
