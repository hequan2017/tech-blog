---
title: "docker 仓库harbor 1.8.2 http 部署"
date: "2019-08-20 18:04:14"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2431158"
---
> **内容介绍**
>
> 本文记录离线部署 Harbor 1.8.2 私有 Docker 镜像仓库的完整流程：安装
> docker-compose、下载官方离线安装包，修改 harbor.yml 中 hostname 后执行
> prepare 与 install.sh 完成安装，并用默认账号 admin 创建 test 项目；末尾
> 给出 Docker 客户端对接 http 协议 Harbor 的方法——在 daemon.json 配置
> insecure-registries 免 https，登录后 tag 并 push 镜像到仓库。

> **技术备注**
>
> - Harbor 1.8.x 已很陈旧（现行主流为 2.x 版，配置文件沿用 harbor.yml），
>   且项目已从 vmware/harbor 迁至 goharbor/harbor。
> - 独立版 docker-compose（1.25.0-rc2）早已停止维护，新环境请改用 Docker
>   自带的 `docker compose` 插件。
> - 默认口令 admin/Harbor12345 仅适用于初体验，生产环境务必启用 https 并改密。

---

## 1. 说明

Harbor 是 VMware 公司开源的企业级 Docker Registry 项目，项目地址：
https://github.com/vmware/harbor （后迁移至 goharbor/harbor，原文链接域名缺失已补全）

部署步骤：

1. 下载离线安装包
2. 安装 Docker
3. 安装 docker-compose
4. Harbor 安装与配置
5. Docker 主机访问 Harbor

## 2. 服务端部署

安装 docker-compose（原文链接域名缺失，已补全 github.com）：

```shell
curl -L https://github.com/docker/compose/releases/download/1.25.0-rc2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose
```

下载 Harbor 离线安装包并解压：

```shell
wget https://storage.googleapis.com/harbor-releases/release-1.8.0/harbor-offline-installer-v1.8.2.tgz

tar xf harbor-offline-installer-v1.8.2.tgz

cd harbor/

vim harbor.yml
```

harbor.yml 中主要修改 hostname（1.8 起配置文件由 harbor.cfg 改为 harbor.yml）：

```yaml
hostname: 192.168.100.150
```

生成配置并安装（原文 `./` 后命令缺失，按官方流程补全为 install.sh）：

```shell
./prepare
./install.sh

docker-compose ps
```

浏览器访问 `http://192.168.100.150`，登录 admin / Harbor12345，创建一个 test 库。

## 3. 客户端配置（免 https）

http 协议的仓库需在 Docker 客户端声明为 insecure-registries：

```shell
vi /etc/docker/daemon.json
```

加上允许的仓库：

```json
{
  "insecure-registries": [
    "192.168.100.150"
  ]
}
```

修改后重启 docker 生效。

## 4. 登录与推送镜像

```shell
docker login 192.168.100.150 -u admin -p Harbor12345
docker tag centos 192.168.100.150/test/centos:v1
docker push 192.168.100.150/test/centos:v1
```
