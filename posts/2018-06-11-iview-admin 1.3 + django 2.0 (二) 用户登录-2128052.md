---
title: "iview-admin 1.3 + django 2.0 (二)  用户登录"
date: "2018-06-11 14:51:33"
category: "vue"
source: "https://blog.51cto.com/hequan/2128052"
---

### Iview-admin

#### main.js

```
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

#### logo.vue

```
<Alert v-show="isshow" type="error" show-icon closable>
    提交错误
    <span slot="desc">{{ e }} </span>
</Alert>

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
                                this.$store.commit('setAvator', 'https:///70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=3448484253,3685836170&fm=27&gp=0.jpg');
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

---

### Django

#### settings.py

```
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

#### urls.py

```
from rest_framework.authtoken import views

path('api-token-auth', views.obtain_auth_token),
```

#### api.py

```
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
