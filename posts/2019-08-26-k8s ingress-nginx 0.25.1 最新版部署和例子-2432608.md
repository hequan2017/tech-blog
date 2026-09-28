---
title: "k8s ingress-nginx 0.25.1 最新版部署和例子"
date: "2019-08-26 14:27:23"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2432608"
---
> **内容介绍**
>
> 本文是Kubernetes 云原生容器编排实践,记录了「k8s ingress-nginx 0.25.1 最新版部署和例子」的相关内容。主要涉及:### k8s ingress-nginx 0.25.1 最新版部署和例子 #### 说明 #### 部署…

> **技术备注**
>
> Nginx 配置在不同大版本间略有差异,建议以当前稳定版(1.24+/1.26+)官方文档为准。

---

### k8s ingress-nginx 0.25.1 最新版部署和例子

#### 说明

```shellhttps:///kubernetes/ingress-nginx/blob/master/docs/deploy/

增加了7层的识别能力，可以根据 http header, path 等进行路由转发
```

#### 部署

```shellwget  https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml

sed -i 's#quay.io/kubernetes-ingress-controller/nginx-ingress-controller#/google_containers/nginx-ingress-controller#g' mandatory.yaml

cat service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  labels:
    /name: ingress-nginx
    /part-of: ingress-nginx
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: 80
      protocol: TCP
      nodePort: 32080  #http
    - name: https
      port: 443
      targetPort: 443
      protocol: TCP
      nodePort: 32443  #https
  selector:
    /name: ingress-nginx
    /part-of: ingress-nginx
```shell

```shellkubectl create -f  mandatory.yaml
kubectl create -f  service-nodeport.yaml
```

#### 检查

```shellkubectl get pod -n ingress-nginx -o wide

kubectl scale --replicas=2  deploy/nginx-ingress-controller -n ingress-nginx
```shell

#### 例子

```shellvim  deploy-demo.yaml
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

vim  ingress-myapp.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
name: ingress-myapp
namespace: default
annotations:
   kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host:
    http:
     paths:
     - path:
       backend:
        serviceName: myapp
        servicePort: 80

kubectl create -f  deploy-demo.yaml
kubectl create -f  ingress-myapp.yaml

　
#修改hosts　　　node节点ip
192.168.100.112   　　

访问 :32080
```
