---
title: "sendEmail报错：at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm"
date: "2016-07-06 15:52:06"
category: "zabbix"
source: "https://blog.51cto.com/hequan/1811246"
---
> **内容介绍**
>
> 本文处理 Zabbix 告警邮件脚本 sendEmail 在 CentOS 7.2 上的报错 "invalid SSL_version
> specified at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm":先贴完整报错(含
> SSL_verify_mode 弃用警告),再引用 sendEmail 官方 FAQ 说明原因是 perl 版本差异
> (CentOS 7.2 自带 5.16,CentOS 6.5 为 5.10),最后给出解决办法:源码编译安装
> perl 5.10.0 到 /usr/local/perl,备份并软链替换 /usr/bin/perl,降级后即可正常发信。

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护(EOL),生产环境建议迁移至 Rocky Linux / AlmaLinux / Ubuntu LTS。
> 整机降级 perl 影响面大,更稳妥的做法是直接改 /usr/bin/sendEmail 第 1906 行左右,把
> `SSL_version => 'SSLv3 TLSv1'` 改为 `'TLSv1'`(新版 IO::Socket::SSL 已移除 SSLv3);
> 如今告警邮件也常用 mailx/msmtp 或 Python 脚本替代 sendEmail。

---

## 1. 报错现象

sendEmail 发邮件的时候,出现如下报错:

```shell
*******************************************************************
 Using the default of SSL_verify_mode of SSL_VERIFY_NONE for client
 is deprecated! Please set SSL_verify_mode to SSL_VERIFY_PEER
 together with SSL_ca_file|SSL_ca_path for verification.
 If you really don't want to verify the certificate and keep the
 connection open to Man-In-The-Middle attacks please set
 SSL_verify_mode explicitly to SSL_VERIFY_NONE in your application.
*******************************************************************
  at /usr/bin/sendEmail line 1906.
invalid SSL_version specified at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm line 415.
```

## 2. 原因:官方 FAQ 与 perl 版本差异

查阅了很多资料,在 sendEmail 官网 <http://caspian.dotconf.net/menu/Software/SendEmail/> 上找到了下面这段话:

**Q:** I get the error "invalid SSL_version specified at /System/Library/Perl/Extras/5.16/IO/Socket/SSL.pm line 332.a on my Apple. What do I do?

**A:** Here's what I got from one user. It's a workaround until I put a real fix in:

> Fixed it by using Perl v5.12 that's still on OSX Mavericks.
> (just changed sendEmail line 1 from `#!/usr/bin/perl -w` to `#!/usr/bin/perl5.12 -w`)

centos7.2 默认是 perl 的版本是 5.16,centos6.5 的是 5.10,后来把 7 的版本换成 5.10,就可以正常发邮件了。

## 3. 解决:安装 perl 5.10.0

```shell
#### perl安装
     wget http://www.cpan.org/src/5.0/perl-5.10.0.tar.gz
     tar -zxf perl-5.10.0.tar.gz
     cd perl-5.10.0
     ./configure.gnu -des -Dprefix=/usr/local/perl
     echo $?
     make
     make test
     make install
     mv /usr/bin/perl /usr/bin/perl.bak
     ln -s /usr/local/perl/bin/perl /usr/bin/perl
     perl -v
```
