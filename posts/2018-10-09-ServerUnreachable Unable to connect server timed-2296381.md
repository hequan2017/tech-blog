---
title: "ServerUnreachable Unable to connect server: timed"
date: "2018-10-09 16:57:59"
category: "python"
source: "https://blog.51cto.com/hequan/2296381"
---
> **内容介绍**
>
> 解决调用阿里云 SDK 创建 ECS 时报 `SDK.ServerUnreachable Unable to connect server: timed out` 的问题：旧版 SDK 对请求设置了固定的默认超时（Python SDK 为 10 秒），CreateInstance 这类慢请求容易超时，需要显式调大 timeout。

> **技术备注**
>
> 该问题针对旧版 aliyun-python-sdk；新版阿里云 V2 SDK 已支持通过 `config.connect_timeout` / `read_timeout` 配置超时，且有自动重试机制，一般不再需要手动处理。文中 `timeout=30` 的用法在旧版 core 中仍有效。

---

阿里云 创建主机
报错:

```text
SDK.ServerUnreachable Unable to connect server: timed out
```

原因:

旧版 SDK 对所有类型的请求均设置了一个固定的超时时间（Java SDK 为 15 秒，Python SDK 为 10 秒，.NET SDK 为 100 秒）。所以，当某次 ECS CreateInstance 请求的执行时间超过上述 SDK 超时时间设置后，timeout 错误就发生了。这个问题是 SDK 的一个已知问题。

解决办法：对 SDK 设置一个合适的超时时间。

```python
# 把超时时间延长
createclt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region_id, timeout=30)
```

