---
title: "ServerUnreachable Unable to connect server: timed"
date: "2018-10-09 16:57:59"
category: "python"
source: "https://blog.51cto.com/hequan/2296381"
---
> **内容介绍**
>
> 本文是Python 编程实战笔记,记录了「ServerUnreachable Unable to connect server: timed」的相关内容。主要涉及:阿里云 创建主机 报错: 原因:…

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

阿里云 创建主机
报错:

```shellSDK.ServerUnreachable Unable to connect server: timed out
```

原因:

```

但SDK对所有类型的请求均设置了一个固定的超时时间

（Java SDK为15秒，Python SDK为10秒，.NET SDK为100秒， PHP SDK超时时间不详）。

所以，当某次ECS CreateInstance请求的执行时间超过上述SDK超时时间设置后，timeout错误就发生了。

这个问题是SDK的一个已知问题。

阿里云计划在未来的版本中修正这个问题。

现在，解决这个问题的办法是对SDK设置一个合适的超时时间

解决办法：

```shell# 把超时时间 延长
createclt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region_id, timeout=30)

