---
title: "iview-admin 2.1  + django 2.1 （一） 登录认证+修改请求头 简单例子"
date: "2018-11-14 17:47:56"
category: "frontend"
source: "https://blog.51cto.com/hequan/2316979"
---
> **内容介绍**
>
> 本文是 iview-admin 2.1（前端）与 Django 2.1 + DRF（后端）前后端分离对接系列的第一篇，实现登录认证与请求头改造：前端在 libs/axios.js 中为除 login 外的请求统一附加 `Authorization: Token xxx` 头；后端用 djangorestframework 的 obtain_auth_token 签发 Token，配置 TokenAuthentication、分页、django-filter 与 django-cors-headers 解决跨域，并给出返回用户信息的 GetInfo 示例接口。

> **技术备注**
>
> iview-admin 2.1 基于 Vue 2 + iView（现名 View UI），该项目已停止维护，其精神续作为 vue-element-admin 与 vue-vben-admin 等 Vue 3 方案。文中 DRF Token 认证沿用至今，但 CORS_ORIGIN_ALLOW_ALL=True 存在安全风险，生产环境应使用 CORS_ALLOWED_ORIGINS 精确配置；另外文末用中间件关闭 CSRF 检查的做法仅适用于纯 Token 认证场景，启用 SessionAuthentication 时请勿照搬。

---

### 登录认证+修改请求头

#### 前端

登录相关文件说明：

- `config/index.js`：dev 环境配置后端地址
- `api/user.js`：登录请求参数

```js
const data = {
  username: userName.valueOf(),
  password
}
```

请求头设置（`libs/axios.js`）：

```js
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

```shell
pip install djangorestframework django-cors-headers
```

##### settings.py

```python
INSTALLED_APPS = [
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
]

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
        'rest_framework.renderers.BrowsableAPIRenderer'  # 注释掉 可以关闭 api web界面
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

```python
from rest_framework.authtoken import views

path('api-token-auth', views.obtain_auth_token),

path('get_info',GetInfo.as_view()),
```

##### views.py

```python
from rest_framework import permissions
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
