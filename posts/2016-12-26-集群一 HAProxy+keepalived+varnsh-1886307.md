---
title: "集群一 HAProxy+keepalived+varnsh"
date: "2016-12-26 20:03:26"
category: "集群"
source: "https://blog.51cto.com/hequan/1886307"
---

```bash
一、部署HAProxy(2台)
1、安装
yum install HAProxy
2、配置
vim /etc/haproxy/haproxy.cfg
global    #全局配置
    log         127.0.0.1 local3      #日志纪录位置
    chroot      /var/lib/haproxy       #haproxy的工作目录
    pidfile     /var/run/haproxy.pid   #pid文件位置
    maxconn     4000                   #最大连接数
    user        haproxy                #运行时使用的用户身份
    group       haproxy                #运行时使用的组身份
    daemon                             #启动为守护进程，不加此处运行在前台
    stats socket /var/lib/haproxy/stats    #本地访问stats统计信息时以套接字方式通信
defaults                                          #默认配置
    mode                    http                  #已http模式运行
    log                     global                  #默认日志为全局配置中日志的设置
    option                  httplog
    option                  dontlognull
    option http-server-close
    option forwardfor       except 127.0.0.0/8    #除本机外所有发往服务器的请求首部中加入“X-Forwarded-For”首部
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          1m
    timeout server          1m
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 3000    #前端最大并发连接数
#---------------------------------------------------------------------
# main frontend which proxys to the backends
#---------------------------------------------------------------------
frontend  web *:80
    #acl url_static       path_beg       -i /static /p_w_picpaths /javascript /stylesheets
    #acl url_static       path_end       -i .jpg .gif .png .css .js .html .txt .htm
    #acl url_dynamic      path_begin     -i .php .jsp
    #default_backend      static_srv if url_static
    #use_backend          dynamic_srv if url_dynamic
    use_backend        varnish_srv
#---------------------------------------------------------------------
# round robin balancing between the various backends
#---------------------------------------------------------------------
backend varnish_srv
    balance     uri           #使用基于URL的一致性哈希调度算法
    hash-type   consistent
    server varnish1 192.168.50.56:9527 check
    server varnish2 192.168.50.57:9527 check
listen stats     #开启HAProxy图形化Web管理功能
    bind :9091
    stats enable
    stats uri   /simpletime?admin
    stats hide-version
    stats auth admin:hequan.123
    stats admin if TRUE
3、启动
systemctl start haproxy
systemctl status haproxy 
systemctl enable haproxy 
netstat -lntup 

二、在haproxy部署keepalived
1、安装
yum install -y keepalived
2、配置
vim /etc/keepalived/keepalived.conf
! Configuration File for keepalived   
global_defs {
 router_id proxy1
}
vrrp_script chk_haproxy {
   script "killall -0 haproxy"
   interval 1
   weight -20
}
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id  100
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        192.168.50.200/24
    }
    track_script {
        chk_down
        chk_haproxy
        }
   notify_master "/etc/keepalived/changemail.py master"
   notify_backup "/etc/keepalived/changemail.py backup"
   notify_fault "/etc/keepalived/changemail.py fault"
}
3、启动
systemctl start   keepalived.service
systemctl enable  keepalived.service
systemctl status  keepalived.service

报警邮件设置
vim  /etc/keepalived/changemail.py
#!/usr/bin/python 
# -*- coding: UTF-8 -*-     
import smtplib 
import socket
import time
from email.MIMEText import MIMEText 
from email.Utils import formatdate 
from email.Header import Header 
import sys
#发送邮件的相关信息，根据实际情况填写 
smtpHost = 'XXXXXXXXXXXXXXXXXXX'
smtpPort = '25'
sslPort  = '110'
fromMail = 'XXXXXXXXXXXXXXXXX'
toMail  = 'XXXXXXXXXXXX'
username = 'XXXXXXXXXX'
password = 'XXXXXXX'
#解决中文问题 
reload(sys) 
sys.setdefaultencoding('utf8') 
#邮件标题和内容 
subject  = socket.gethostname() + " HA status has changed"
body     = (time.strftime("%Y-%m-%d %H:%M:%S")) + " vrrp transition, " + socket.gethostname() + " changed to be " + sys.argv[1]
#初始化邮件 
encoding = 'utf-8' 
mail = MIMEText(body.encode(encoding),'plain',encoding) 
mail['Subject'] = Header(subject,encoding) 
mail['From'] = fromMail 
mail['To'] = toMail 
mail['Date'] = formatdate() 
try: 
    #连接smtp服务器，明文/SSL/TLS三种方式，根据你使用的SMTP支持情况选择一种 
    #普通方式，通信过程不加密 
    smtp = smtplib.SMTP(smtpHost,smtpPort)
    smtp.ehlo() 
    smtp.login(username,password) 
    #tls加密方式，通信过程加密，邮件数据安全，使用正常的smtp端口 
    #smtp = smtplib.SMTP(smtpHost,smtpPort) 
    #smtp.ehlo() 
    #smtp.starttls() 
    #smtp.ehlo() 
    #smtp.login(username,password) 
    #纯粹的ssl加密方式，通信过程加密，邮件数据安全 
    #smtp = smtplib.SMTP_SSL(smtpHost,sslPort) 
    #smtp.ehlo() 
    #smtp.login(username,password) 
    #发送邮件 
    smtp.sendmail(fromMail,toMail,mail.as_string()) 
    smtp.close() 
    print 'OK' 
except Exception: 
    print 'Error: unable to send email'
chmod +x /etc/keepalived/changemail.py
三、部署varnsh（2台）

1、安装
yum install varnish -y
2、配置
vim /etc/varnish/varnish.params
VARNISH_LISTEN_PORT=9527 #更改默认端口
vim /etc/varnish/default.vcl  #修改配置文件
vcl 4.0;
##############启用负载均衡模块###############
import directors;
################定义Purge-ACL控制#######################
acl purgers {
    "127.0.0.1";
    "192.168.50.0"/24;
}
# Default backend definition. Set this to point to your content server.
##############配置健康状态探测##############
probe HE {                      #静态检测
    .url = "/health.html";      #指定检测URL
    .timeout = 2s;              #探测超时时长
    .window = 5;                #探测次数
    .threshold = 2;             #探测次数成功多少次才算健康
    .initial = 2;               #Varnish启动探测后端主机2次健康后加入主机
    .interval = 2s;             #探测间隔时长
    .expected_response = 200;   #期望状态响应码
}
probe HC {                      #动态监测
    .url = "/health.php";       
    .timeout = 2s;             
    .window = 5;               
    .threshold = 2;             
    .initial = 2;               
    .interval = 2s;             
    .expected_response = 200;   
}
#############添加后端主机################
backend web1 {
    .host = "192.168.50.58:80";
    .port = "80";
    .probe = HC;
}
backend web2 {
    .host = "192.168.50.59:80";
    .port = "80";
    .probe = HC;
}
backend app1 {
    .host = "192.168.50.60:80";
    .port = "80";
    .probe = HE;
}
backend app2 {
    .host = "192.168.50.61:80";
    .port = "80";
    .probe = HE;
}
#############定义负载均衡及算法###############
sub vcl_init {
    new webcluster = directors.round_robin();
    webcluster.add_backend(web1);
    webcluster.add_backend(web2);
    new appcluster = directors.round_robin();
    appcluster.add_backend(app1);
    appcluster.add_backend(app2);
}
################定义vcl_recv函数段######################
sub vcl_recv {
#####ACL未授权，不允许PURGE，并返回405#####
    if (req.method == "PURGE") {
        if(!client.ip ~ purgers){
            return(synth(405,"Purging not allowed for" + client.ip));
        }
        return (purge);
    }
#####添加首部信息，使后端服务记录访问者的真实IP
#    if (req.restarts == 0) {
#        set req.http.X-Forwarded-For = req.http.X-Forwarded-For + ", " + client.ip;
#    } else {
#        set req.http.X-Forwarded-For = client.ip;
#    }
#    set req.backend_hint = webcluster.backend();
#   set req.backend_hint = appcluster.backend();
#注：因为Varnish不是一级代理，配置forward只能取到上级代理IP，而上级代理IP，本身就包含在HAProxy发送过来的Forward里，所以没必要配置，而后端服务器只要日志格式有启用记录Forward信息，并且上级代理没有做限制，那么，就能获取到客户端真实IP；
#####动静分离#####
  if (req.url ~ "(?i)\.(php|asp|aspx|jsp|do|ashx|shtml)($|\?)") {
        set req.backend_hint = webcluster.backend();
    }else{
        set req.backend_hint = appcluster.backend();
        }
#####不正常的请求不缓存#####
    if (req.method != "GET" &&
        req.method != "HEAD" &&
        req.method != "PUT" &&
        req.method != "POST" &&
        req.method != "TRACE" &&
        req.method != "OPTIONS" &&
        req.method != "PATCH" &&
        req.method != "DELETE") {
        return (pipe);
    }
#####如果请求不是GET或者HEAD，不缓存#####
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }
#####如果请求包含Authorization授权或Cookie认证，不缓存#####
    if (req.http.Authorization || req.http.Cookie) {
        return (pass);
    }
#####启用压缩，但排除一些流文件压缩#####
    if (req.http.Accept-Encoding) {
        if (req.url ~ "\.(bmp|png|gif|jpg|jpeg|ico|gz|tgz|bz2|tbz|zip|rar|mp3|mp4|ogg|swf|flv)$") {
            unset req.http.Accept-Encoding;
        } elseif (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elseif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {
            unset req.http.Accept-Encoding;
        }
    }
        return (hash);
}
####################定义vcl_pipe函数段#################
sub vcl_pipe {
    return (pipe);
}
sub vcl_miss {
    return (fetch);
}
####################定义vcl_hash函数段#################
sub vcl_hash {
    hash_data(req.url);
    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }
    if (req.http.Accept-Encoding ~ "gzip") {
        hash_data ("gzip");
    } elseif (req.http.Accept-Encoding ~ "deflate") {
        hash_data ("deflate");
    }
}
##############设置资源缓存时长#################
sub vcl_backend_response {
    if (beresp.http.cache-control !~ "s-maxage") {
       if (bereq.url ~ "(?i)\.(jpg|jpeg|png|gif|css|js|html|htm)$") {
          unset beresp.http.Set-Cookie;
          set beresp.ttl = 3600s;
       }
    }
}
################启用Purge#####################
sub vcl_purge {
    return(synth(200,"Purged"));
}
###############记录缓存命中状态##############
sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT from " + req.http.host;
        set resp.http.X-Cache-Hits = obj.hits;
    } else {
        set resp.http.X-Cache = "MISS from " + req.http.host;
    }
    unset resp.http.X-Powered-By;
    unset resp.http.Server;
    unset resp.http.Via;
    unset resp.http.X-Varnish;
    unset resp.http.Age;
}
3、启动
systemctl start varnish.service
systemctl enable varnish.service
systemctl status varnish.service
4、查看，加载配置，因为还没有配置后端应用服务器，可以看到后端主机健康检测全部处于Sick状态
#varnishadm -S /etc/varnish/secret -T 127.0.0.1:6082 
200  
varnish> vcl.load conf1 default.vcl
200       
VCL compiled.
varnish>  vcl.use conf1
200       
VCL 'conf1' now active
varnish>  backend.list
200       
Backend name                   Refs   Admin      Probe
web1(192.168.50.58,,80)        2      probe      Sick 0/5
web2(192.168.50.59,,80)        2      probe      Sick 0/5
app1(192.168.50.60,,80)        2      probe      Sick 0/5
app2(192.168.50.61,,80)        2      probe      Sick 0/5
```
