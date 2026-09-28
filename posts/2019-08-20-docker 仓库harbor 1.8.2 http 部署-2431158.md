---
title: "docker 仓库harbor 1.8.2 http 部署"
date: "2019-08-20 18:04:14"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2431158"
---

### docker 仓库harbor 1.8.2 http 部署

Harbor是VMware公司开源的企业级Docker Registry项目，项目地址： https:///vmware/harbor
1、下载离线安装包

2、安装Docker
3、安装docker-compose
4、 Harbor安装与配置
5、 Docker主机访问Harbor

---

#### 部署

```
curl -L https:///docker/compose/releases/download/1.25.0-rc2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

wget https://storage.googleapis.com/harbor-releases/release-1.8.0/harbor-offline-installer-v1.8.2.tgz

tar xf  harbor-offline-installer-v1.8.2.tgz
```

```
cd harbor/

vim harbor.yml
hostname: 192.168.100.150

./prepare
./

docker-compose  ps

登录  admin   密码Harbor12345，创建一个test的库
```

#### 客户端

```
免https

vi /etc/docker/daemon.json

# 加上 允许的仓库
{
  "insecure-registries":[
    "192.168.100.150"
  ]
}
```

```
docker  login  192.168.100.150   -u admin -p Harbor12345
docker tag centos  192.168.100.150/test/centos:v1
docker push 192.168.100.150/test/centos:v1
```
