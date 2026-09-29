---
title: "Sending Email with Python: Sina Basic Version | Zabbix Version"
date: "2017-06-19 15:59:49"
category: "python"
source: "https://blog.51cto.com/hequan/1939844"
lang: "en"
---
> **About this post**
>
> This post presents two snippets that send email through Sina Mail's
> SMTP_SSL (port 465) using the Python standard library smtplib. The first
> is a minimal Sina basic version: a function that, once logged in, sends a
> plain-text email. The second builds on it by adding try/except to report
> whether the send succeeded, and switches to sys.argv to receive the
> recipient, subject, and content as three arguments, so it can be placed
> directly in the Zabbix alert script directory and invoked by alert actions
> as a media-type script.

> **Technical notes**
>
> Two timeliness reminders: Sina Mail now requires enabling the SMTP service
> in the web settings and using an "authorization code" instead of the login
> password as the pwd argument. The SMTP server address in
> `host_server = ''` was eaten by the editor when the original post was
> published and has been filled in as `smtp.sina.com` (SSL port 465)
> according to Sina's official documentation. For Zabbix 3.4+, the alert
> script directory is usually /usr/lib/zabbix/alertscripts or
> share/zabbix/alertscripts under the installation directory, depending on
> how Zabbix was installed.

---

## 1. Sina Basic Version

```python
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

def send_mail(sender_sina='', pwd='', receiver='', mail_title='', mail_content=''):
    # SMTP server of the mailbox
    host_server = 'smtp.sina.com'       # left empty in the original; filled in per Sina's official docs
    sender_sina_mail = sender_sina + '@sina.com'
    # SSL login
    smtp = SMTP_SSL(host_server)
    # set_debuglevel() is for debugging. 1 turns on debug mode, 0 turns it off
    smtp.set_debuglevel(0)
    smtp.ehlo(host_server)
    smtp.login(sender_sina, pwd)
    msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_sina_mail
    msg["To"] = receiver
    smtp.sendmail(sender_sina_mail, receiver, msg.as_string())
    smtp.quit()

send_mail("hequan2011", "密码", "hequan2011@sina.com", "标题", '内容')
```

## 2. Zabbix Version

As a Zabbix alert script, it receives the recipient, subject, and content in order via positional arguments:

```python
#!/usr/bin/python
#coding:utf-8
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import sys

def send_mail(sender_sina='', pwd='', receiver='', mail_title='', mail_content=''):
    host_server = 'smtp.sina.com'       # left empty in the original; filled in per Sina's official docs
    sender_sina_mail = sender_sina + '@sina.com'
    # SSL login
    smtp = SMTP_SSL(host_server)
    # set_debuglevel() is for debugging. 1 turns on debug mode, 0 turns it off
    smtp.set_debuglevel(0)
    smtp.ehlo(host_server)
    smtp.login(sender_sina, pwd)
    try:
        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_sina_mail
        msg["To"] = receiver
        smtp.sendmail(sender_sina_mail, receiver, msg.as_string())
        smtp.quit()
        print("发送成功")
        return True
    except Exception as e:
        print("发送失败：", e)
        return False

if __name__ == "__main__":
    #send_mail("hequan2011","password","hequan2011@sina.com","title",'content')
    send_mail("hequan2011", "密码", sys.argv[1], sys.argv[2], sys.argv[3])
```
