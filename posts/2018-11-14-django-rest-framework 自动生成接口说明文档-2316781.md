---
title: "django-rest-framework     自动生成接口说明文档"
date: "2018-11-14 14:45:01"
category: "后端"
source: "https://blog.51cto.com/hequan/2316781"
---

### 自动生成接口说明文档

#### 安装

```
pip install djangorestframework 
```

#### urls.py

```
from rest_framework.documentation import include_docs_urls

    path('docs/', include_docs_urls(title='文档')),
	
```

#### models.py

```
from django.db import models

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
```

#### serializers.py

```
from rest_framework import serializers
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(help_text='主机')

    class Meta:
        model = Asset
        fields = '__all__'
```

#### views.py

```
import json
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
```

#### docs

```
http://127.0.0.1:8000/docs/
```

![](assets/2316781/01_3391fe36a610f5961dab6ac9359e1121.jpg)
