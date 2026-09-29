---
title: "Deploying the Harbor 1.8.2 Docker Registry over HTTP"
date: "2019-08-20 18:04:14"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2431158"
lang: "en"
---
> **About this post**
>
> This post documents the complete process of an offline deployment of Harbor
> 1.8.2, a private Docker image registry: installing docker-compose, downloading
> the official offline installer, changing the hostname in harbor.yml, then
> running prepare and install.sh to finish the installation, and using the
> default admin account to create a test project. The end of the post shows how
> to connect a Docker client to an HTTP-based Harbor — configure
> insecure-registries in daemon.json to bypass HTTPS, then log in and tag and
> push images to the registry.

> **Technical notes**
>
> - Harbor 1.8.x is quite outdated (the current mainstream is the 2.x line,
>   which still uses harbor.yml as its config file), and the project has moved
>   from vmware/harbor to goharbor/harbor.
> - The standalone docker-compose (1.25.0-rc2) has long been unmaintained; in
>   new environments, use Docker's built-in `docker compose` plugin instead.
> - The default admin/Harbor12345 password is only suitable for a first try; in
>   production, always enable HTTPS and change the password.

---

## 1. Overview

Harbor is an enterprise-grade Docker Registry project open-sourced by VMware. Project address:
https://github.com/vmware/harbor (later migrated to goharbor/harbor; the domain missing from the original link has been filled in)

Deployment steps:

1. Download the offline installer
2. Install Docker
3. Install docker-compose
4. Harbor installation and configuration
5. Access Harbor from the Docker host

## 2. Server-Side Deployment

Install docker-compose (the domain was missing in the original link; github.com has been filled in):

```shell
curl -L https://github.com/docker/compose/releases/download/1.25.0-rc2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose
```

Download the Harbor offline installer and extract it:

```shell
wget https://storage.googleapis.com/harbor-releases/release-1.8.0/harbor-offline-installer-v1.8.2.tgz

tar xf harbor-offline-installer-v1.8.2.tgz

cd harbor/

vim harbor.yml
```

The main change in harbor.yml is the hostname (starting with 1.8, the config file changed from harbor.cfg to harbor.yml):

```yaml
hostname: 192.168.100.150
```

Generate the configuration and install (the command after `./` was missing in the original; restored as install.sh per the official process):

```shell
./prepare
./install.sh

docker-compose ps
```

Visit `http://192.168.100.150` in a browser, log in as admin / Harbor12345, and create a test project.

## 3. Client Configuration (Bypassing HTTPS)

A registry served over HTTP must be declared as an insecure-registries entry in the Docker client:

```shell
vi /etc/docker/daemon.json
```

Add the allowed registry:

```json
{
  "insecure-registries": [
    "192.168.100.150"
  ]
}
```

Restart Docker for the change to take effect.

## 4. Logging In and Pushing Images

```shell
docker login 192.168.100.150 -u admin -p Harbor12345
docker tag centos 192.168.100.150/test/centos:v1
docker push 192.168.100.150/test/centos:v1
```
