---
title: "Ucloud  api  signature 生成  (python3)"
date: "2019-08-01 15:11:54"
category: "python"
source: "https://blog.51cto.com/hequan/2425633"
---
> **内容介绍**
>
> 本文给出 UCloud 公有云 API 数字签名的 Python3 生成函数 _verfy_ac:
> 把请求参数按 key 排序后依次拼接 key+value,末尾再拼上私钥,整体按
> UTF-8 编码后取 SHA1,得到的十六进制摘要即 Signature 参数。文末以
> DescribeImage(查询镜像)请求为例演示调用与输出。

> **技术备注**
>
> 签名规则与 UCloud 官方 API 文档一致(参数排序拼接 + 私钥 + SHA1);
> 函数名 `_verfy_ac` 的拼写与官方 SDK 相同,并非笔误,请勿"修正"。
> 示例中 Region cn-bj2 为北京二区;新项目接入建议直接使用官方
> ucloud-sdk-python3,签名逻辑已内置。

---

## 1. 签名生成函数

UCloud API 每个请求都要带 Signature 参数,算法如下:

```python
import hashlib

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
