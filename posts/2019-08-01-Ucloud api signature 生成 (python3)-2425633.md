---
title: "Ucloud  api  signature 生成  (python3)"
date: "2019-08-01 15:11:54"
category: "python"
source: "https://blog.51cto.com/hequan/2425633"
---
> **内容介绍**
>
> 本文是Python 编程实战笔记,记录了「Ucloud  api  signature 生成  (python3)」的相关内容。

---

```pythonimport
hashlib

def _verfy_ac(private_key, params):
    items = sorted(params.items(), key=lambda x: x[0])
    params_data = ""
    for i in items:
        params_data = params_data + i[0] + i[1]
    params_data = params_data + private_key

    sign = hashlib.sha1()
    sign.update(params_data.encode("utf8"))
    signature = sign.hexdigest()

    return signature

s = _verfy_ac("私钥", {
    "Action": "DescribeImage",
    "PublicKey": "公钥",
    "OsType": "Linux",
    "Region": "cn-bj2"
})

print(s)
```
