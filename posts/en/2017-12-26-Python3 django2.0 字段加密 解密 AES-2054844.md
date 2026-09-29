---
title: "Python3 Django 2.0 Field Encryption/Decryption with AES"
date: "2017-12-26 17:40:05"
category: "python"
source: "https://blog.51cto.com/hequan/2054844"
lang: "en"
---
> **About this post**
>
> This post provides two reversible encryption/decryption implementations for
> sensitive Django model fields: for Python 3.5 and earlier, use AES in CBC
> mode via pycrypto, wrapped in an AESCipher class with built-in padding
> (pad/unpad) and base64 encoding; from Python 3.6 on, switch to Fernet
> symmetric encryption from the cryptography library, with two functions
> encrypt_p / decrypt_p that can be used directly to encrypt fields such as
> passwords before storing them and restore them after reading.

> **Technical notes**
>
> - pycrypto has long been unmaintained; consider switching to its compatible
>   fork `pycryptodome` (`pip install pycryptodome`; the `from Crypto...`
>   import style stays the same).
> - Django 2.0 reached end of life in April 2019, and Python 3.5 / 3.6 are
>   both EOL as well.
> - The Fernet key hardcoded in the source is for demonstration only; in
>   production it should go into environment variables or a configuration
>   center. Django's built-in `django.core.signing` can also be used for
>   reversible field encryption.

---

## 1. Python 3.5 and earlier: pycrypto + AES

Installation:

```shell
pip install pycrypto
```

Code:

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

## 2. Python 3.6: cryptography + Fernet

Installation:

```shell
pip install cryptography
```

Code:

```python
from cryptography.fernet import Fernet

# key = base64.urlsafe_b64encode(os.urandom(32))  generate key

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
