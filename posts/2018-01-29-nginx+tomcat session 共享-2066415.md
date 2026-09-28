---
title: "nginx+tomcat   session 共享"
date: "2018-01-29 15:25:46"
category: "tomcat"
source: "https://blog.51cto.com/hequan/2066415"
---
> **内容介绍**
>
> 本文是Tomcat 中间件部署与调优,记录了「nginx+tomcat   session 共享」的相关内容。主要涉及:Tomcat 工作模式必须为Nio 模式。…

> **技术备注**
>
> Nginx 配置在不同大版本间略有差异,建议以当前稳定版(1.24+/1.26+)官方文档为准。

---

```shell
* tomcat1   192.168.10.153

* tomcat2   192.168.10.154
```

Tomcat  工作模式必须为Nio 模式。

```html
##添加如下内容，         注意更换   address="192.168.10.154"  为本机IP
vim /usr/local/tomcat/conf/server.xml

<Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster"
                 channelSendOptions="8">

          <Manager className="org.apache.catalina.ha.session.DeltaManager"
                   expireSessionsOnShutdown="false"
                   notifyListenersOnReplication="true"/>

          <Channel className="org.apache.catalina.tribes.group.GroupChannel">
            <Membership className="org.apache.catalina.tribes.membership.McastService"
                        address="228.0.0.4"
                        port="45564"
                        frequency="500"
                        dropTime="3000"/>
            <Receiver className="org.apache.catalina.tribes.transport.nio.NioReceiver"
                      address="192.168.10.154"
                      port="4000"
                      autoBind="100"
                      selectorTimeout="5000"
                      maxThreads="6"/>

            <Sender className="org.apache.catalina.tribes.transport.ReplicationTransmitter">
              <Transport className="org.apache.catalina.tribes.transport.nio.PooledParallelSender"/>
            </Sender>
            <Interceptor className="org.apache.catalina.tribes.group.interceptors.TcpFailureDetector"/>
            <Interceptor className="org.apache.catalina.tribes.group.interceptors.MessageDispatchInterceptor"/>
          </Channel>

          <Valve className="org.apache.catalina.ha.tcp.ReplicationValve"
                 filter=""/>
          <Valve className="org.apache.catalina.ha.session.JvmRouteBinderValve"/>

          <Deployer className="org.apache.catalina.ha.deploy.FarmWarDeployer"
                    tempDir="/tmp/war-temp/"
                    deployDir="/tmp/war-deploy/"
                    watchDir="/tmp/war-listen/"
                    watchEnabled="false"/>

          <ClusterListener className="org.apache.catalina.ha.session.ClusterSessionListener"/>
        </Cluster>
```

```html
##  修改 web文件，在</web-app>  上面  添加一行内容
vim /usr/local/tomcat/webapps/ROOT/WEB-INF/web.xml

<distributable/>
vim      index.jsp
<%@ page contentType="text/html; charset=GBK" %>
<%@ page import="java.util.*" %>
<html>
    <head>
        <title>Cluster App Test</title>
    </head>
    <body>
    Server Info: <%  out.println(request.getLocalAddr() + " : " + request.getLocalPort()+"
");%>
    <%
    out.println("
ID " + session.getId()+"
");   // 如果有新的 Session 属性设置
    String dataName = request.getParameter("dataName");
        if (dataName != null && dataName.length() > 0) {
            String dataValue = request.getParameter("dataValue");
            session.setAttribute(dataName, dataValue);
        }
     %>
     </body>
</html>
```nginx

```shell
##配置 nginx负责均衡，进行测试

        upstream tomcatserver {

        server 192.168.10.153:8080 weight=5;
        server  192.168.10.154:8080  weight=5;

        }

        location    / {

            proxy_pass http://tomcatserver;  #来自jsp请求交给tomcat处理
        }
```

![](assets/2066415/01_23f627c80559b900c1ba53508540897b.png)

![](assets/2066415/02_e58c876bd28e52ebe33ff5645e8f3129.png)
