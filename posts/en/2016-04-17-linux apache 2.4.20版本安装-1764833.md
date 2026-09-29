---
title: "Installing Apache 2.4.20 on Linux"
date: "2016-04-17 20:48:01"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764833"
lang: "en"
---
> **About this post**
>
> This post documents the complete process of building Apache httpd 2.4.20 from source on CentOS 6.7 (64-bit):
> first installing base dependencies such as gcc, gcc-c++, make, and zlib-devel via yum, and explaining the roles
> of the three dependency packages apr, apr-util, and apr-iconv; then building and installing apr 1.5.2,
> apr-iconv 1.2.1, apr-util 1.5.4, and pcre 8.38 in turn; then compiling httpd 2.4.20 with options such as
> --enable-deflate/expires/headers/rewrite, --enable-modules=most, and --with-mpm=worker; and finally verifying
> the version with apachectl -v, starting the service, and opening port 80 in /etc/sysconfig/iptables.

> **Technical notes**
>
> CentOS 6 reached end of life (EOL) in November 2020; Apache 2.4.20 is a 2016 release, and since then the
> 2.4.x line has fixed multiple security vulnerabilities, so production environments should use the latest 2.4.x.
> The mirror download direct links in this post no longer work; Apache source packages can be obtained from the
> official archive at archive.apache.org. The iptables syntax in the firewall section applies only to systems
> with the iptables service enabled; newer distributions default to firewalld.

---

## 1. Environment and Base Dependencies

CentOS 6.7 64-bit, Apache 2.4.20.

```shell
yum install gcc gcc-c++ make uuid-devel libuuid-devel unzip zlib-devel zlib -y
```

The roles of the three apr-family dependency packages:

- apr: contains some common development components, including mmap, DSO, and so on.
- apr-util: this directory also contains some commonly used development components. Compared with those under the apr directory, they are more closely related to Apache itself — for example, buckets and bucket brigades, encryption, and so on.
- apr-iconv: the files in this package are mainly used to implement iconv encoding. Most current encoding conversion is tied to the local encoding; before converting, the local encoding must be set correctly. Therefore, if two non-local encodings A and B need to be converted, the process is roughly A->Local and Local->B, or B->Local and Local->A.

Install the four packages Apache depends on: apr, apr-iconv, apr-util, and pcre.

## 2. Installing the Dependency Packages

### (1) Installing apr

```shell
# The original mirror direct link is dead; use the official archive URL instead:
# wget https://archive.apache.org/dist/apr/apr-1.5.2.tar.gz
tar zxvf apr-1.5.2.tar.gz
cd apr-1.5.2
./configure --prefix=/usr/local/apr
make && make install
```

### (2) Installing apr-iconv

```shell
# wget https://archive.apache.org/dist/apr/apr-iconv-1.2.1.tar.gz
tar -zxvf apr-iconv-1.2.1.tar.gz
cd apr-iconv-1.2.1
./configure --prefix=/usr/local/apr-iconv --with-apr=/usr/local/apr
make && make install
```

### (3) Installing apr-util

```shell
# wget https://archive.apache.org/dist/apr/apr-util-1.5.4.tar.gz
tar zxvf apr-util-1.5.4.tar.gz
cd apr-util-1.5.4
./configure --prefix=/usr/local/apr-util --with-apr=/usr/local/apr \
    --with-apr-iconv=/usr/local/apr-iconv/bin/apriconv
make && make install
```

### (4) Installing pcre

```shell
# The original post downloaded pcre-8.38.zip from a SourceForge mirror IP direct link,
# which is now dead; get it yourself from https://sourceforge.net/projects/pcre/files/pcre/8.38/
unzip -o pcre-8.38.zip
cd pcre-8.38
./configure --prefix=/usr/local/pcre
make && make install
```

## 3. Compiling and Installing httpd 2.4.20

Download the source package (about 8.0 MB):

```shell
# wget https://archive.apache.org/dist/httpd/httpd-2.4.20.tar.gz
ls httpd-2.4.20.tar.gz -sh
# 8.0M httpd-2.4.20.tar.gz

tar zxvf httpd-2.4.20.tar.gz
cd httpd-2.4.20
```

Documentation files bundled with the source package:

```shell
ll INSTALL README
```

```text
-rw-r--r-- 1 501 games 3781 10月 14 2015 INSTALL   安装
-rw-r--r-- 1 501 games 4642 1月  24 2014 README    说明
```

The three quick-install steps given in the INSTALL document:

```shell
./configure --prefix=PREFIX
make
make install
PREFIX/bin/apachectl start
```

The actual build (full options):

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

## 4. Verifying the Version and Starting the Service

Check the version information:

```shell
/application/apache2.4.20/bin/apachectl -v
```

```text
Server version: Apache/2.4.20 (Unix)
```

Start it:

```shell
/application/apache2.4.20/bin/apachectl start
```

## 5. Opening Port 80 in the Firewall

```shell
vi /etc/sysconfig/iptables
```

Add the following after the `:OUTPUT ACCEPT [0:0]` line:

```text
-A OUTPUT -p tcp --sport 80 -j ACCEPT
-A INPUT -p tcp --dport 80 -j ACCEPT
```
