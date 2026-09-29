---
title: "Django + ECharts + AJAX async + display optimization -- a basic example"
date: "2017-08-08 11:15:24"
category: "python"
source: "https://blog.51cto.com/hequan/1954409"
lang: "en"
---
> **About this post**
>
> This post presents a basic example of asynchronous chart refreshing with Django + ECharts + AJAX: the front-end
> template loads echarts.min.js; on the first visit the back-end view `show` renders the latest data directly (no need
> to wait for a refresh to see the chart); afterwards a `setInterval` fires an AJAX request to `/jigui/showapi` every
> 2 seconds to fetch JSON, updates the bar chart's xAxis/series and calls setOption to redraw. Display optimizations
> such as window.onresize adaptation and the showLoading loading animation are included as well, and the back end shows
> a side-by-side implementation of the two views `show` and `showapi`.

> **Technical notes**
>
> Two typos have been fixed: the full-width parenthesis in `eval（json)` — with dataType:'json', jQuery already parses
> the response into an object, so `server_info = json` is enough; and the missing argument in `name.append()` in the
> view (the content was swallowed when the post was originally published), completed as `name.append(i.name)`
> according to the model field. In addition: for the 2-second polling approach, WebSocket (e.g., Django Channels) is
> recommended under high concurrency; the ECharts 3.x init/setOption usage remains compatible in v5.

---

## 1. Front-end template (ECharts + AJAX polling)

Define where the chart is displayed and load the JS:

```html
<script src="/static/js/echarts.min.js"></script>

<script>
    $(function () {
        var server_info;

        var myChart = echarts.init(document.getElementById('echarts-line'));
        var option = {
            title: {
                text: 'Total cabinets'
            },
            tooltip: {},
            legend: {
                data:['Total']
            },
            xAxis: {
                data: {{ name  | safe }}    ## On the first visit, the backend returns the latest data right away, so users don't have to wait for a refresh.
            },
            yAxis: {},
            series: [{
                name: 'Sales',
                type: 'bar',
                data: {{ jq | safe }} ## On the first visit, the backend returns the latest data first
            }]
        };
        myChart.setOption(option, true);

{#        myChart.showLoading();#}   ## ECharts loading animation for the page
        setInterval( function () {     ## Fetch data via AJAX through showapi

                $.ajax({
                    type: 'GET',
                    url: '/jigui/showapi',
                    dataType: 'json',
                    success: function (json) {
                        server_info = json;   ## With dataType:'json', jQuery has already parsed it into an object
                    }
                });

                    option.xAxis.data =  server_info.name;   ## Assign the values
                    option.series[0].data = server_info.jq;
{#                    myChart.hideLoading();#}   ## Hide the ECharts loading animation for the page
                    myChart.setOption(option, true);

                }, 2000);  ## Fetch once every 2 seconds and regenerate the values

         window.onresize = function () {
            myChart.resize();      ## Resize the chart according to the page size
        };
    });

</script>
```

## 2. Back-end views (show for the first render / showapi endpoint)

```python
@login_required(login_url="/login.html")
def show(request):  ## Display         Returns one set of data on the first visit
    name_id = models.JiguiInfo.objects.filter(id__gt=0)
    name = []
    jq = []
    for i in name_id:
        name.append(i.name)
        jq.append(i.jq)

    ret = {'name': name, 'jq': jq}

    return render(request, 'jigui/show.html',{'name':name,'jq':jq})

@login_required(login_url="/login.html")
def showapi(request):  ## Display    API returning data
    name_id = models.JiguiInfo.objects.filter(id__gt=0)
    name = []
    jq = []
    for i in name_id:
        name.append(i.name)
        jq.append(i.jq)

    ret={'name':name,'jq':jq}
    return  HttpResponse(json.dumps(ret))
```
