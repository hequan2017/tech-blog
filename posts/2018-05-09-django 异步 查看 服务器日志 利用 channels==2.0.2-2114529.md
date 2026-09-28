---
title: "django  异步 查看 服务器日志 | 利用 channels==2.0.2"
date: "2018-05-09 17:42:31"
category: "autoops"
source: "https://blog.51cto.com/hequan/2114529"
---
> **内容介绍**
>
> 本文是自动化运维平台开发实践,记录了「django  异步 查看 服务器日志 | 利用 channels==2.0.2」的相关内容。主要涉及:### django 异步 查看 服务器日志 实例 可以查看我编写的这个项目： https:///hequan2017/chain…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

### django  异步 查看 服务器日志

实例 可以查看我编写的这个项目：
https:///hequan2017/chain

### 模块

#### 需要安装以下模块

安装后会有一个版本号报错，不影响

```shellchannels==2.0.2
channels-redis==2.1.0
amqp==1.4.9
anyjson==0.3.3
asgi-redis==1.4.3
asgiref==2.3.0
async-timeout==2.0.0
attrs==17.4.0

cd /tmp/
wget https://files.pythonhosted.org/packages/12/2a/e9e4fb2e6b2f7a75577e0614926819a472934b0b85f205ba5d5d2add54d0/Twisted-18.4.0.tar.bz2
tar xf Twisted-18.4.0.tar.bz2
cd Twisted-18.4.0
python3 setup.py install
```

#### 启动redis

#### 原理

点击  查看日志页面，启动一个websocket连接，执行命令。

根据 **登录的用户名**，返回后端生成的消息，前端负责消费。

---

### 目录

```shellchain/
		chain/
			 settings.py
			 asgi.py
			 consumers.py
			 routing.py
    templates/
		   tasks/
			    tail.html
```

---

#### settings.py

```shellINSTALLED_APPS = [
    'channels',
]

# django-channels配置
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# 配置ASGI
ASGI_APPLICATION = "chain.routing.application"
```

#### consumers.py

```pythonfrom asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

class EchoConsumer(WebsocketConsumer):
    def connect(self):
        # 创建channels group， 命名为：用户名，并使用channel_layer写入到redis
        async_to_sync(self.channel_layer.group_add)(self.scope['user'].username, self.channel_name)

        # 返回给receive方法处理
        self.accept()

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.scope['user'].username,
            {
                "type": "user.message",
                "text": text_data,
            },
        )

    def user_message(self, event):
        # 消费
        self.send(text_data=event["text"])

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.scope['user'].username, self.channel_name)
```

#### asgi.py

```pythonimport os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chain.settings")
django.setup()
application = get_default_application()
```

#### routing.py

```pythonfrom channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter, ProtocolTypeRouter
from django.urls import path

from .consumers import EchoConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path(r"ws/", EchoConsumer),
            # path(r"stats/", StatsConsumer),
        ])
    )
})
```

---

### 网页设置：

#### 逻辑：

![](assets/2114529/01_483cf915ac1d4f9f20e0076044e188c5.png)

1. tail页面 向后面 post 主机信息，要查看的日志路径
2. 后端去利用 paramiko 执行命令，一直读取此接口，先返回一遍信息，如有新日志生成，再次返回给前端。
3. 点击停止，会修改一个环境变量， 上面paramiko监测到此环境变量为false后，就停止执行命令。

```html <a id="tail" class="btn btn-primary"  type="submit">查看</a>
<a id="tail_stop" class="btn btn-danger"  type="submit">不看了,必须点停止</a>

 <div class="ibox-content" >
         <pre id="output_append" ></pre>
 </div>

$(function () {

            $(document).on('click','#tail',function () {

                    $.ajax({
                        url: "{% url 'tasks:tail_perform' %}",
                        timeout : 5000, //超时时间设置，单位毫秒
                        type: 'POST',
                        data: $('.cmd_from').serialize(),
                        success: function (data) {
                            var obj = JSON.parse(data);
                                if (obj.status) {
                                    toastr.success("执行成功！")
                            } else {
                                 toastr.error(obj.error)
                            }

                        }
                    })
                });

              $(document).on('click','#tail_stop',function () {

                    $.ajax({
                        url: "{% url 'tasks:tail_perform_stop' %}",
                        timeout : 5000, //超时时间设置，单位毫秒
                        type: 'POST',
                        data: {"status":"stop"},
                        success: function (data) {
                            var obj = JSON.parse(data);
                                if (obj.status) {
                                    toastr.success("停止成功！")
                            } else {
                                 toastr.success("停止失败！")
                            }

                        }
                    })
                });
            });

 $(document).ready(function () {
    CreateWebSocket();
});

function CreateWebSocket() {
    var socket = new WebSocket('ws://' + window.location.host + '/ws/');
    socket.onmessage = function (message) {
        var result = JSON.parse(message.data);
        var status = result.status;
        var data = result.data;
        var output_html = '';
        if (status === 0) {
{#            $('#output_append').empty();#}
            output_html = data;
        }
        else if (status === 1) {
            $('#output_append').empty();
            output_html = data;
        }
        $("#output_append").prepend(output_html);
    }
}
```

#### urls.py

```shell    path('tail.html', views.TasksTail.as_view(), name='tail'),
    path('tailperform.html', views.taskstailperform, name='tail_perform'),
    path('tailperform-stop.html', views.taskstailstopperform, name='tail_perform_stop'),
```

#### views.py

```pythonfrom asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import paramiko

def taillog(request, hostname, port, username, password, private, tail):
    """
    执行 tail log 接口
    """
    channel_layer = get_channel_layer()
    user = request.user.username
    os.environ["".format(user)] = "true"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        ssh.connect(hostname=hostname, port=port, username=username, password=decrypt_p(password))
    else:
        pkey = paramiko.RSAKey.from_private_key_file(private)
        ssh.connect(hostname=hostname, port=port, username=username, pkey=pkey)
    cmd = "tail " + tail
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in iter(stdout.readline, ""):
        if os.environ.get("".format(user)) == 'false':
            break
        result = {"status": 0, 'data': line}
        result_all = json.dumps(result)
        async_to_sync(channel_layer.group_send)(user, {"type": "user.message", 'text': result_all})

def taskstailperform(request):
    """
    执行 tail_log  命令
    """
    if request.method == "POST":
        ret = {'status': True, 'error': None, }
        name = Names.objects.get(username=request.user)
        ids = request.POST.get('id')
        tail = request.POST.get('tail', None)

        if not ids or not tail:
            ret['status'] = False
            ret['error'] = "请选择服务器,输入参数及日志地址."
            return HttpResponse(json.dumps(ret))

        obj = AssetInfo.objects.get(id=ids)
  
     
        try:
            taillog(request, obj.network_ip, obj.port, obj.user.username, obj.user.password, obj.user.private_key, tail)
        except Exception as e:
            ret['status'] = False
            ret['error'] = "错误{0}".format(e)
            logger.error(e)
        return HttpResponse(json.dumps(ret))

def taskstailstopperform(request):
    """
    执行 tail_log  命令
    """
    if request.method == "POST":
        ret = {'status': True, 'error': None, }
        name = request.user.username
        os.environ["".format(name)] = "false"
        return HttpResponse(json.dumps(ret))
```

---
