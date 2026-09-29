---
title: "Alibaba Cloud Log Service: send data to SLS fail, error_code:Request"
date: "2021-01-27 11:39:01"
category: "cluster"
source: "https://blog.51cto.com/hequan/2607839"
lang: "en"
---
> **About this post**
>
> How to fix the failure when sending data to Alibaba Cloud Log Service (SLS) with the error `address is null`: the cause is that `ilogtail` uses the private-network endpoint by default; in cross-network or public-network environments, change `defaultEndpoint` in `user_log_config.json` to the public domain name, then restart the `ilogtaild` service.

> **Technical notes**
>
> This example is based on the legacy configuration of Alibaba Cloud Logtail (formerly ilogtail); newer Logtail versions support configuring the endpoint directly via the console or environment variables, and managing the service with `systemctl` is recommended. A public endpoint incurs internet traffic charges, so in intranet environments prefer a private or VPC endpoint.

---

```shell
send data to SLS fail, error_code:RequestError	error_message:address is null.	endpoint:http://
Edit /usr/local/ilogtail/user_log_config.json

 "defaultEndpoint" :   private network by default, change it to the public domain name

 Then restart the service.

  sudo /etc/init.d/ilogtaild stop
  sudo /etc/init.d/ilogtaild start

```

![Alibaba Cloud Log Service overview page, with the public access domain name marked in a red box](../assets/2607839/01_e1b84e5836dd9fa186002f3292e85c39.jpg)
