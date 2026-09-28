---
title: "python 发邮件：sina普通版    |  zabbix版本"
date: "2017-06-19 15:59:49"
category: "python"
source: "https://blog.51cto.com/hequan/1939844"
---
> **内容介绍**
>
> 本文给出两段用 Python 标准库 smtplib 经新浪邮箱 SMTP_SSL(465 端口)发信
> 的代码:第一段是最小化的 sina 普通版函数,登录后即可发送纯文本邮件;第二段
> 在此基础上加 try/except 返回发送成败,并改用 sys.argv 接收收件人、标题、
> 内容三个参数,可直接放进 zabbix 告警脚本目录作为媒介脚本被告警动作调用。

> **技术备注**
>
> 两点时效提醒:新浪邮箱现在必须在网页版设置中开启 SMTP 服务,并使用"授权码"
> 而非登录密码作为 pwd 参数;代码中 `host_server = ''` 的 SMTP 服务器地址在
> 原文发布时被编辑器吃掉,已按新浪官方补全为 `smtp.sina.com`(SSL 端口
> 465)。zabbix 3.4+ 的告警脚本目录一般位于 /usr/lib/zabbix/alertscripts 或
> 安装目录下的 share/zabbix/alertscripts,视安装方式而定。

---

## 1. sina 普通版

```python
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

def send_mail(sender_sina='', pwd='', receiver='', mail_title='', mail_content=''):
    # 邮箱smtp服务器
    host_server = 'smtp.sina.com'       # 原文此处为空,已按新浪官方补全
    sender_sina_mail = sender_sina + '@sina.com'
    # ssl登录
    smtp = SMTP_SSL(host_server)
    # set_debuglevel()是用来调试的。参数值为1表示开启调试模式,参数值为0关闭调试模式
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

## 2. zabbix 版本

作为 zabbix 告警脚本,通过位置参数依次接收收件人、标题、内容:

```python
#!/usr/bin/python
#coding:utf-8
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import sys

def send_mail(sender_sina='', pwd='', receiver='', mail_title='', mail_content=''):
    host_server = 'smtp.sina.com'       # 原文此处为空,已按新浪官方补全
    sender_sina_mail = sender_sina + '@sina.com'
    # ssl登录
    smtp = SMTP_SSL(host_server)
    # set_debuglevel()是用来调试的。参数值为1表示开启调试模式,参数值为0关闭调试模式
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
    #send_mail("hequan2011","密码","hequan2011@sina.com","标题",'内容')
    send_mail("hequan2011", "密码", sys.argv[1], sys.argv[2], sys.argv[3])
```
