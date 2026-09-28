---
title: "django+echarts+ajax异步+显示优化--基本例子"
date: "2017-08-08 11:15:24"
category: "python"
source: "https://blog.51cto.com/hequan/1954409"
---
> **内容介绍**
>
> 本文给出 Django + ECharts + AJAX 异步刷新图表的基本例子:前端模板加载
> echarts.min.js,首次访问由后端视图 show 直接渲染最新数据(免去看图等刷新),
> 之后 setInterval 每 2 秒 AJAX 请求 /jigui/showapi 拉取 JSON,更新柱状图的
> xAxis/series 并 setOption 重绘;附带 window.onresize 自适应与 showLoading
> 加载动画等显示优化,后端给出 show 与 showapi 两个视图的对照实现。

> **技术备注**
>
> 两处笔误已修正:`eval（json)` 的全角括号——因 dataType:'json' 时 jQuery 已
> 自动解析为对象,直接 `server_info = json` 即可;视图里 `name.append()` 缺参
> (原发布时内容被吞),按模型字段补全为 `name.append(i.name)`。另:2 秒轮询的
> 做法在高并发场景建议改用 WebSocket(如 Django Channels);ECharts 3.x 的
> init/setOption 用法在 v5 中依然兼容。

---

## 1. 前端模板(ECharts + AJAX 轮询)

定义要显示的地方并加载 js:

```html
<script src="/static/js/echarts.min.js"></script>

<script>
    $(function () {
        var server_info;

        var myChart = echarts.init(document.getElementById('echarts-line'));
        var option = {
            title: {
                text: '机柜总数'
            },
            tooltip: {},
            legend: {
                data:['总数']
            },
            xAxis: {
                data: {{ name  | safe }}    ##第一次访问页面时，先从后端返回一个最新的数据，这样子就不会需要人们等着更新数据。
            },
            yAxis: {},
            series: [{
                name: '销量',
                type: 'bar',
                data: {{ jq | safe }} ##第一次访问页面时，先从后端返回一个最新的数据
            }]
        };
        myChart.setOption(option, true);

{#        myChart.showLoading();#}   ## echarts 的显示加载页面
        setInterval( function () {     ##AJAX去获取数据通过showapi

                $.ajax({
                    type: 'GET',
                    url: '/jigui/showapi',
                    dataType: 'json',
                    success: function (json) {
                        server_info = json;   ## dataType:'json' 时 jQuery 已解析为对象
                    }
                });

                    option.xAxis.data =  server_info.name;   ##赋值
                    option.series[0].data = server_info.jq;
{#                    myChart.hideLoading();#}   ## echarts 的隐藏加载页面
                    myChart.setOption(option, true);

                }, 2000);  ##每隔2秒 获取一次，重新生成值

         window.onresize = function () {
            myChart.resize();      ##根据页面大小重新定义图形大小
        };
    });

</script>
```

## 2. 后端视图(show 首次渲染 / showapi 接口)

```python
@login_required(login_url="/login.html")
def show(request):  ## 展示         第一次访问返回一个数据
    name_id = models.JiguiInfo.objects.filter(id__gt=0)
    name = []
    jq = []
    for i in name_id:
        name.append(i.name)
        jq.append(i.jq)

    ret = {'name': name, 'jq': jq}

    return render(request, 'jigui/show.html',{'name':name,'jq':jq})

@login_required(login_url="/login.html")
def showapi(request):  ## 展示    API返回数据
    name_id = models.JiguiInfo.objects.filter(id__gt=0)
    name = []
    jq = []
    for i in name_id:
        name.append(i.name)
        jq.append(i.jq)

    ret={'name':name,'jq':jq}
    return  HttpResponse(json.dumps(ret))
```
