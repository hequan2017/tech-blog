---
title: "iview-admin 2.1 + django 2.1 (Part 1): A Simple Example of Login Authentication + Modifying Request Headers"
date: "2018-11-14 17:47:56"
category: "frontend"
source: "https://blog.51cto.com/hequan/2316979"
lang: "en"
---
> **About this post**
>
> This is the first post in a series on integrating iview-admin 2.1 (frontend) with Django 2.1 + DRF (backend) in a decoupled front-end/back-end setup, implementing login authentication and request header modification: the frontend attaches an `Authorization: Token xxx` header to every request except login in libs/axios.js; the backend uses djangorestframework's obtain_auth_token to issue tokens, configures TokenAuthentication, pagination, django-filter, and django-cors-headers to handle cross-origin requests, and provides a sample GetInfo endpoint that returns user information.

> **Technical notes**
>
> iview-admin 2.1 is based on Vue 2 + iView (now named View UI); that project is no longer maintained, and its spiritual successors include Vue 3 solutions such as vue-element-admin and vue-vben-admin. The DRF token authentication described here is still in use today, but CORS_ORIGIN_ALLOW_ALL=True poses a security risk; in production, use CORS_ALLOWED_ORIGINS with an explicit allowlist instead. Also, the approach of disabling CSRF checks via middleware at the end of this post applies only to pure token authentication scenarios — do not copy it when SessionAuthentication is enabled.

---

### Login Authentication + Modifying Request Headers

#### Frontend

Description of the login-related files:

- `config/index.js`: configures the backend address for the dev environment
- `api/user.js`: login request parameters

```js
const data = {
  username: userName.valueOf(),
  password
}
```

Request header settings (`libs/axios.js`):

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

options = Object.assign(this.getInsideConfig(options.url), options)   // add options.url
```

#### Backend

##### Installing DRF

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
        'rest_framework.renderers.BrowsableAPIRenderer'  # comment this out to disable the API web UI
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
