---
title: "jquery  datatable ajax 获取数据/重新加载"
date: "2019-07-02 14:20:24"
category: "frontend"
source: "https://blog.51cto.com/hequan/2416184"
---
> **内容介绍**
>
> 本文记录 jQuery DataTables 表格的 Ajax 动态加载与重新初始化:先给出
> Bootstrap 风格的 table 骨架和后端返回的 JSON 数据格式(键 "1"~"5"
> 对应五列),再用 $.getJSON 取数,先 fnClearTable() / fnDestroy() 清掉
> 并销毁旧表,然后以返回数据重新初始化 DataTable;同时附上中文化的
> oLanguage 配置与 copy/csv/excel 导出按钮。

> **技术备注**
>
> 两处笔误已修正:oLanguage 键名 "sInfoEmtpy" 应为 sInfoEmpty;JSON
> 示例第一行末尾多余的逗号已去掉。fnClearTable/fnDestroy 是 DataTables
> 1.9 旧版 API,1.10+ 推荐改用 `table.ajax.reload()` 或
> `table.clear().rows.add(data).draw()`。代码中 `{#"order": [[0, 'desc']],#}`
> 是 Django 模板的注释语法,作用是注释掉默认排序配置。

---

## 1. 表格 HTML

```html
<table class="table table-striped table-bordered table-hover " style="width: 100%;" id="table1">
    <thead>
    <tr>
        <th>名</th>
        <th>类型</th>
        <th>是否为空</th>
        <th>默认值</th>
        <th>备注</th>
    </tr>
    </thead>

    <tbody></tbody>
</table>
```

## 2. 返回数据格式

接口返回的 JSON,键 "1"~"5" 与下面 columns 的 data 一一对应:

```json
{
    "data": [
        {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5},
        {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    ]
}
```

## 3. JS:Ajax 获取数据并重新加载

重新加载前先 fnClearTable() 清数据、fnDestroy() 销毁旧实例,再重新初始化:

```javascript
$.getJSON(url, function (data, textStatus) {
    $("#table1").dataTable().fnClearTable();
    $("#table1").dataTable().fnDestroy();

    var data1 = data['data']

    $('#table1').DataTable({
        data: data1,
        columns: [
            {data: '1'},
            {data: '2'},
            {data: '3'},
            {data: '4'},
            {data: '5'}
        ],

        "oLanguage": {
            "sLengthMenu": "每页显示 _MENU_ 条记录",
            "sZeroRecords": "对不起，查询不到任何相关数据",
            "sInfo": "当前显示 _START_ 到 _END_ 条，共 _TOTAL_条记录",
            "sInfoEmpty": "找不到相关数据",
            "sInfoFiltered": " 数据表中共为 _MAX_ 条记录",
            "sProcessing": "正在加载中...",
            "sSearch": "搜索",
            "oPaginate": {
                "sFirst": "第一页",
                "sPrevious": " 上一页 ",
                "sNext": " 下一页 ",
                "sLast": " 最后一页 "
            }
        },
        dom: '<"html5buttons"B>lTfgitp',
        {#"order": [[0, 'desc']],#}
        "ordering": false, // 禁止排序
        buttons: ['copy', 'csv', 'excel']
    });
});
```
