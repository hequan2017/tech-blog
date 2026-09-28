---
title: "Python3  django2.0  字段加密 解密 AES"
date: "2017-12-26 17:40:05"
category: "python"
source: "https://blog.51cto.com/hequan/2054844"
---

以下设置，适用于python3.5及以前的

```
pip  install   pycrypto

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

python3.6版本的

```
pip install  cryptography

from cryptography.fernet import Fernet

##  key = base64.urlsafe_b64encode(os.urandom(32))  生成key

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
