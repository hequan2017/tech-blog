---
title: "Generating UCloud API signatures (python3)"
date: "2019-08-01 15:11:54"
category: "python"
source: "https://blog.51cto.com/hequan/2425633"
lang: "en"
---
> **About this post**
>
> This post provides a Python3 function, _verfy_ac, for generating the digital signature of UCloud
> public cloud API requests: sort the request parameters by key, concatenate key+value in order,
> append the private key at the end, encode the whole string as UTF-8 and take the SHA1 hash; the
> resulting hexadecimal digest is the Signature parameter. At the end, a DescribeImage (query
> images) request is used as an example to demonstrate the call and its output.

> **Technical notes**
>
> The signing rules match the official UCloud API documentation (sorted parameter concatenation +
> private key + SHA1); the function name _verfy_ac is spelled exactly as in the official SDK and is
> not a typo — do not "fix" it.
> In the example, Region cn-bj2 is Beijing Zone 2; for new projects it is recommended to use the
> official ucloud-sdk-python3 directly, which has the signing logic built in.

---

## 1. Signature generation function

Every UCloud API request must carry a Signature parameter. The algorithm is as follows:

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
