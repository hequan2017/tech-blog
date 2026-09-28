---
title: "django-rest-framework     自动生成接口说明文档"
date: "2018-11-14 14:45:01"
category: "后端"
source: "https://blog.51cto.com/hequan/2316781"
---
> **内容介绍**
>
> 本文是后端服务开发笔记,记录了「django-rest-framework     自动生成接口说明文档」的相关内容。主要涉及:### 自动生成接口说明文档 #### 安装 #### urls.py…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

### 自动生成接口说明文档

#### 安装

```shellpip
install djangorestframework
```

#### urls.py

```pythonfrom
rest_framework.documentation import include_docs_urls

    path('docs/', include_docs_urls(title='文档')),

```

#### models.py

```pythonfrom
django.db import models

# Create your models here.

class Asset(models.Model):

    hostname = models.CharField(max_length=64, verbose_name='主机名', unique=True)
    ip = models.CharField(max_length=30, verbose_name='ip', blank=True, null=True, )

    class Meta:
        db_table = "asset"
        verbose_name = "asset"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname
```pytho
n

#### serializers.py

```pythonfrom
rest_framework import serializers
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(help_text='主机')

    class Meta:
        model = Asset
        fields = '__all__'
```

#### views.py

```pythonimport
json
from django.shortcuts import HttpResponse
from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import AssetSerializer
from .models import Asset

class AssetInfo(generics.ListCreateAPIView):
    """
    资产
    """
    queryset = Asset.objects.get_queryset().order_by('id')
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAdminUser,)

#### docs

```

![](assets/2316781/01_3391fe36a610f5961dab6ac9359e1121.jpg)
