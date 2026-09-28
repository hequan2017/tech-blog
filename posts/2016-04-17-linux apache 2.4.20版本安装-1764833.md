---
title: "linux apache 2.4.20版本安装"
date: "2016-04-17 20:48:01"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764833"
---
> **内容介绍**
>
> 本文记录在 CentOS 6.7（64 位）上源码编译安装 Apache httpd 2.4.20 的完整过程:
> 先 yum 安装 gcc、gcc-c++、make、zlib-devel 等基础依赖,并说明 apr、apr-util、
> apr-iconv 三个依赖包各自的作用;再依次编译安装 apr 1.5.2、apr-iconv 1.2.1、
> apr-util 1.5.4 与 pcre 8.38;然后以 --enable-deflate/expires/headers/rewrite、
> --enable-modules=most、--with-mpm=worker 等参数编译 httpd 2.4.20,最后用
> apachectl -v 验证版本、启动服务,并在 /etc/sysconfig/iptables 中放行 80 端口。

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护（EOL）;Apache 2.4.20 为 2016 年版本,此后
> 2.4.x 修复了多个安全漏洞,生产环境应使用最新的 2.4.x。文中的镜像下载直链已
> 全部失效,Apache 系列源码包可从官方归档 archive.apache.org 获取。防火墙部分
> 的 iptables 语法仅适用于启用 iptables 服务的系统,新发行版默认为 firewalld。

---

## 1. 环境与基础依赖

centos 6.7_64 位,apache 2.4.20 版本。

```shell
yum install gcc gcc-c++ make uuid-devel libuuid-devel unzip zlib-devel zlib -y
```

三个 apr 系列依赖包的作用:

- apr:包含了一些通用的开发组件,包括 mmap、DSO 等等
- apr-util:该目录中也是包含了一些常用的开发组件。这些组件与 apr 目录下的相比,它们与 apache 的关系更加密切一些。比如存储段和存储段组,加密等等。
- apr-iconv:包中的文件主要用于实现 iconv 编码。目前的大部分编码转换过程都是与本地编码相关的。在进行转换之前必须能够正确地设置本地编码。因此假如两个非本地编码 A 和 B 需要转换,则转换过程大致为 A->Local 以及 Local->B,或者 B->Local 以及 Local->A。

安装 apache 依赖关联包（共四个:apr、apr-iconv、apr-util、pcre）。

## 2. 安装依赖包

### （1）安装 apr

```shell
# 原文镜像直链已失效,可改用官方归档地址:
# wget https://archive.apache.org/dist/apr/apr-1.5.2.tar.gz
tar zxvf apr-1.5.2.tar.gz
cd apr-1.5.2
./configure --prefix=/usr/local/apr
make && make install
```

### （2）安装 apr-iconv

```shell
# wget https://archive.apache.org/dist/apr/apr-iconv-1.2.1.tar.gz
tar -zxvf apr-iconv-1.2.1.tar.gz
cd apr-iconv-1.2.1
./configure --prefix=/usr/local/apr-iconv --with-apr=/usr/local/apr
make && make install
```

### （3）安装 apr-util

```shell
# wget https://archive.apache.org/dist/apr/apr-util-1.5.4.tar.gz
tar zxvf apr-util-1.5.4.tar.gz
cd apr-util-1.5.4
./configure --prefix=/usr/local/apr-util --with-apr=/usr/local/apr \
    --with-apr-iconv=/usr/local/apr-iconv/bin/apriconv
make && make install
```

### （4）安装 pcre

```shell
# 原文使用 sourceforge 镜像 IP 直链下载 pcre-8.38.zip,现已失效,
# 可到 https://sourceforge.net/projects/pcre/files/pcre/8.38/ 自行下载
unzip -o pcre-8.38.zip
cd pcre-8.38
./configure --prefix=/usr/local/pcre
make && make install
```

## 3. 编译安装 httpd 2.4.20

下载源码包（约 8.0M）:

```shell
# wget https://archive.apache.org/dist/httpd/httpd-2.4.20.tar.gz
ls httpd-2.4.20.tar.gz -sh
# 8.0M httpd-2.4.20.tar.gz

tar zxvf httpd-2.4.20.tar.gz
cd httpd-2.4.20
```

源码包自带的说明文件:

```shell
ll INSTALL README
```

```text
-rw-r--r-- 1 501 games 3781 10月 14 2015 INSTALL   安装
-rw-r--r-- 1 501 games 4642 1月  24 2014 README    说明
```

INSTALL 文档给出的快速安装三步:

```shell
./configure --prefix=PREFIX
make
make install
PREFIX/bin/apachectl start
```

正式编译（完整参数）:

```shell
./configure \
--prefix=/application/apache2.4.20 \
--enable-deflate \
--enable-expires \
--enable-headers \
--enable-modules=most \
--enable-so \
--with-mpm=worker \
--enable-rewrite \
--with-apr=/usr/local/apr \
--with-apr-util=/usr/local/apr-util \
--with-pcre=/usr/local/pcre
make && make install
```

## 4. 版本确认与启动

查看版本信息:

```shell
/application/apache2.4.20/bin/apachectl -v
```

```text
Server version: Apache/2.4.20 (Unix)
```

启动:

```shell
/application/apache2.4.20/bin/apachectl start
```

## 5. 防火墙放行 80 端口

```shell
vi /etc/sysconfig/iptables
```

在 `:OUTPUT ACCEPT [0:0]` 这行后面添加:

```text
-A OUTPUT -p tcp --sport 80 -j ACCEPT
-A INPUT -p tcp --dport 80 -j ACCEPT
```
