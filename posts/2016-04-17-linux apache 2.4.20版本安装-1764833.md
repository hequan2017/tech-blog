---
title: "linux apache 2.4.20版本安装"
date: "2016-04-17 20:48:01"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764833"
---
> **内容介绍**
>
> 本文是Linux 系统运维笔记,记录了「linux apache 2.4.20版本安装」的相关内容。主要涉及:centos 6.7_64位 apache 2.4.20版本 apr中包含了一些通用的开发组件，包括mmap，DSO等等 apr-util该目录中也是包含了一些…

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护(EOL),生产环境建议迁移至 Rocky Linux / AlmaLinux / Ubuntu LTS。

---

centos  6.7_64位                apache 2.4.20版本

```bash
yum install   gcc     gcc-c++   make    uuid-devel    libuuid-devel    unzip  zlib-devel zlib  -y
```

apr中包含了一些通用的开发组件，包括mmap，DSO等等

apr-util该目录中也是包含了一些常用的开发组件。这些组件与apr目录下的相比，它们与apache的关系更加密切一些。比如存储段和存储段组，加密等等。

apr-iconv包中的文件主要用于实现iconv编码。目前的大部分编码转换过程都是与本地编码相关的。在进行转换之前必须能够正确地设置本地编码。因此假如两个非本地编码A和B需要转换，则转换过程大致为A->Local以及Local->B或者B->Local以及Local->A。

**安装 apache 依赖关联包（共四个：apr，apr-iconv，apr-util，pcre）**

**（1）、安装apr**

```bash
wget http:////apr/apr-1.5.2.tar.gz
tar zxvf apr-1.5.2.tar.gz
cd apr-1.5.2
 ./configure --prefix=/usr/local/apr
make   &&   make install
```

**（2）、安装apr-iconv**

```bash
wget http:////apr/apr-iconv-1.2.1.tar.gz
tar -zxvf apr-iconv-1.2.1.tar.gz
cd apr-iconv-1.2.1
 ./configure --prefix=/usr/local/apr-iconv --with-apr=/usr/local/apr
make   &&   make install
```

**（3）、安装apr-util**

```bash
wget http:///apache//apr/apr-util-1.5.4.tar.gz
tar zxvf apr-util-1.5.4.tar.gz
cd apr-util-1.5.4
./configure --prefix=/usr/local/apr-util  --with-apr=/usr/local/apr    --with-apr-iconv=/usr/local/apr-iconv/bin/apriconv
make    &&   make install
```

**（4）、安装 pcre**

```bash
wget  http://120.52.73.44/nchc.dl.sourceforge.net/project/pcre/pcre/8.38/pcre-8.38.zip
unzip  -o pcre-8.38.zip
cd pcre-8.38
./configure --prefix=/usr/local/pcre
make    &&   make install
```

**开始正式安装apache**

```bash
wget   http:///apache/httpd/httpd-2.4.20.tar.gz
```

**[http:///apache/httpd/httpd-2.4.20.tar.gz](http:///apache/httpd/httpd-2.4.20.tar.gz)**

# ls httpd-2.4.20.tar.gz -sh

8.0M httpd-2.4.20.tar.gz

```bash
tar  zxvf   httpd-2.4.20.tar.gz
```

**[http:///apache/httpd/httpd-2.4.20.tar.gz](http:///apache/httpd/httpd-2.4.20.tar.gz)**

```bash
cd httpd-2.4.20
```

# ll INSTALL README

-rw-r--r-- 1 501 games 3781 10月 14 2015 INSTALL  安装

-rw-r--r-- 1 501 games 4642 1月  24 2014 README   说明

$ ./configure --prefix=PREFIX

$ make

$ make install

$ PREFIX/bin/apachectl start

```bash
./configure \
--prefix=/application/apache2.4.20  \
--enable-deflate \
--enable-expires  \
--enable-headers  \
--enable-modules=most \
--enable-so \
--with-mpm=worker \
--enable-rewrite \
--with-apr=/usr/local/apr \
--with-apr-util=/usr/local/apr-util \
--with-pcre=/usr/local/pcre
make  && make install
```

版本信息

/application/apache2.4.20/bin/**apachectl -v**

Server version: Apache/2.4.20 (Unix)

启动

```bash
/application/apache2.4.20/bin/apachectl   start
```

防火墙

vi /etc/sysconfig/iptables

:OUTPUT ACCEPT [0:0]                在这后面

-A OUTPUT -p tcp --sport 80 -j ACCEPT

-A INPUT -p tcp --dport 80 -j ACCEPT
