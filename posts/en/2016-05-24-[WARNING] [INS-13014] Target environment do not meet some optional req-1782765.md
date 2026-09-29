---
title: "[WARNING] [INS-13014] Target environment do not meet some optional requirements."
date: "2016-05-24 23:16:29"
category: "Linux"
source: "https://blog.51cto.com/hequan/1782765"
lang: "en"
---
> **About this post**
>
> This post documents the troubleshooting process for the [INS-13014] warning
> that appears during an Oracle installation: by inspecting the installActions
> log, it pinpoints a failed swap space check (PRVF-7575) and missing
> dependency packages such as compat-libstdc++-33, libaio-devel, libgcc,
> unixODBC-devel, and pdksh.

> **Technical notes**
>
> INS-13014 is merely a summary warning that "some optional prerequisites are
> not met"; items with Severity IGNORABLE in the log can be skipped by
> checking Ignore All in the installer UI. Since RHEL/CentOS 6, the official
> repositories no longer ship pdksh — installing ksh satisfies that check.
> The i386 (32-bit) dependencies are a legacy requirement of Oracle 11g
> x86_64; on modern systems it is recommended to install the matching
> oracle preinstall RPM to set up all dependencies and kernel parameters in
> one shot.

---

## 1. Installation Warning

Oracle reports the following warning:

```bash
[WARNING] [INS-13014] Target environment do not meet some optional requirements.
   CAUSE: Some of the optional prerequisites are not met. See logs for details. /opt/logs/installActions2014-02-12_11-09-40AM.log
   ACTION: Identify the list of failed prerequisite checks from the log: /opt/logs/installActions2014-02-12_11-09-40AM.log. Then either from the log file or from installation manual find the appropriate configuration to meet the prerequisites and fix it manually.
You can find the log of this install session at:
 /opt/logs/installActions2014-02-12_11-09-40AM.log
```

## 2. Log Analysis

The log shows that some packages are missing and the swap space is too small.

```bash
INFO: 交换空间大小: 此先决条件将测试系统是否具有足够的总交换空间。
INFO: Severity:IGNORABLE
INFO: OverallStatus:OPERATION_FAILED

INFO: Verification Result for Node:DB_2
WARNING: 此验证任务没有结果值
INFO: Error Message:PRVF-7575 : 出现内部错误。未正确定义用于验证交换空间大小的引用数据的范围
INFO: Cause: 无法根据可用物理内存确定交换空间大小。
INFO: Action: 这是应向 Oracle 报告的内部错误。

INFO: 包: compat-libstdc++-33-3.2.3: 此先决条件将测试系统是否具有程序包 "compat-libstdc++-33-3.2.3"。
INFO: Severity:IGNORABLE
INFO: OverallStatus:VERIFICATION_FAILED

INFO: Verification Result for Node:DB_2
INFO: Expected Value:libaio-devel-0.3.105 (i386)
INFO: Actual Value:缺失
INFO: Error Message:PRVF-7532 : 节点 "DB_2" 上缺少程序包 "libaio-devel-0.3.105 (i386)"
INFO: Cause: 指定的节点上未安装必需的程序包; 或者如果该程序包是内核模块, 则未加载该程序包。
INFO: Action: 确保必需的程序包已安装且可用。

INFO: 包: libgcc-3.4.6: 此先决条件将测试系统是否具有程序包 "libgcc-3.4.6"。
INFO: Severity:IGNORABLE
INFO: OverallStatus:VERIFICATION_FAILED

INFO: Verification Result for Node:DB_2
INFO: Expected Value:libgcc-3.4.6 (i386)
INFO: Actual Value:缺失
INFO: Error Message:PRVF-7532 : 节点 "DB_2" 上缺少程序包 "libgcc-3.4.6 (i386)"
...skipping...
INFO: OverallStatus:VERIFICATION_FAILED

INFO: Verification Result for Node:DB_2
INFO: Expected Value:unixODBC-devel-2.2.11 (i386)
INFO: Actual Value:缺失
INFO: Error Message:PRVF-7532 : 节点 "DB_2" 上缺少程序包 "unixODBC-devel-2.2.11 (i386)"
INFO: Cause: 指定的节点上未安装必需的程序包; 或者如果该程序包是内核模块, 则未加载该程序包。
INFO: Action: 确保必需的程序包已安装且可用。

INFO: 包: pdksh-5.2.14: 此先决条件将测试系统是否具有程序包 "pdksh-5.2.14"。
INFO: Severity:IGNORABLE
INFO: OverallStatus:VERIFICATION_FAILED
```
