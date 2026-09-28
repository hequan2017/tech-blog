---
title: "sendEmail报错：at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm"
date: "2016-07-06 15:52:06"
category: "zabbix"
source: "https://blog.51cto.com/hequan/1811246"
---
> **内容介绍**
>
> 本文是Zabbix 监控系统实践,记录了「sendEmail报错：at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm」的相关内容。主要涉及:sendEmail发邮件的时候，出现的报错，然后查阅了很多资料 在[http://caspian.dotconf.net/menu/Software/SendE…

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护(EOL),生产环境建议迁移至 Rocky Linux / AlmaLinux / Ubuntu LTS。

---

```bash
*******************************************************************
 Using the default of SSL_verify_mode of SSL_VERIFY_NONE for client
 is deprecated! Please set SSL_verify_mode to SSL_VERIFY_PEER
 together with SSL_ca_file|SSL_ca_path for verification.
 If you really don't want to verify the certificate and keep the
 connection open to Man-In-The-Middle attacks please set
 SSL_verify_mode explicitly to SSL_VERIFY_NONE in your application.
*******************************************************************
  at /usr/bin/sendEmail line 1906.
invalid SSL_version specified at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm line 415.
```

sendEmail发邮件的时候，出现的报错，然后查阅了很多资料

在[http://caspian.dotconf.net/menu/Software/SendEmail/](http://caspian.dotconf.net/menu/Software/SendEmail/)

上找到了 下面这段话

**Q:** I get the error "invalid SSL_version specified at /System/Library/Perl/Extras/5.16/IO/Socket/SSL.pm line 332.a on my Apple. What do I do?
**A:** Here's what I got from one user. It's a workaround until I put a real fix in:

> Fixed it by using Perl v5.12 that's still on OSX Mavericks. > (just changed sendEmail line 1 from #!/usr/bin/perl -w to #!/usr/bin/perl5.12 -w)

centos7.2默认是 perl的版本是5.16，centos6.5的是5.10，后来把7的版本换成5.10，就可以正常发邮件了。

```bash
#### perl安装
     wget http://www.cpan.org/src/5.0/perl-5.10.0.tar.gz
     tar -zxf perl-5.10.0.tar.gz
     cd perl-5.22.0
     ./configure.gnu -des -Dprefix=/usr/local/perl
     echo $?
     make
     make test
     make install
     mv /usr/bin/perl /usr/bin/perl.bak
     ln -s /usr/local/perl/bin/perl /usr/bin/perl
     perl -v
```
