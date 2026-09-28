---
title: "iview-admin 1.3 + django 2.0 (二)  用户登录"
date: "2018-06-11 14:51:33"
category: "vue"
source: "https://blog.51cto.com/hequan/2128052"
---
> **内容介绍**
>
> 本文是 iview-admin 1.3 + Django 2.0 前后端分离系列第二篇，实现用户登录鉴权：
> 前端在 main.js 给 axios 注册请求拦截器，自动在请求头带上 localStorage 中保存的
> Token；登录页 logo.vue 校验表单后提交到 DRF 的 /api-token-auth 接口换取 Token，
> 写入 Cookie 与 localStorage 并跳转首页。后端 settings 启用
> rest_framework.authtoken、默认权限改为 IsAuthenticated 并细化 CORS 配置，
> api.py 增加 CSRF 豁免中间件与分页，资产接口从此必须携带 Token 访问。

> **技术备注**
>
> Django 2.0 已于 2019 年 8 月停止支持；DRF 的 obtain_auth_token 认证方式至今仍
> 可用，更复杂的需求可换 djangorestframework-simplejwt；
> iView 已更名为 View UI，本例基于 vue2 版 iview-admin 1.3；
> 原文部分内容被编辑器吃掉：已补全 logo.vue 的 <template> 标签和 setAvator 头像
> 的 ss1.bdstatic.com 域名；登录表单的 Form 模板原文已佚失，现仅保留错误提示与脚本逻辑。

---

## 1. 前端 iview-admin

### main.js：axios 请求拦截器

```javascript
import axios from 'axios';

axios.interceptors.request.use(
    config => {
        let ttoken = JSON.parse(localStorage.getItem('token'));
        if (ttoken !== null) {
            config.headers['Authorization'] = 'Token ' + ttoken;
        }
        return config;
    }, function (error) {
        return Promise.reject(error);
    }
);

axios.defaults.withCredentials = true;
Vue.prototype.$ajax = axios;
```

### logo.vue：登录提交

```html
<template>
    <Alert v-show="isshow" type="error" show-icon closable>
        提交错误
        <span slot="desc">{{ e }} </span>
    </Alert>
</template>

<script>
import Cookies from 'js-cookie';
export default {
    data () {
        return {
            form: {
                username: 'admin',
                password: '1qaz.2wsx'
            },
            isshow: '',
            e: '',
            rules: {
                username: [
                    { required: true, message: '账号不能为空', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '密码不能为空', trigger: 'blur' }
                ]
            }
        };
    },
    methods: {
        handleSubmit: function () {
            this.$refs.loginForm.validate((valid) => {
                if (valid) {
                    this.$ajax.post('http://127.0.0.1:8000/api-token-auth', this.form, {emulateJSON: true})
                        .then((res) => {
                            console.log(res);
                            if (res.statusText !== 'OK') {
                                this.isshow = true;
                                this.e = JSON.stringify(res.data.data);
                            } else {
                                Cookies.set('user', this.form.username);
                                localStorage.setItem('token', JSON.stringify(res.data.token));
                                this.$store.commit('setAvator', 'https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=3448484253,3685836170&fm=27&gp=0.jpg');
                                if (this.form.username === 'iview_admin') {
                                    Cookies.set('access', 0);
                                } else {
                                    Cookies.set('access', 1);
                                }
                                this.$router.push({
                                    name: 'home_index'
                                });
                            }
                        });
                }
            });
        }
    }
};
</script>
```

## 2. 后端 Django

### settings.py

```python
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
]

# http://www.django-rest-framework.org/api-guide/permissions/#api-reference
# rest-framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',

    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    )
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    'localhost:8080',
)

APPEND_SLASH=False
```

### urls.py

```python
from rest_framework.authtoken import views

path('api-token-auth', views.obtain_auth_token),
```

### api.py

```python
from .serializers import AssetSerializer

from rest_framework import permissions
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from django.utils.deprecation import MiddlewareMixin

class StandardResultsSetPagination(PageNumberPagination):
        page_size = 2
        page_size_query_param = 'page'
        max_page_size = 1000

class DisableCSRFCheck(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

class AssetList(generics.ListCreateAPIView,DisableCSRFCheck):

    queryset = AssetLoginUser.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

class AssetDetail(generics.RetrieveUpdateDestroyAPIView,DisableCSRFCheck):
    queryset = AssetLoginUser.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
```

注意：api.py 里的 `AssetLoginUser` 来自上一篇的 asset 应用，别忘了
`from .models import AssetLoginUser`。
