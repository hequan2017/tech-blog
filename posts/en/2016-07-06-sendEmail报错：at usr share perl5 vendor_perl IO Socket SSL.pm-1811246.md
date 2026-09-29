---
title: "sendEmail Error: at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm"
date: "2016-07-06 15:52:06"
category: "zabbix"
source: "https://blog.51cto.com/hequan/1811246"
lang: "en"
---
> **About this post**
>
> This post deals with the error "invalid SSL_version
> specified at /usr/share/perl5/vendor_perl/IO/Socket/SSL.pm" thrown by the sendEmail
> alert-email script on CentOS 7.2: it first shows the full error (including the
> SSL_verify_mode deprecation warning), then cites the official sendEmail FAQ
> explaining that the cause is a perl version difference
> (CentOS 7.2 ships 5.16, CentOS 6.5 has 5.10), and finally gives the fix: build and
> install perl 5.10.0 from source into /usr/local/perl, back up /usr/bin/perl and
> replace it with a symlink; after the downgrade, emails are sent normally again.

> **Technical notes**
>
> CentOS 6 reached end of life (EOL) in November 2020; production environments are advised to migrate to Rocky Linux / AlmaLinux / Ubuntu LTS.
> Downgrading perl system-wide has a broad impact; a safer approach is to edit /usr/bin/sendEmail directly around line 1906, changing
> `SSL_version => 'SSLv3 TLSv1'` to `'TLSv1'` (newer IO::Socket::SSL releases have removed SSLv3);
> nowadays alert emails are also commonly sent with mailx/msmtp or Python scripts instead of sendEmail.

---

## 1. The error

When sending email with sendEmail, the following error appears:

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

## 2. Cause: the official FAQ and the perl version difference

After checking a lot of references, I found the following passage on the sendEmail official site <http://caspian.dotconf.net/menu/Software/SendEmail/>:

**Q:** I get the error "invalid SSL_version specified at /System/Library/Perl/Extras/5.16/IO/Socket/SSL.pm line 332.a on my Apple. What do I do?

**A:** Here's what I got from one user. It's a workaround until I put a real fix in:

> Fixed it by using Perl v5.12 that's still on OSX Mavericks.
> (just changed sendEmail line 1 from `#!/usr/bin/perl -w` to `#!/usr/bin/perl5.12 -w`)

The default perl version on CentOS 7.2 is 5.16, while CentOS 6.5 ships 5.10. After switching the version on 7 to 5.10, emails could be sent normally again.

## 3. Fix: install perl 5.10.0

```shell
#### perl installation
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
