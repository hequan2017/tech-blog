---
title: "django+echarts+ajax异步+显示优化--基本例子"
date: "2017-08-08 11:15:24"
category: "python"
source: "https://blog.51cto.com/hequan/1954409"
---
> **内容介绍**
>
> 本文是Python 编程实战笔记,记录了「django+echarts+ajax异步+显示优化--基本例子」的相关内容。

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

```htm
l
##定义要显示的地方

<script src="/static/js/echarts.min.js"></script> 
#加载js

<script>
    $(function () {
        var server_info;

        var myChart = echarts.init(document.getElementById('echarts-line'));
        var option = {
            title: {
                text: '机柜总数'
            },
            tooltip: {},
            legend: {
                data:['总数']
            },
            xAxis: {
                data: {{ name  | safe }}    ##第一次访问页面时，先从后端返回一个最新的数据，这样子就不会需要人们等着更新数据。
            },
            yAxis: {},
            series: [{
                name: '销量',
                type: 'bar',
                data: {{ jq | safe }} ##第一次访问页面时，先从后端返回一个最新的数据
            }]
        };
        myChart.setOption(option, true);

{#        myChart.showLoading();#}   ## echarts 的显示加载页面
        setInterval( function () {     ##AJAX去获取数据通过showapi

                $.ajax({
                    type: 'GET',
                    url: '/jigui/showapi',
                    dataType: 'json',
                    success: function (json) {
                        server_info = eval（json);
                    }
                });

                    option.xAxis.data =  server_info.name;   ##赋值
                    option.series[0].data = server_info.jq;
{#                    myChart.hideLoading();#}   ## echarts 的隐藏加载页面
                    myChart.setOption(option, true);

                }, 2000);  ##每隔2秒 获取一次，重新生成值

         window.onresize = function () {
            myChart.resize();      ##根据页面大小重新定义图形大小
        };
    });

</script>
```

```pytho
n
@login_required(login_url="/login.html")
def show(request):  ## 展示         第一次访问返回一个数据         
    name_id = models.JiguiInfo.objects.filter(id__gt=0)
    name = []
    jq = []
    for i in name_id:
        name.append()
        jq.append(i.jq)
    
    ret = {'name': name, 'jq': jq}
    
    return render(request, 'jigui/show.html',{'name':name,'jq':jq})

@login_required(login_url="/login.html")
def showapi(request):  ## 展示    API返回数据
    name_id = models.JiguiInfo.objects.filter(id__gt=0)
    name = []
    jq = []
    for i in name_id:
        name.append()
        jq.append(i.jq)
    
    ret={'name':name,'jq':jq}
    return  HttpResponse(json.dumps(ret))
```
