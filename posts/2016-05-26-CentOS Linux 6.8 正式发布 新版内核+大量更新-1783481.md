---
title: "CentOS Linux 6.8 正式发布 新版内核+大量更新"
date: "2016-05-26 15:27:54"
category: "Linux"
source: "https://blog.51cto.com/hequan/1783481"
---
> **内容介绍**
>
> 本文是Linux 系统运维笔记,记录了「CentOS Linux 6.8 正式发布 新版内核+大量更新」的相关内容。主要涉及:**摘要：**CentOS开发人员兼维护者Johnny Hughes于5月25号宣布了CentOS Linux 6.8操作系统已经正式发布的消息。其基于红帽6.…

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护(EOL),生产环境建议迁移至 Rocky Linux / AlmaLinux / Ubuntu LTS。

---

**摘要：**CentOS开发人员兼维护者Johnny Hughes于5月25号宣布了CentOS Linux 6.8操作系统已经正式发布的消息。其基于红帽6.8企业版（RHEL）打造，并迎来了多处改动，比如最新的Linux 2.6.32内核，支持在XFS文件系统上存储高达300TB的数据；网络连接管理实用工具NetworkManager中的虚拟专用网终端解决方案，现已提供libreswan库（而不是此前所使用的Openswan IPsec）。

![CentOS 6.8 LiveCD 的 GNOME 桌面截图](assets/1783481/01_975B8AFA944E1B54FE97F6011325DAAE.jpg)

系统安全服务守护程序（SSSD）似乎默认禁用了SSLv2协议，此外还支持智能卡。Johnny Hughes在公告中称：

> 与此前的CentOS Linux 6相比，本次发行版中有许多根本性的变化，所有6.8上流发行版的镜像均已零时差更新。你可以通过各种媒介安装CentOS 6.8，并在安装完成后经常运行“yum update”。

![CentOS 6.8 终端执行 uname 查询系统版本信息](assets/1783481/02_496CEE008842F1F7632B9457892DC2AC.jpg)

CentOS Linux 6.8还包含了许多应用程序的更新，其中包括长期支持的LibreOffice 4.3.7办公套件、Squid 3.4缓存、以及转发网络代理。

此外，许多应用现已支持TLS 1.2（安全传输层协议），如Git、YUM、Postfix、OpenLDAP、stunnel和vsftpd。其它方面：

以人类可读格式查看计算机DMI表内容的“dmidecode”开源工具（查看硬件信息），现已支持SMBIOS 3.0.0；

> 可从HTTPS来源获取kickstart文件，NTPd（网络时间协议守护进程）包有一个可选的解决方案（像chrony一样）；
>
> SSLv3（终于）默认已被禁用以保障用户安全，最后就是更好的Hyper-V支持。

**下载地址：**

https://www.centos.org/download/
