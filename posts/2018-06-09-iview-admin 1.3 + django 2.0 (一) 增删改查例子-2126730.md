---
title: "iview-admin 1.3 + django 2.0 (一)  增删改查例子"
date: "2018-06-09 16:29:33"
category: "vue"
source: "https://blog.51cto.com/hequan/2126730"
---
> **内容介绍**
>
> 本文是 iview-admin 1.3（Vue2 + iView）+ Django 2.0 前后端分离系列第一篇，用资产
> 管理做最基础的增删改查例子：前端在克隆下来的 iview-admin 模板上修改 ESLint 与
> webpack 配置、引入 axios，新增资产路由与 asset / asset-add / asset-info /
> asset-edit 四个页面，通过 axios 调用 localhost:8000 的接口完成列表、新增、详情、
> 编辑与删除；后端用 DRF 的 ListCreateAPIView / RetrieveUpdateDestroyAPIView 两个
> 通用视图配合 ModelSerializer 暴露 /asset 接口，并用 django-cors-headers 处理跨域。

> **技术备注**
>
> Django 2.0 已于 2019 年 8 月停止支持；iView 2019 年 10 月起更名为 View UI（Vue3
> 版为 View UI Plus），本例基于 vue2 的 iview-admin 1.3 模板；
> axios 请求里的 {emulateJSON: true} 是 vue-resource 的参数，对 axios 无效，提交
> JSON 应由后端解析或改发 FormData；
> 原文若干内容被编辑器吃掉，已补全：git 克隆地址、asset.vue / asset-add.vue 的
> <template> 标签、按钮事件中丢失的 params.row.id，以及 models.py 的 Meta 缩进。

---

以下为利用 iview-admin + django 做的一个最基本的增删改查例子。

## 1. 前端 iview-admin

### 克隆与启动

```shell
git clone https://github.com/iview/iview-admin.git
cd iview-admin
npm install
npm run dev
```

修改 `.eslintrc.json`（第 17、21 行），放开 console 与 switch 穿透告警：

```json
"no-console": ["off"],
"no-fallthrough": 0,
```

`npm run dev` 报错时，修改 `build/webpack.dev.config.js`（第 11 行）与
`build/webpack.prod.config.js`（第 15 行）：

```javascript
const buf = Buffer.from('export default "development";');
```

### src/main.js

先安装依赖：`npm install axios`，再把 axios 挂到 Vue 原型上：

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
        { path: 'asset-info/:id', title: '资产详情', name: 'asset-info', component: () => import('@/views/asset/asset-info.vue') },
        { path: 'asset-edit/:id', title: '资产编辑', name: 'asset-edit', component: () => import('@/views/asset/asset-edit.vue') },
    ]
};

export const appRouter = [
    {
        path: '/asset',
        icon: 'key',
        name: 'asset',
        title: '资产管理',
        component: Main,
        children: [
            { path: 'asset', title: '资产管理', name: 'asset-index', component: () => import('@/views/asset/asset.vue') },
            { path: 'asset-add', title: '资产添加', name: 'asset-add', component: () => import('@/views/asset/asset-add.vue') },

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
                    资产管理
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
                        title: '详情',
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
                            }, '了解详情');
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
                                }, '编辑'),
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
                                                    this.$Message.success('提交成功');
                                                    this.remove(params.index);
                                                })
                                                .catch(error => {
                                                    this.e = JSON.stringify(error.response.data);
                                                });
                                        }
                                    }
                                }, '删除')
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
                this.$Message.success('删除了第' + (index + 1) + '行数据');
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
                            提交错误
                            <span slot="desc">{{ e }} </span>
                        </Alert>

                        <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="80">
                            <FormItem label="名字" prop="hostname">
                                <Input v-model="formValidate.hostname" placeholder="Enter your hostname"></Input>
                            </FormItem>
                            <FormItem label="账号" prop="username">
                                <Input v-model="formValidate.username" placeholder="Enter your username"></Input>
                            </FormItem>
                            <FormItem label="密码" prop="password">
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
                                this.$Message.success('提交成功');
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
                    资产详情
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
                            提交错误
                            <span slot="desc">{{ e }} </span>
                        </Alert>

                        <Form ref="formValidate" :model="formValidate" :rules="ruleValidate" :label-width="80">
                            <FormItem label="名字" prop="hostname">
                                <Input v-model="formValidate.hostname" placeholder="Enter your hostname"></Input>
                            </FormItem>
                            <FormItem label="账号" prop="username">
                                <Input v-model="formValidate.username" placeholder="Enter your username"></Input>
                            </FormItem>
                            <FormItem label="密码" prop="password">
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
                                this.$Message.success('提交成功');
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

## 2. 后端 Django

### 新建一个 asset 的 app

```shell
pip install djangorestframework  django-cors-headers
```

`settings.py`：

```python
INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
]
```

```python
# http://www.django-rest-framework.org/api-guide/permissions/#api-reference
# rest-framework    权限分类，现在是默认管理员可以访问
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
    'corsheaders.middleware.CorsMiddleware',  ## 添加此项目
    'django.middleware.common.CommonMiddleware',
    ...
]

## 允许跨域的地址
CORS_ORIGIN_WHITELIST = (
    "localhost:8080"
)
APPEND_SLASH=False
```

`asset/models.py`：

```python
class AssetLoginUser(models.Model):
    hostname = models.CharField(max_length=64, verbose_name='名称', unique=True)
    username = models.CharField(max_length=64, verbose_name="用户名", default='root', null=True, blank=True)
    password = models.CharField(max_length=256, blank=True, null=True, verbose_name='密码')
    ps = models.CharField(max_length=10240, verbose_name="备注", null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间', blank=True)
    utime = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间', blank=True)

    class Meta:
        db_table = "AssetLoginUser"
        verbose_name = "资产用户"
        verbose_name_plural = '资产用户'

    def __str__(self):
        return self.hostname
```

`urls.py`：

```python
path('asset', api.AssetList.as_view(), name='asset_api_list'),
path('asset/<int:pk>', api.AssetDetail.as_view(), name='asset_api_detail'),
```

`asset/serializers.py`：

```python
from rest_framework import serializers
from .models import AssetLoginUser

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLoginUser
        fields = '__all__'
```

`asset/api.py`：

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
