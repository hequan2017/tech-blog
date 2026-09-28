---
title: "Solo博客系统--Jenkins/docker自动化构建发布系统"
date: "2018-04-05 20:24:32"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2095114"
---
> **内容介绍**
>
> 用 Jenkins + Docker 为 Solo 博客系统搭建自动化构建发布流水线的实战记录：自建 git 裸仓库存放代码，Jenkins 容器内挂载 docker.sock 构建镜像并推送到 Harbor 私有仓库，Poll SCM 每分钟轮询触发 Maven 构建，最后通过 SSH 远程在 Docker 主机上重建并启动 Solo 容器。

> **技术备注**
>
> 文中方案基于 2018 年的 Jenkins 2.x + Docker 早期版本：官方 `jenkins` 镜像已更名为 `jenkins/jenkins`，Debian jessie 源早已下线（163 镜像同样不可用），现代做法是基于 `jenkins/jenkins:lts` 自行封装。挂载 docker.sock 构建镜像的方式如今多被 Kaniko、BuildKit 等无特权方案替代；Tomcat 8.0 与 JDK 8 均已 EOL，仅供理解流程参考。

---

![Jenkins 自动化发布环境规划表,三台服务器的分工](assets/2095114/01_a2f996f35d2f81ba2ec75f4906b23bbf.jpg)
![环境工具版本表,含 maven、jenkins 与 docker 版本](assets/2095114/02_20d586154eba556461fd88e24ecd513b.jpg)

### 部署

#### git服务器

```shell
yum install git
useradd git
passwd git

创建仓库
su - git
mkdir  solo.git
git --bare  init  ##初始化仓库
```

#### docker

```shell
cat >> /etc/docker/daemon.json　<< EOF
{
"insecure-registries":[":5000"]
}
EOF
```

#### Jenkins服务器

```shell
wget https://codeload.github.com/b3log/solo/zip/master
unzip master

##用来让 jenkins 免密钥 拉代码
ssh-keygen    -t rsa
ssh-copy-id   git@

git clone git@:/home/git/solo.git
cp -rf solo-master/* solo/
cd solo

 # docker服务器 ip  和 监听端口
vim   src/main/resources/latke.properties
serverHost=192.168.1.111
serverPort=80

#上传代码
git add .
git commit  -m "all"
git push origin  master
```

#### 生成一个基本镜像

```shell
cat >>  Dockerfile << EOF

FROM jenkins

USER root
RUN echo '' > /etc/apt/sources.list.d/jessie-backports.list && \
    wget http://mirrors.163.com/.help/sources.list.jessie -O /etc/apt/sources.list

RUN apt-get update && apt-get install -y git libltdl-dev

EOF

docker  build   -t  jenkins:v1  .
```

#### 启动jenkins

```shell
docker run -d \
--name jenkins \
-p 8080:8080 \
-v /var/jenkins_home/:/var/jenkins_home \
-v /usr/local/apache-maven-3.5.0:/usr/local/maven \
-v /usr/local/jdk1.8.0_45:/usr/local/jdk \
-v /var/run/docker.sock:/var/run/docker.sock \
-v $(which docker):/usr/bin/docker \
-v ~/.ssh:/root/.ssh \
jenkins:v1
```

#### tomcat 基础镜像上传到 harbor 服务器

```dockerfile
FROM centos:7
MAINTAINER   hequan

RUN yum install unzip iproute -y

ENV JAVA_HOME /usr/local/jdk

ADD apache-tomcat-8.0.46.tar.gz /usr/local
RUN mv /usr/local/apache-tomcat-8.0.46 /usr/local/tomcat

WORKDIR /usr/local/tomcat
EXPOSE 8080
ENTRYPOINT ["./bin/catalina.sh", "run"]
```

```shell
docker  build  -t  /test/tomcat:v1  .
docker  login -u hequan -p  123456
docker  push  /test/tomcat:v1
```

---

```shell
启动 设置jdk,git,maven

插件-高级    https://updates.jenkins.io/update-center.json
```

```shell
配置 Credentials -- (global) -- Add Credentials
SSH Username with private key
root
From the Jenkins master ~/.ssh
配置　　免密登录 docker 服务器系统管理--系统设置--
SSH remote
hosts
192.168.1.111 22root(docker)
```

### 创建任务

#### git

```shell
git@192.168.1.112:/home/git/solo.git
```

#### Poll SCM

```shell
* * * * *
```

#### Build

`clean install -Dmaven.test.skip=true`

#### Post Steps

##### Execute shell

```shell
cd $WORKSPACE
cat > Dockerfile <<EOF
FROM  /test/tomcat:v1

COPY  target/solo.war  /tmp/ROOT.war

RUN  rm -rf /usr/local/tomcat/webapps/*  && \
     unzip   /tmp/ROOT.war  -d  /usr/local/tomcat/webapps/ROOT  && \
     rm -f /tmp/ROOT.war

WORKDIR /usr/local/tomcat
EXPOSE 8080
ENTRYPOINT  ["./bin/catalina.sh","run"]
EOF

docker  build  -t  /test/solo:v1  .
docker  login -u hequan -p  123456
docker  push  /test/solo:v1
```

##### Execute shell script on remote host  using ssh

```shell
docker rm -f    solol  | true
docker  rmi -f   /test/solo:v1  |  true

docker  login -u hequan  -p  123456
docker  run   -itd   --name solol    -p 80:8080  -v /usr/local/jdk1.8.0_45/:/usr/local/jdk  /test/solo:v1
```

---

### 构建
