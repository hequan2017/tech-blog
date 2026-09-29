---
title: "iview-admin 1.3 + django 2.0 (Part 2): User Login"
date: "2018-06-11 14:51:33"
category: "vue"
source: "https://blog.51cto.com/hequan/2128052"
lang: "en"
---
> **About this post**
>
> This is the second post in the iview-admin 1.3 + Django 2.0 front-end/back-end separation series, implementing user login authentication:
> On the front end, main.js registers a request interceptor for axios that automatically attaches the Token saved in
> localStorage to the request header; the login page logo.vue validates the form and posts it to the DRF /api-token-auth
> endpoint to exchange it for a Token, writes it into a Cookie and localStorage, and then redirects to the home page.
> On the back end, settings enables rest_framework.authtoken, changes the default permission to IsAuthenticated, and
> refines the CORS configuration; api.py adds a CSRF-exemption middleware and pagination, so the asset endpoints
> now require a Token.

> **Technical notes**
>
> Django 2.0 reached end of support in August 2019; DRF's obtain_auth_token authentication still works today, and for
> more complex needs you can switch to djangorestframework-simplejwt;
> iView has been renamed View UI; this example is based on the vue2-era iview-admin 1.3;
> Part of the original post was eaten by the editor: the <template> tag of logo.vue and the ss1.bdstatic.com domain of
> the setAvator avatar have been restored; the Form template of the login form was lost in the original, so only the
> error alert and the script logic remain.

---

## 1. Frontend: iview-admin

### main.js: axios request interceptor

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

### logo.vue: login submission

```html
<template>
    <Alert v-show="isshow" type="error" show-icon closable>
        Submission error
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
                    { required: true, message: 'Username cannot be empty', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: 'Password cannot be empty', trigger: 'blur' }
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

## 2. Backend: Django

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

Note: the `AssetLoginUser` in api.py comes from the asset app in the previous post; don't forget
`from .models import AssetLoginUser`.
