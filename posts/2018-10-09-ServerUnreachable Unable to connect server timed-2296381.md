---
title: "ServerUnreachable Unable to connect server: timed"
date: "2018-10-09 16:57:59"
category: "python"
source: "https://blog.51cto.com/hequan/2296381"
---

阿里云 创建主机
报错:

```
SDK.ServerUnreachable Unable to connect server: timed out
```

原因:

```
ECS创建实例（CreateInstance请求）的最长等待时间为90秒，

但SDK对所有类型的请求均设置了一个固定的超时时间

（Java SDK为15秒，Python SDK为10秒，.NET SDK为100秒， PHP SDK超时时间不详）。

所以，当某次ECS CreateInstance请求的执行时间超过上述SDK超时时间设置后，timeout错误就发生了。

这个问题是SDK的一个已知问题。

阿里云计划在未来的版本中修正这个问题。

现在，解决这个问题的办法是对SDK设置一个合适的超时时间
```

解决办法：

```
# 把超时时间 延长
createclt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region_id, timeout=30)
```
