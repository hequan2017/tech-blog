---
title: "GraphQL graphene-django: A Basic Usage Guide"
date: "2019-04-10 17:07:29"
category: "python"
source: "https://blog.51cto.com/hequan/2376728"
lang: "en"
---
> **About this post**
>
> A basic usage guide to graphene-django: integrating GraphQL into a Django project, defining a DjangoObjectType to map the User model, implementing the two query styles (List/Field) and the three mutations (create/update/delete), plus the settings and urls configuration and complete GraphQL request examples.
>
> **Technical notes**
>
> This post is based on graphene 2.x. Starting with graphene 3, `mutate(self, info, **kwargs)` must be changed to `mutate(root, info, **kwargs)`, and DjangoObjectType must declare `fields` explicitly (or use `fields = "__all__"`). Keep this in mind when upgrading. For graphene-django compatibility with Django 4.x+, refer to the version matrix in its official documentation.

---

### graphene-django: A Basic Usage Guide

#### Introduction

> A query language for your API
> GraphQL is a query language for APIs and also a runtime for fulfilling your data queries. GraphQL provides a complete and understandable description of the data in your API, gives clients the power to ask for exactly what they need and nothing more, makes it easier to evolve APIs over time, and enables building powerful developer tools.

#### Documentation

- Official site: http://graphql.cn/
- Reference documentation: https://docs.graphene-python.org/projects/django/en/latest/ (the original link is dead; this is the address of the new documentation)

#### Personal Project

https://github.com/hequan2017/seal

#### Module

```shell
pip install graphene-django
```

#### Usage

```python
INSTALLED_APPS = [
    'graphene_django',
]

GRAPHENE = {
    'SCHEMA': 'app.schema.schema'
}

# urls.py
from graphene_django.views import GraphQLView
from app.schema import schema

urlpatterns = [
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]
```

#### app/schema.py

```python
from django.contrib.auth.models import  User  as Users
from graphene_django import DjangoObjectType
import graphene

# Related docs: https://docs.graphene-python.org/projects/django/en/latest/
class UserType(DjangoObjectType):
    class Meta:
        model = Users

class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    # List == Field:
    # List: the result iterates over all query results
    # Field: the result is a single object (extra arguments can be added, e.g. pk)
    single_user = graphene.Field(UserType, pk=graphene.Int())

    # Resolver naming convention: resolve_<field>
    # **kwargs passes the arguments
    # pk: if defined on the field, it must appear in the method parameters
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
        # print(info.context.user, '==current user==')
        # kwargs holds the variables passed in
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
        pk = graphene.Int(required=True)

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
        pk = graphene.Int(required=True)

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

#### Requests

> Request URL: http://localhost/graphql

> GraphQL request parameters

```graphql
query {
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
