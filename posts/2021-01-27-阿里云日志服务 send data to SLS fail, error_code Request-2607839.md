---
title: "阿里云日志服务 send data to SLS fail, error_code:Request"
date: "2021-01-27 11:39:01"
category: "集群"
source: "https://blog.51cto.com/hequan/2607839"
---

```
send data to SLS fail, error_code:RequestError	error_message:address is null.	endpoint:http://
```

```
解决办法:
修改 /usr/local/ilogtail/user_log_config.json

 "defaultEndpoint" :   默认是私网，改成公网域名
 
 然后重启服务即可。
 
  sudo /etc/init.d/ilogtaild stop
  sudo /etc/init.d/ilogtaild start
 
```

![](assets/2607839/01_e1b84e5836dd9fa186002f3292e85c39.jpg)
