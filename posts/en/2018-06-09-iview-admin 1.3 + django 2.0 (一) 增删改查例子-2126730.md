---
title: "iview-admin 1.3 + django 2.0 (Part 1): A Basic CRUD Example"
date: "2018-06-09 16:29:33"
category: "vue"
source: "https://blog.51cto.com/hequan/2126730"
lang: "en"
---
> **About this post**
>
> This is the first post in a series on decoupled front-end/back-end development with
> iview-admin 1.3 (Vue2 + iView) + Django 2.0. It uses asset management to build the most
> basic CRUD example: on the front end, the cloned iview-admin template is modified (ESLint
> and webpack configuration, axios integration) and an asset route is added along with four
> pages — asset / asset-add / asset-info / asset-edit — which call the API on localhost:8000
> via axios to implement list, create, detail, edit, and delete; on the back end, two DRF
> generic views (ListCreateAPIView / RetrieveUpdateDestroyAPIView) together with a
> ModelSerializer expose the /asset endpoint, and django-cors-headers handles cross-origin
> requests.

> **Technical notes**
>
> Django 2.0 reached end of support in August 2019; iView was renamed View UI in October
> 2019 (the Vue3 version is View UI Plus). This example is based on the vue2-based
> iview-admin 1.3 template;
> {emulateJSON: true} in the axios request is a vue-resource parameter and has no effect on
> axios — to submit JSON, either parse it on the back end or send FormData instead;
> several parts of the original post were eaten by the editor and have been restored: the
> git clone URL, the <template> tags of asset.vue / asset-add.vue, the params.row.id lost
> in the button events, and the Meta indentation in models.py.

---

Below is the most basic CRUD example built with iview-admin + django.

## 1. Frontend: iview-admin

### Clone and start

```shell
git clone https://github.com/iview/iview-admin.git
cd iview-admin
npm install
npm run dev
```

Edit `.eslintrc.json` (lines 17 and 21) to turn off the console and switch fallthrough
warnings:

```json
"no-console": ["off"],
"no-fallthrough": 0,
```

If `npm run dev` reports an error, edit `build/webpack.dev.config.js` (line 11) and
`build/webpack.prod.config.js` (line 15):

```javascript
const buf = Buffer.from('export default "development";');
```

### src/main.js

First install the dependency with `npm install axios`, then attach axios to the Vue
prototype:

```javascript
import axios from 'axios';
Vue.prototype.axios = axios;
```

### src/router/router.js

```javascript
export const otherRouter = {
    path: '/',
    name: 'otherRouter',
    redirect: '/home',
    component: Main,
    children: [
        { path: 'asset-info/:id', title: 'Asset Detail', name: 'asset-info', component: () => import('@/views/asset/asset-info.vue') },
        { path: 'asset-edit/:id', title: 'Asset Edit', name: 'asset-edit', component: () => import('@/views/asset/asset-edit.vue') },
    ]
};

export const appRouter = [
    {
        path: '/asset',
        icon: 'key',
        name: 'asset',
        title: 'Asset Management',
        component: Main,
        children: [
            { path: 'asset', title: 'Asset Management', name: 'asset-index', component: () => import('@/views/asset/asset.vue') },
            { path: 'asset-add', title: 'Asset Add', name: 'asset-add', component: () => import('@/views/asset/asset-add.vue') },

        ]
    },
]
```

### src/views/asset/asset.vue

```html
<template>
    <div>
        <Row>
            <Card>
                <h4 slot="title">
                    <Icon type="android-archive"></Icon>
                    Asset Management
                </h4>
                <Row>
                    <Col span="24">
                        <Table border ref="selection"   :columns="columns1" :data="data1"  ></Table>
                        <Button @click="handleSelectAll(true)">Set all selected</Button>
                        <Button @click="handleSelectAll(false)">Cancel all selected</Button>
                    </Col>
                </Row>
            </Card>
        </Row>

    </div>
</template>

<script>
    export default {
        name: 'exportable-table',
        data () {
            return {
                columns1: [
                    {
                        type: 'selection',
                        title: 'id',
                        key: 'id'
                    },
                    {
                        title: 'id',
                        key: 'id'
                    },
                    {
                        title: 'hostname',
                        key: 'hostname'
                    },
                    {
                        title: 'username',
                        key: 'username'
                    },
                    {
                        title: 'password',
                        key: 'password'
                    },
                    {
                        title: 'Detail',
                        key: 'show_more',
                        align: 'center',
                        render: (h, params) => {
                            return h('Button', {
                                props: {
                                    type: 'text',
                                    size: 'small'
                                },
                                on: {
                                    click: () => {
                                        let argu = { id: params.row.id };
                                        this.$router.push({
                                            name: 'asset-info',
                                            params: argu
                                        });
                                    }
                                }
                            }, 'View details');
                        }
                    },
                    {
                        title: 'Action',
                        key: 'action',
                        width: 150,
                        align: 'center',
                        render: (h, params) => {
                            return h('div', [
                                h('Button', {
                                    props: {
                                        type: 'primary',
                                        size: 'small'
                                    },
                                    style: {
                                        marginRight: '5px'
                                    },
                                    on: {
                                        click: () => {
                                            let argu = { id: params.row.id };
                                            this.$router.push({
                                                name: 'asset-edit',
                                                params: argu
                                            });
                                        }
                                    }
                                }, 'Edit'),
                                h('Button', {
                                    props: {
                                        type: 'error',
                                        size: 'small'
                                    },
                                    style: {
                                        marginRight: '5px'
                                    },
                                    on: {
                                        click: () => {
                                            this.$ajax.delete('http://localhost:8000/asset/' + params.row.id)
                                                .then(response => {
                                                    this.$Message.success('Submitted successfully');
                                                    this.remove(params.index);
                                                })
                                                .catch(error => {
                                                    this.e = JSON.stringify(error.response.data);
                                                });
                                        }
                                    }
                                }, 'Delete')
                            ]);
                        }
                    }
                ],
                data1: []
            };
        },
        created () {
            this.aget();
        },
        methods: {
            handleSelectAll (status) {
                this.$refs.selection.selectAll(status);
            },
            aget: function () {
                this.$ajax.get('http://localhost:8000/asset')
                    .then(response => {
                        this.data1 = response.data;
                    })
                    .catch(error => {
                        console.log(error);
                    });
            },
            remove (index) {
                this.data1.splice(index, 1);
            },
            handleDel (val, index) {
                this.$Message.success('Deleted row ' + (index + 1) + ' of the data');
            }
        }

    };
</script>
```

### src/views/asset/asset-add.vue

```html
<template>
    <div>
        <Row>
            <Card>
                <Row>
                    <Col span="12">

                        <Alert v-show="isshow" type="error" show-icon closable>
                            Submission failed
                            <span slot="desc">{{ e }} </span>
                        </Alert>

                        <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="80">
                            <FormItem label="Name" prop="hostname">
                                <Input v-model="formValidate.hostname" placeholder="Enter your hostname"></Input>
                            </FormItem>
                            <FormItem label="Username" prop="username">
                                <Input v-model="formValidate.username" placeholder="Enter your username"></Input>
                            </FormItem>
                            <FormItem label="Password" prop="password">
                                <Input v-model="formValidate.password" placeholder="Enter your password"></Input>
                            </FormItem>

                            <FormItem>
                                <Button type="primary" @click="handleSubmit('formValidate')">Submit</Button>
                                <Button type="ghost" @click="handleReset('formValidate')" style="margin-left: 8px">
                                    Reset
                                </Button>
                            </FormItem>
                        </Form>

                    </Col>
                </Row>
            </Card>
        </Row>

    </div>
</template>

<script>
    export default {
        data () {
            return {
                formValidate: {
                    hostname: '',
                    username: '',
                    password: ''
                },
                ruleValidate: {
                    hostname: [
                        {required: true, message: 'The name cannot be empty', trigger: 'blur'}
                    ]
                },
                e: '',
                isshow: false
            };
        },
        methods: {
            handleSubmit (name) {
                this.$refs[name].validate((valid) => {
                    if (valid) {
                        this.$ajax.post('http://localhost:8000/asset', this.formValidate, {emulateJSON: true})
                            .then(response => {
                                this.$Message.success('Submitted successfully');
                                this.isshow = false;
                                // this.$Message.success(response.statusText);
                            })
                            .catch(error => {
                                // this.$Message.error(JSON.stringify(error.response.data));
                                this.isshow = true;
                                this.e = JSON.stringify(error.response.data);
                            });
                    } else {
                        this.$Message.error('Fail!');
                    }
                });
            },
            handleReset (name) {
                this.$refs[name].resetFields();
            }
        }
    };
</script>
```

### src/views/asset/asset-info.vue

```html
<style lang="less" scoped>
    @import '../../styles/common.less';
    @import './components/table.less';
</style>

<template>

    <div>
        <Row>
            <Card>
                <h4 slot="title">
                    <Icon type="android-archive"></Icon>
                    Asset Detail
                </h4>
                <Row>
                    <Col span="24">
                        <div  v-bind:content='item' v-for="(item,key)  of data1" >
                           {{ key }} {{ item }}
                        </div>
                    </Col>
                </Row>
            </Card>
        </Row>

    </div>
</template>

<script>
    export default {
        name: 'exportable-table',
        data () {
            return {
                columns1: [
                    {
                        type: 'selection',
                        title: 'id',
                        key: 'id'
                    },
                    {
                        title: 'id',
                        key: 'id'
                    },
                    {
                        title: 'hostname',
                        key: 'hostname'
                    },
                    {
                        title: 'username',
                        key: 'username'
                    },
                    {
                        title: 'password',
                        key: 'password'
                    },
                    {
                        title: 'ps',
                        key: 'ps'
                    }
                ],
                data1: '',
                ids: ''
            };
        },
        created () {
            this.aget();
        },
        methods: {
            handleSelectAll (status) {
                this.$refs.selection.selectAll(status);
            },
            aget: function () {
                let ids = this.$route.params.id;
                this.$ajax.get('http://localhost:8000/asset/' + ids)
                    .then(response => {
                        this.data1 = response.data;
                    })
                    .catch(error => {
                        console.log(error);
                    });
            }
        }

    };
</script>
```

### src/views/asset/asset-edit.vue

```html
<template>
    <div>
        <Row>
            <Card>
                <Row>
                    <Col span="12">

                        <Alert v-show="isshow" type="error" show-icon closable>
                            Submission failed
                            <span slot="desc">{{ e }} </span>
                        </Alert>

                        <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="80">
                            <FormItem label="Name" prop="hostname">
                                <Input v-model="formValidate.hostname" placeholder="Enter your hostname"></Input>
                            </FormItem>
                            <FormItem label="Username" prop="username">
                                <Input v-model="formValidate.username" placeholder="Enter your username"></Input>
                            </FormItem>
                            <FormItem label="Password" prop="password">
                                <Input v-model="formValidate.password" placeholder="Enter your password"></Input>
                            </FormItem>

                            <FormItem>
                                <Button type="primary" @click="handleSubmit('formValidate')">Submit</Button>
                                <Button type="ghost" @click="handleReset('formValidate')" style="margin-left: 8px">
                                    Reset
                                </Button>
                            </FormItem>
                        </Form>

                    </Col>
                </Row>
            </Card>
        </Row>

    </div>
</template>

<script>
    export default {
        data () {
            return {
                formValidate: {
                    hostname: '',
                    username: '',
                    password: ''
                },
                ruleValidate: {
                    hostname: [
                        {required: true, message: 'The name cannot be empty', trigger: 'blur'}
                    ]
                },
                e: '',
                isshow: false,
                ids: ''
            };
        },
        methods: {
            aget: function () {
                let ids = this.$route.params.id;
                this.$ajax.get('http://localhost:8000/asset/' + ids)
                    .then(response => {
                        this.formValidate.hostname = response.data.hostname;
                        this.formValidate.username = response.data.username;
                        this.formValidate.password = response.data.password;
                    })
                    .catch(error => {
                        console.log(error);
                    });
            },
            handleSubmit (name) {
                this.$refs[name].validate((valid) => {
                    let ids = this.$route.params.id;
                    if (valid) {
                        this.$ajax.put('http://localhost:8000/asset/' + ids, this.formValidate)
                            .then(response => {
                                this.$Message.success('Submitted successfully');
                                this.isshow = false;
                                // this.$Message.success(response.statusText);
                            })
                            .catch(error => {
                                // this.$Message.error(JSON.stringify(error.response.data));
                                this.isshow = true;
                                this.e = JSON.stringify(error.response.data);
                            });
                    } else {
                        this.$Message.error('Fail!');
                    }
                });
            },
            handleReset (name) {
                this.$refs[name].resetFields();
            }
        },
        created () {
            this.aget();
        }
    };
</script>
```

## 2. Backend: Django

### Create an asset app

```shell
pip install djangorestframework  django-cors-headers
```

`settings.py`:

```python
INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
]
```

```python
# http://www.django-rest-framework.org/api-guide/permissions/#api-reference
# rest-framework    permission classes; for now the default lets the admin access it
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.IsAdminUser',
    ),
}
```

```python
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',  ## add this entry
    'django.middleware.common.CommonMiddleware',
    ...
]

## Addresses allowed for cross-origin access
CORS_ORIGIN_WHITELIST = (
    "localhost:8080"
)
APPEND_SLASH=False
```

`asset/models.py`:

```python
class AssetLoginUser(models.Model):
    hostname = models.CharField(max_length=64, verbose_name='name', unique=True)
    username = models.CharField(max_length=64, verbose_name="username", default='root', null=True, blank=True)
    password = models.CharField(max_length=256, blank=True, null=True, verbose_name='password')
    ps = models.CharField(max_length=10240, verbose_name="note", null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation time', blank=True)
    utime = models.DateTimeField(auto_now=True, null=True, verbose_name='update time', blank=True)

    class Meta:
        db_table = "AssetLoginUser"
        verbose_name = "asset user"
        verbose_name_plural = 'asset user'

    def __str__(self):
        return self.hostname
```

`urls.py`:

```python
path('asset', api.AssetList.as_view(), name='asset_api_list'),
path('asset/<int:pk>', api.AssetDetail.as_view(), name='asset_api_detail'),
```

`asset/serializers.py`:

```python
from rest_framework import serializers
from .models import AssetLoginUser

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLoginUser
        fields = '__all__'
```

`asset/api.py`:

```python
from rest_framework import generics
from .models import AssetLoginUser
from .serializers import AssetSerializer
from rest_framework import permissions

class AssetList(generics.ListCreateAPIView):
    queryset = AssetLoginUser.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.AllowAny,)

class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetLoginUser.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.AllowAny,)
```
