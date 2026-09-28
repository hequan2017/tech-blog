---
title: "Python3  django2.0  字段加密 解密 AES"
date: "2017-12-26 17:40:05"
category: "python"
source: "https://blog.51cto.com/hequan/2054844"
---
> **内容介绍**
>
> 本文提供 Django 模型敏感字段的两套可逆加解密实现：Python 3.5 及以前
> 使用 pycrypto 的 AES CBC 模式，封装 AESCipher 类，自带补位（pad/unpad）
> 与 base64 编码；Python 3.6 起改用 cryptography 库的 Fernet 对称加密，
> 给出 encrypt_p / decrypt_p 两个函数，可直接用于密码等字段入库前加密、
> 读出后还原。

> **技术备注**
>
> - pycrypto 早已停止维护，建议改装其兼容分支 `pycryptodome`
>   （`pip install pycryptodome`，`from Crypto...` 导入方式不变）。
> - Django 2.0 已于 2019 年 4 月停止支持，Python 3.5 / 3.6 也均已 EOL。
> - 文中 Fernet 密钥硬编码在源码里仅作演示，生产环境应放入环境变量或
>   配置中心；另 Django 自带 `django.core.signing` 亦可做可逆字段加密。

---

## 1. Python 3.5 及以前：pycrypto + AES

安装：

```shell
pip install pycrypto
```

代码：

```python
import base64
from Crypto.Cipher import AES
from Crypto import Random

BS = 16
key = "1234567890123456"
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.urlsafe_b64decode(enc.encode('utf-8'))
        iv = enc[:BS]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[BS:]))

a = AESCipher(key=key)
b = a.encrypt(raw='123456')
b1 = b.decode()
print(b1,type(b),type(b1))

c = a.decrypt(enc='N4wGyzPTnggQtUr_gyGcsxMzU136thzPIc8y3mJ2uxg=')
print(c)
```

## 2. Python 3.6 版本：cryptography + Fernet

安装：

```shell
pip install cryptography
```

代码：

```python
from cryptography.fernet import Fernet

# key = base64.urlsafe_b64encode(os.urandom(32))  生成key

def  encrypt_p(password):
        f = Fernet('Ow2Qd11KeZS_ahNOMicpWUr3nu3RjOUYa0_GEuMDlOc=')
        p1 = password.encode()
        token = f.encrypt(p1)
        p2 = token.decode()
        return   p2

def  decrypt_p(password):
        f = Fernet('Ow2Qd11KeZS_ahNOMicpWUr3nu3RjOUYa0_GEuMDlOc=')
        p1 = password.encode()
        token = f.decrypt(p1)
        p2 = token.decode()
        return p2
```
