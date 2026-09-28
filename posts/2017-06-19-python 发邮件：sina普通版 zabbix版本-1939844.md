---
title: "python 发邮件：sina普通版    |  zabbix版本"
date: "2017-06-19 15:59:49"
category: "python"
source: "https://blog.51cto.com/hequan/1939844"
---
> **内容介绍**
>
> 本文是Python 编程实战笔记,记录了「python 发邮件：sina普通版    |  zabbix版本」的相关内容。

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

```pytho
n
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

def send_mail(sender_sina='',pwd='',receiver='',mail_title='',mail_content=''):
    # 邮箱smtp服务器
    host_server = ''
    sender_sina_mail = sender_sina+'@sina.com'
    #ssl登录
    smtp = SMTP_SSL(host_server)
    #set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
    smtp.set_debuglevel(0)
    smtp.ehlo(host_server)
    smtp.login(sender_sina, pwd)
    msg = MIMEText(mail_content, "plain", 'utf-8')
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_sina_mail
    msg["To"] = receiver
    smtp.sendmail(sender_sina_mail, receiver, msg.as_string())
    smtp.quit()
send_mail("hequan2011","密码","hequan2011@sina.com","标题",'内容')
```

```pytho
n
#!/usr/bin/python
#coding:utf-8
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import sys

def send_mail(sender_sina='',pwd='',receiver='',mail_title='',mail_content=''):
    host_server = ''
    sender_sina_mail = sender_sina+'@sina.com'
    #ssl登录
    smtp = SMTP_SSL(host_server)
    #set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
    smtp.set_debuglevel(0)
    smtp.ehlo(host_server)
    smtp.login(sender_sina, pwd)
    try:
        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_sina_mail
        msg["To"] = receiver
        smtp.sendmail(sender_sina_mail, receiver, msg.as_string())
        smtp.quit()
        print("发送成功")
        return  True
    except  Exception as e :
        print("发送失败：",e)
        return False
        
if __name__=="__main__":
    #send_mail("hequan2011","密码","hequan2011@sina.com","标题",'内容')
    send_mail("hequan2011", "密码", sys.argv[1], sys.argv[2], sys.argv[3])
```
