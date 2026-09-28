---
title: "iview-admin 2.1  + django 2.1 （一） 登录认证+修改请求头 简单例子"
date: "2018-11-14 17:47:56"
category: "前端"
source: "https://blog.51cto.com/hequan/2316979"
---
> **内容介绍**
>
> 本文是前端开发学习与实践,记录了「iview-admin 2.1  + django 2.1 （一） 登录认证+修改请求头 简单例子」的相关内容。主要涉及:### 登录认证+修改请求头 #### 前端 #### 后端…

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

### 登录认证+修改请求头

#### 前端

```shell登录

config/index.js

dev: 后端地址

api/user.js

const data = {
  username: userName.valueOf(),
  password
}

请求头设置

libs/axios.js

libs/axios.js

getInsideConfig (url) {
  const config = {
    baseURL: this.baseUrl,
    headers: {
      //
    }
  }
  if (url !== 'login') {
    config.headers['Authorization'] = 'Token ' + store.state.user.token
  }
  return config
}

options = Object.assign(this.getInsideConfig(options.url), options)   // 添加 options.url
```

#### 后端

##### 安装drf

```shellpip install djangorestframework  django-cors-headers

##### settings.py

'rest_framework.authtoken',
'corsheaders',
'django_filters'

# REST_FRAMEWORK
# http://drf.jiuyou.info/#/drf/requests

MIDDLEWARE = [
'corsheaders.middleware.CorsMiddleware',
'django.middleware.common.CommonMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',

    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer' #注释掉 可以关闭  api web界面
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*',
)

class DisableCSRFCheck(object):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

MIDDLEWARE_CLASSES = 'DisableCSRFCheck'
```

##### urls.py

```pythonfrom rest_framework.authtoken import views

path('api-token-auth', views.obtain_auth_token),

path('get_info',GetInfo.as_view()),
```

##### views.py

```pythonfrom rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

class GetInfo(APIView):

    def get(self, request):
        admin = {
            'name': 'super_admin',
            'user_id': '1',
            'access': ['super_admin', 'admin'],
            'token': 'super_admin',
            'avator': 'https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png'
        }
        return Response(admin)
```
