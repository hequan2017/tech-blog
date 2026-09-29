---
title: "Clustering, Part 1: HAProxy+keepalived+varnish"
date: "2016-12-26 20:03:26"
category: "cluster"
source: "https://blog.51cto.com/hequan/1886307"
lang: "en"
---
> **About this post**
>
> First post in the cluster series: two HAProxy front ends use keepalived for VRRP
> master/backup (VIP 192.168.50.200, with automatic failover that triggers an email
> alert script). HAProxy serves a stats admin page on port 9091 and, on port 80,
> forwards requests to two Varnish nodes (9527) using URL-based consistent hashing;
> Varnish load-balances to four web/app backends via the directors module, with
> health probes, static/dynamic request separation, a PURGE ACL, compression, and
> cache TTLs configured in VCL. Finally, varnishadm is used to load the
> configuration and check backend health.

> **Technical notes**
>
> CentOS 7 reached end of life (EOL) on June 30, 2024; migrating to Rocky Linux 9 /
> AlmaLinux 9 or the Chinese openEuler is recommended.
>
> The alert email script changemail.py uses Python 2 syntax (`from email.MIMEText`,
> `reload(sys)`, `print 'OK'`); under Python 3 it must be changed to
> `from email.mime.text import MIMEText` and the setdefaultencoding call removed.
>
> The VCL uses Varnish 4.0 syntax (`import directors`, `vcl_backend_response`);
> newer Varnish versions (6/7.x) have adjusted syntax details, so consult the
> official upgrade notes when upgrading.

---

## 1. Deploy HAProxy (2 nodes)

Install:

```shell
yum install haproxy
```

Configure `/etc/haproxy/haproxy.cfg`:

```ini
global                                      # global settings
    log         127.0.0.1 local3            # where logs are written
    chroot      /var/lib/haproxy            # haproxy working directory
    pidfile     /var/run/haproxy.pid        # pid file location
    maxconn     4000                        # maximum connections
    user        haproxy                     # user identity at runtime
    group       haproxy                     # group identity at runtime
    daemon                                  # run as a daemon; without this it runs in the foreground
    stats socket /var/lib/haproxy/stats     # unix socket for local access to the stats

defaults                                    # default settings
    mode                    http            # run in http mode
    log                     global          # use the log settings from the global section
    option                  httplog
    option                  dontlognull
    option  http-server-close
    option  forwardfor      except 127.0.0.0/8    # add the "X-Forwarded-For" header to all requests sent to servers except localhost
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          1m
    timeout server          1m
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 3000            # maximum concurrent connections on the frontend

#---------------------------------------------------------------------
# main frontend which proxys to the backends
#---------------------------------------------------------------------
frontend  web *:80
    #acl url_static       path_beg       -i /static /images /javascript /stylesheets
    #acl url_static       path_end       -i .jpg .gif .png .css .js .html .txt .htm
    #acl url_dynamic      path_begin     -i .php .jsp
    #default_backend      static_srv if url_static
    #use_backend          dynamic_srv if url_dynamic
    use_backend        varnish_srv

#---------------------------------------------------------------------
# round robin balancing between the various backends
#---------------------------------------------------------------------
backend varnish_srv
    balance     uri              # URL-based consistent hashing algorithm
    hash-type   consistent
    server varnish1 192.168.50.56:9527 check
    server varnish2 192.168.50.57:9527 check

listen stats                     # enable the HAProxy web-based stats admin UI
    bind :9091
    stats enable
    stats uri   /simpletime?admin
    stats hide-version
    stats auth admin:hequan.123
    stats admin if TRUE
```

Start:

```shell
systemctl start haproxy
systemctl status haproxy
systemctl enable haproxy
netstat -lntup
```

## 2. Deploy keepalived on the HAProxy nodes

Install:

```shell
yum install -y keepalived
```

Configure `/etc/keepalived/keepalived.conf`:

```ini
! Configuration File for keepalived
global_defs {
 router_id proxy1
}
vrrp_script chk_haproxy {
   script "killall -0 haproxy"
   interval 1
   weight -20
}
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id  100
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        192.168.50.200/24
    }
    track_script {
        chk_down
        chk_haproxy
        }
   notify_master "/etc/keepalived/changemail.py master"
   notify_backup "/etc/keepalived/changemail.py backup"
   notify_fault  "/etc/keepalived/changemail.py fault"
}
```

Start:

```shell
systemctl start   keepalived.service
systemctl enable  keepalived.service
systemctl status  keepalived.service
```

Alert email setup in `/etc/keepalived/changemail.py`:

```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
import socket
import time
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.Header import Header
import sys
# Mail sending details; fill in according to your actual environment
smtpHost = 'XXXXXXXXXXXXXXXXXXX'
smtpPort = '25'
sslPort  = '110'
fromMail = 'XXXXXXXXXXXXXXXXX'
toMail   = 'XXXXXXXXXXXX'
username = 'XXXXXXXXXX'
password = 'XXXXXXX'
# Fix Chinese encoding issues
reload(sys)
sys.setdefaultencoding('utf8')
# Mail subject and body
subject = socket.gethostname() + " HA status has been changed"
body    = (time.strftime("%Y-%m-%d %H:%M:%S")) + " vrrp transition, " + socket.gethostname() + " changed to be " + sys.argv[1]
# Initialize the mail
encoding = 'utf-8'
mail = MIMEText(body.encode(encoding), 'plain', encoding)
mail['Subject'] = Header(subject, encoding)
mail['From'] = fromMail
mail['To'] = toMail
mail['Date'] = formatdate()
try:
    # Connect to the SMTP server; plain/SSL/TLS, pick one depending on what your SMTP supports
    # Plain mode: communication is not encrypted
    smtp = smtplib.SMTP(smtpHost, smtpPort)
    smtp.ehlo()
    smtp.login(username, password)
    # TLS mode: encrypted communication, secure mail data, uses the normal SMTP port
    #smtp = smtplib.SMTP(smtpHost, smtpPort)
    #smtp.ehlo()
    #smtp.starttls()
    #smtp.ehlo()
    #smtp.login(username, password)
    # Pure SSL mode: encrypted communication, secure mail data
    #smtp = smtplib.SMTP_SSL(smtpHost, sslPort)
    #smtp.ehlo()
    #smtp.login(username, password)
    # Send the mail
    smtp.sendmail(fromMail, toMail, mail.as_string())
    smtp.close()
    print 'OK'
except Exception:
    print 'Error: unable to send email'
```

```shell
chmod +x /etc/keepalived/changemail.py
```

## 3. Deploy varnish (2 nodes)

Install:

```shell
yum install varnish -y
```

Change the listening port in `/etc/varnish/varnish.params`:

```ini
VARNISH_LISTEN_PORT=9527    # change the default port
```

Edit `/etc/varnish/default.vcl`:

```vcl
vcl 4.0;
##############enable load balancing module###############
import directors;
################define PURGE ACL#######################
acl purgers {
    "127.0.0.1";
    "192.168.50.0"/24;
}
# Default backend definition.  Set this to point at your content server.
##############health probe configuration##############
probe HE {                      # static check
    .url = "/health.html";      # probe URL
    .timeout = 2s;              # probe timeout
    .window = 5;                # number of probes
    .threshold = 2;             # how many probes must succeed to be healthy
    .initial = 2;               # backend joins after 2 healthy probes at Varnish startup
    .interval = 2s;             # probe interval
    .expected_response = 200;   # expected response status code
}
probe HC {                      # dynamic check
    .url = "/health.php";
    .timeout = 2s;
    .window = 5;
    .threshold = 2;
    .initial = 2;
    .interval = 2s;
    .expected_response = 200;
}
#############add backend hosts################
backend web1 {
    .host = "192.168.50.58:80";
    .port = "80";
    .probe = HC;
}
backend web2 {
    .host = "192.168.50.59:80";
    .port = "80";
    .probe = HC;
}
backend app1 {
    .host = "192.168.50.60:80";
    .port = "80";
    .probe = HE;
}
backend app2 {
    .host = "192.168.50.61:80";
    .port = "80";
    .probe = HE;
}
#############define load balancers and algorithms###############
sub vcl_init {
    new webcluster = directors.round_robin();
    webcluster.add_backend(web1);
    webcluster.add_backend(web2);
    new appcluster = directors.round_robin();
    appcluster.add_backend(app1);
    appcluster.add_backend(app2);
}
################vcl_recv subroutine######################
sub vcl_recv {
#####not in ACL: PURGE not allowed, return 405#####
    if (req.method == "PURGE") {
        if (!client.ip ~ purgers) {
            return(synth(405, "Purging not allowed for" + client.ip));
        }
        return (purge);
    }
#####add a header so backends log the visitor's real IP
#    if (req.restarts == 0) {
#        set req.http.X-Forwarded-For = req.http.X-Forwarded-For + ", " + client.ip;
#    } else {
#        set req.http.X-Forwarded-For = client.ip;
#    }
#    set req.backend_hint = webcluster.backend();
#    set req.backend_hint = appcluster.backend();
#Note: since Varnish is not the first-level proxy, forwarding would only capture the upstream proxy IP, which is already included in the Forward header sent by HAProxy, so there is no need to configure it; as long as the backend log format records Forward information and the upstream proxy does not restrict it, the client's real IP can be obtained;
#####separate dynamic and static content#####
    if (req.url ~ "(?i)\.(php|asp|aspx|jsp|do|ashx|shtml)($|\?)") {
        set req.backend_hint = webcluster.backend();
    } else {
        set req.backend_hint = appcluster.backend();
    }
#####do not cache abnormal requests#####
    if (req.method != "GET" &&
        req.method != "HEAD" &&
        req.method != "PUT" &&
        req.method != "POST" &&
        req.method != "TRACE" &&
        req.method != "OPTIONS" &&
        req.method != "PATCH" &&
        req.method != "DELETE") {
        return (pipe);
    }
#####do not cache requests that are not GET or HEAD#####
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }
#####do not cache requests carrying Authorization or Cookie#####
    if (req.http.Authorization || req.http.Cookie) {
        return (pass);
    }
#####enable compression but exclude some media files#####
    if (req.http.Accept-Encoding) {
        if (req.url ~ "\.(bmp|png|gif|jpg|jpeg|ico|gz|tgz|bz2|tbz|zip|rar|mp3|mp4|ogg|swf|flv)$") {
            unset req.http.Accept-Encoding;
        } elseif (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elseif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {
            unset req.http.Accept-Encoding;
        }
    }
    return (hash);
}
####################vcl_pipe subroutine#################
sub vcl_pipe {
    return (pipe);
}
sub vcl_miss {
    return (fetch);
}
####################vcl_hash subroutine#################
sub vcl_hash {
    hash_data(req.url);
    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }
    if (req.http.Accept-Encoding ~ "gzip") {
        hash_data("gzip");
    } elseif (req.http.Accept-Encoding ~ "deflate") {
        hash_data("deflate");
    }
}
#############set cache TTL for resources##############
sub vcl_backend_response {
    if (beresp.http.cache-control !~ "s-maxage") {
        if (bereq.url ~ "(?i)\.(jpg|jpeg|png|gif|css|js|html|htm)$") {
            unset beresp.http.Set-Cookie;
            set beresp.ttl = 3600s;
        }
    }
}
################enable Purge#####################
sub vcl_purge {
    return(synth(200, "Purged"));
}
###############record cache hit status##############
sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT from " + req.http.host;
        set resp.http.X-Cache-Hits = obj.hits;
    } else {
        set resp.http.X-Cache = "MISS from " + req.http.host;
    }
    unset resp.http.X-Powered-By;
    unset resp.http.Server;
    unset resp.http.Via;
    unset resp.http.X-Varnish;
    unset resp.http.Age;
}
```

Start:

```shell
systemctl start varnish.service
systemctl enable varnish.service
systemctl status varnish.service
```

## 4. Loading the configuration and checking status

Use varnishadm to load the VCL and check backend health. Since the backend
application servers have not been set up yet, all backend health checks can be
seen in the Sick state:

```shell
varnishadm -S /etc/varnish/secret -T 127.0.0.1:6082
```

```text
200
varnish> vcl.load conf1 default.vcl
200
VCL compiled.
varnish> vcl.use conf1
200
VCL 'conf1' now active
varnish> backend.list
200
Backend name                   Refs   Admin      Probe
web1(192.168.50.58,,80)        2      probe      Sick 0/5
web2(192.168.50.59,,80)        2      probe      Sick 0/5
app1(192.168.50.60,,80)        2      probe      Sick 0/5
app2(192.168.50.61,,80)        2      probe      Sick 0/5
```
