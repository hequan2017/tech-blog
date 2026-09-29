---
title: "django-rest-framework     自动生成接口说明文档"
date: "2018-11-14 14:45:01"
category: "backend"
source: "https://blog.51cto.com/hequan/2316781"
---
> **内容介绍**
>
> 本文演示了如何用 Django REST framework 自带的 include_docs_urls 自动生成 API 接口说明文档：在 urls.py 挂载 docs/ 路由后，结合 serializers 字段的 help_text 与视图 docstring，DRF 会渲染出包含参数说明和可在线调试的文档页面。文中以一个简单的 Asset 资产模型为例给出了 models、serializers、views 的配套写法。

> **技术备注**
>
> DRF 自带的 include_docs_urls 依赖 coreapi，该方案自 DRF 3.10 起已标记废弃并在 DRF 3.16 中移除。目前官方推荐基于 OpenAPI 的 drf-spectacular（或较早的 drf-yasg）来生成 Swagger/Redoc 接口文档。

---

### 自动生成接口说明文档

#### 安装

```shell
pip install djangorestframework
```

#### urls.py

```python
from rest_framework.documentation import include_docs_urls

    path('docs/', include_docs_urls(title='文档')),

```

#### models.py

```python
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

```python
from rest_framework import serializers
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(help_text='主机')

    class Meta:
        model = Asset
        fields = '__all__'
```

#### views.py

```python
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

![drf 自动生成的 API 接口文档页面,含参数说明](assets/2316781/01_3391fe36a610f5961dab6ac9359e1121.jpg)
