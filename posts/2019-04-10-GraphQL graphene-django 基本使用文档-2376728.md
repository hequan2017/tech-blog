---
title: "GraphQL  graphene-django  基本使用文档"
date: "2019-04-10 17:07:29"
category: "python"
source: "https://blog.51cto.com/hequan/2376728"
---
> **内容介绍**
>
> 本文是Python 编程实战笔记,记录了「GraphQL  graphene-django  基本使用文档」的相关内容。主要涉及:### graphene-django 基本使用文档 #### 介绍 > 一种用于 API 的查询语言…

---

### graphene-django  基本使用文档

#### 介绍

> 一种用于 API 的查询语言
> GraphQL 既是一种用于 API 的查询语言也是一个满足你数据查询的运行时。 GraphQL 对你的 API 中的数据提供了一套易于理解的完整描述，使得客户端能够准确地获得它需要的数据，而且没有任何冗余，也让 API 更容易地随着时间推移而演进，还能用于构建强大的开发者工具。

#### 文档

> 官网 http://graphql.cn/

> 参考文档 https:///graphql/index/drf

#### 个人项目应用

> https:///hequan2017/seal

#### 模块

```shellpip install  graphene-django
```

#### 使用

```pythonINSTALLED_APPS = [
	    'graphene_django',
]

GRAPHENE = {
    'SCHEMA': 'app.schema.schema'
}

urls.py
from graphene_django.views import GraphQLView
from app.schema import schema

    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
		
		
```

#### app/schema.py

```pythonfrom django.contrib.auth.models import  User  as Users
from graphene_django import DjangoObjectType
import graphene

# 相关文档 https:///graphql/index/drf
class UserType(DjangoObjectType):
    class Meta:
        model = Users

class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    # List == Field:
    # List 返回结果会是遍历所有查询结果
    # Field 返回结果只存在单个 (其中可添加参数, ex. pk)
    single_user = graphene.Field(UserType, pk=())

    # 定义函数名的格式: resolve_字段
    # **kwargs 传递参数
    # pk: 如果在字段中定义, 则方法参数中必含
    def resolve_users(self, info, **kwargs):
        return Users.objects.all()

    def resolve_single_user(self, info, pk):
        return Users.objects.get(id=pk)

class TQuery(Query, graphene.ObjectType):
    pass

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    info = graphene.Field(UserType)
    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        # print(info.context.user, '==当前用户==')
        # kwargs 是传递参数中的变量
        # user = info.context.user
        user_obj = Users(**kwargs)
        try:
            user_obj.save()
            ok = True
        except Exception as e:
            print(e)
            ok = False
        return CreateUser(ok=ok, info=user_obj)

class CMutation(object):
    create_user = CreateUser.Field()

class UpdateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        pk = (required=True)

    info = graphene.Field(UserType)
    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        pk = kwargs.get('pk')
        user_obj = Users.objects.get(id=pk)
        if not user_obj:
            return UpdateUser(ok=False)
        user_obj.__dict__.update(**kwargs)
        user_obj.save()
        ok = True
        return UpdateUser(ok=ok, info=user_obj)

class UMutation(object):
    update_user = UpdateUser.Field()

class DeleteUser(graphene.Mutation):
    class Arguments:
        pk = ()

    ok = graphene.Boolean()

    def mutate(self, info, **kwargs):
        pk = kwargs.get('pk')

        user = Users.objects.get(id=pk)
        user.delete()
        return DeleteUser(ok=True)

class DMutation(object):
    delete_user = DeleteUser.Field()

class Mutations(CMutation, UMutation,DMutation,graphene.ObjectType):
    pass

schema = graphene.Schema(query=TQuery, mutation=Mutations)
```

#### 请求

> 请求地址 :  http://localhost/graphql

> GraphQL 请求参数

```shellquery{
  users{
    id,
    username,
    email
  }
}

query{
  singleUser(pk: 1){
    username,
    email
  }
}

mutation createUser {
 createUser (username: "test1") {
     info {
         id,
     },
     ok
 }
}

mutation updateUser {
 updateUser (pk:2,username: "test2") {
     info {
         id,
     },
     ok
 }
}

mutation deleteUser {
 deleteUser (pk:2) {
     ok
 }
}
```
