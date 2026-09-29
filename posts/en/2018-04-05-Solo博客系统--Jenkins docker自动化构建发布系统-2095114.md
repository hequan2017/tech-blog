---
title: "Solo Blog System -- Jenkins/Docker Automated Build and Release System"
date: "2018-04-05 20:24:32"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2095114"
lang: "en"
---
> **About this post**
>
> A hands-on record of building an automated build-and-release pipeline for the Solo blog system with Jenkins + Docker: a self-hosted git bare repository stores the code; the Jenkins container mounts docker.sock to build images and push them to a private Harbor registry; Poll SCM triggers the Maven build by polling every minute; and finally the Solo container is rebuilt and started on the Docker host remotely over SSH.

> **Technical notes**
>
> The solution in this post is based on Jenkins 2.x and early versions of Docker from 2018: the official `jenkins` image has since been renamed to `jenkins/jenkins`, the Debian jessie repositories were taken offline long ago (the 163 mirror is likewise unavailable), and the modern approach is to build a custom image on top of `jenkins/jenkins:lts`. Building images by mounting docker.sock has largely been replaced by unprivileged solutions such as Kaniko and BuildKit; both Tomcat 8.0 and JDK 8 have reached EOL, so this post is kept only as a reference for understanding the workflow.

---

![Jenkins automated release environment plan, division of work across three servers](../assets/2095114/01_a2f996f35d2f81ba2ec75f4906b23bbf.jpg)
![Environment tool versions, including maven, jenkins and docker versions](../assets/2095114/02_20d586154eba556461fd88e24ecd513b.jpg)

### Deployment

#### git server

```shell
yum install git
useradd git
passwd git

Create the repository
su - git
mkdir  solo.git
git --bare  init  ## initialize the repository
```

#### docker

```shell
cat >> /etc/docker/daemon.json　<< EOF
{
"insecure-registries":[":5000"]
}
EOF
```

#### Jenkins server

```shell
wget https://codeload.github.com/b3log/solo/zip/master
unzip master

## lets jenkins pull code without a key
ssh-keygen    -t rsa
ssh-copy-id   git@

git clone git@:/home/git/solo.git
cp -rf solo-master/* solo/
cd solo

 # docker server IP and listening port
vim   src/main/resources/latke.properties
serverHost=192.168.1.111
serverPort=80

# upload the code
git add .
git commit  -m "all"
git push origin  master
```

#### Build a base image

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

#### Start jenkins

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

#### Upload the tomcat base image to the harbor server

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
Start and configure jdk, git, maven

Plugins - Advanced    https://updates.jenkins.io/update-center.json
```

```shell
Configure Credentials -- (global) -- Add Credentials
SSH Username with private key
root
From the Jenkins master ~/.ssh
Configure passwordless login to the docker server: Manage Jenkins -- System settings --
SSH remote
hosts
192.168.1.111 22root(docker)
```

### Create a job

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

### Build
