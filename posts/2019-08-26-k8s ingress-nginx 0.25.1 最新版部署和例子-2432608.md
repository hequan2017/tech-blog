---
title: "k8s ingress-nginx 0.25.1 最新版部署和例子"
date: "2019-08-26 14:27:23"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2432608"
---
> **内容介绍**
>
> 本文记录 Kubernetes 集群部署 ingress-nginx 0.25.1 的过程与示例：下载官方
> mandatory.yaml 并用 sed 把镜像替换为国内仓库，通过 NodePort Service 暴露
> 32080/32443 端口，扩容 controller 副本；随后以 myapp 的 Deployment + Service +
> Ingress 三件套演示七层路由，修改客户端 hosts 指向 node IP 后经 NodePort 访问
> 验证。

> **技术备注**
>
> - ingress-nginx 0.25.1 为 2019 年版本，`mandatory.yaml` 已淘汰：新版
>   （controller v1.x）改用官方 `deploy.yaml` 或 Helm 安装。
> - 文中 Ingress 用 `extensions/v1beta1`，该 API 在 K8s 1.16 弃用、1.22 起
>   移除，新集群需改用 `networking.k8s.io/v1`。
> - quay.io 镜像国内拉取困难，文中 sed 替换的仓库前缀原文被截断，按国内
>   常见写法补全为 `registry.aliyuncs.com/google_containers`。

---

## 1. 说明

官方部署文档： https://github.com/kubernetes/ingress-nginx/blob/master/docs/deploy/
（原文链接域名缺失，已补全 github.com）

ingress 为集群增加了七层的识别能力，可以根据 http header、path 等进行路由转发。

## 2. 部署

下载并替换镜像仓库（sed 目标前缀原文被截断，按常见用法补全）：

```shell
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml

sed -i 's#quay.io/kubernetes-ingress-controller/nginx-ingress-controller#registry.aliyuncs.com/google_containers/nginx-ingress-controller#g' mandatory.yaml
```

service-nodeport.yaml（原文 label 前缀 `app.kubernetes.io` 缺失，已补全）：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  labels:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: 80
      protocol: TCP
      nodePort: 32080  # http
    - name: https
      port: 443
      targetPort: 443
      protocol: TCP
      nodePort: 32443  # https
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
```

创建资源：

```shell
kubectl create -f mandatory.yaml
kubectl create -f service-nodeport.yaml
```

## 3. 检查

```shell
kubectl get pod -n ingress-nginx -o wide

# 扩容到 2 个副本
kubectl scale --replicas=2 deploy/nginx-ingress-controller -n ingress-nginx
```

## 4. 例子：myapp 三件套

deploy-demo.yaml（原文缩进错乱、混有全角空格，已按合法 YAML 修复）：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: default
spec:
  selector:
    app: myapp
    release: stable
  ports:
  - name: myapp
    port: 80
    targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: default
spec:
  selector:
    matchLabels:
      app: myapp
      release: stable
  replicas: 3
  template:
    metadata:
      labels:
        app: myapp
        release: stable
    spec:
      containers:
      - name: myapp
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - name: myapp
          containerPort: 80
```

ingress-myapp.yaml（原文 host、path 值缺失，按示例补全）：

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-myapp
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: myapp.hequan.com
    http:
      paths:
      - path: /
        backend:
          serviceName: myapp
          servicePort: 80
```

创建并验证：

```shell
kubectl create -f deploy-demo.yaml
kubectl create -f ingress-myapp.yaml
```

修改客户端 hosts（node 节点 IP）：

```shell
192.168.100.112    myapp.hequan.com
```

浏览器访问 `http://myapp.hequan.com:32080`
