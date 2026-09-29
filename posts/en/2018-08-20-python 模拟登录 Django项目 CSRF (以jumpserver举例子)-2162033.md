---
title: "Simulating Login to a Django Project with CSRF in Python (a JumpServer Example)"
date: "2018-08-20 16:21:13"
category: "python"
source: "https://blog.51cto.com/hequan/2162033"
lang: "en"
---
> **About this post**
>
> Demonstrates simulating login to a CSRF-protected Django site with requests: first GET the login page and extract the `csrfmiddlewaretoken` with a regex, then submit the login form with the token, and afterwards reuse the same Session to call the user-list and create-user endpoints. JumpServer is used as the example, with configuration read from config.ini.

> **Technical notes**
>
> This applies to the form-based login of the Django 1.x/2.x era; newer JumpServer versions (2.x and later) have switched to REST API + Token/AccessKey authentication, so it is recommended to use the official API directly. The approach of requests plus regex extraction of the CSRF token still works for any Django form-based site.

---

### File Directory

- config.ini
- jumpserver.py

---

### config.ini

```ini
[local_environment]
title = Local Test Environment
url = http://192.168.100.28/
login_url= http://192.168.100.28/users/login/
user_url = http://192.168.100.28/users/user/
user_list_url= http://192.168.100.28/api/users/v1/users/
user_create_url = http://192.168.100.28/users/user/create/

username = admin
password = admin
```

### jumpserver.py

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import configparser
import socket
import requests
import json
import re

class Jumpserver(object):

    def __init__(self):
        self.header = {'Content-Type': "application/x-www-form-urlencoded"}
        self.lgconf = self.load_conf()
        self.r_session = requests.Session()
        self.reg = r"<input type='hidden' name='csrfmiddlewaretoken' value='(.+)' />"

    def load_conf(self):
        conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")

        if not os.path.exists(conf_path):
            raise Exception("config file is not exists! please filling configuration file")

        conf = configparser.ConfigParser()
        conf.read(conf_path)

        configmodel = 'product_environment' if socket.gethostname().endswith('product.com') else 'local_environment'

        if not conf.has_section(configmodel):
            raise Exception("There is no configuration file %s configuration items" % (configmodel))

        for para in ('url', 'username', 'password'):
            if not dict(conf.items(configmodel)).get(para):
                raise Exception("There is no '%s' parameter in the configuration item %s" % (para, configmodel))

        return dict(conf.items(configmodel))

    def login(self):
        try:
            request = self.r_session.get(self.lgconf.get('login_url'), headers=self.header, timeout=20)
            csrf, r_sessions = re.findall(self.reg, request.text)[0], self.r_session

            auth = {'username': self.lgconf.get('username'), 'password': self.lgconf.get('password'),
                    'csrfmiddlewaretoken': csrf}

            login_request = r_sessions.post(self.lgconf.get('login_url'), data=auth, headers=self.header, timeout=2,
                                            allow_redirects=True)
            if login_request.url == self.lgconf.get('url'):
                return True
            else:
                return False
        except Exception as e:
            print("Request url failed:%s" % (e))
            return

    def user_list(self):
        try:
            request = self.r_session.get(self.lgconf.get('user_list_url'), headers=self.header, timeout=20)
            return json.loads(request.text)
        except Exception as e:
            print("Request url failed:%s" % (e))
            return

    def user_create(self, data):
        try:
            request = self.r_session.get(self.lgconf.get('user_create_url'), headers=self.header, timeout=20)
            data['csrfmiddlewaretoken'] = re.findall(self.reg, request.text)[0]
            user_create_request = self.r_session.post(self.lgconf.get('user_create_url'), data=data,
                                                      headers=self.header,
                                                      timeout=20, allow_redirects=True)

            if user_create_request.url == self.lgconf.get('user_url'):
                return True
            else:
                return False
        except Exception as e:
            print("Request url failed:%s" % (e))
            return False

    def logout(self):
        try:
            request = self.r_session.get(self.lgconf.get('logout_url'), headers=self.header, timeout=20,
                                         allow_redirects=True)

            if request.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print("Logout url failed:%s" % (e))
            return

if __name__ == "__main__":
    http_request = Jumpserver()
    http_request.login()
    user_list = http_request.user_list()
    ret = http_request.user_create(
        data={'name': 'hequan', 'username': 'hequan', 'email': 'hequan@', 'otp_level': 0, 'role': 'User',
              'date_expired': '2088-08-02'})
    http_request.logout()
```
