---
title: "ServerUnreachable Unable to connect server: timed"
date: "2018-10-09 16:57:59"
category: "python"
source: "https://blog.51cto.com/hequan/2296381"
lang: "en"
---
> **About this post**
>
> How to fix the `SDK.ServerUnreachable Unable to connect server: timed out` error thrown when calling the Alibaba Cloud SDK to create an ECS instance: the legacy SDK sets a fixed default timeout on requests (10 seconds for the Python SDK), so slow requests such as CreateInstance tend to time out, and you need to explicitly raise the timeout.

> **Technical notes**
>
> This issue applies to the legacy aliyun-python-sdk; the newer Alibaba Cloud V2 SDK already supports configuring timeouts via `config.connect_timeout` / `read_timeout` and has a built-in automatic retry mechanism, so manual handling is generally no longer needed. The `timeout=30` usage in this post still works in the legacy core.

---

Creating an instance on Alibaba Cloud
The error:

```text
SDK.ServerUnreachable Unable to connect server: timed out
```

Cause:

The legacy SDK sets a fixed timeout for all types of requests (15 seconds for the Java SDK, 10 seconds for the Python SDK, and 100 seconds for the .NET SDK). Therefore, once the execution time of an ECS CreateInstance request exceeds the timeout configured in the SDK, the timeout error occurs. This is a known issue of the SDK.

Solution: set an appropriate timeout for the SDK.

```python
# Increase the timeout
createclt = client.AcsClient(self.AccessKeyId, self.AccessKeySecret, region_id, timeout=30)
```
