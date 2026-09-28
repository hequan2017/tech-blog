---
title: "jquery  datatable ajax 获取数据/重新加载"
date: "2019-07-02 14:20:24"
category: "前端"
source: "https://blog.51cto.com/hequan/2416184"
---
> **内容介绍**
>
> 本文是前端开发学习与实践,记录了「jquery  datatable ajax 获取数据/重新加载」的相关内容。主要涉及:### table ### js…

---

### table

```html   <table class="table table-striped table-bordered table-hover "  style="width: 100%;"
                                               id="table1">
					<thead>
					<tr>
							<th>名</th>
							<th>类型</th>
							<th>是否为空</th>
							<th>默认值</th>
							<th>备注</th>
					</tr>
					</thead>

					<tbody>

					</tbody>

</table>

### js

{
"data":[
	{"1":1,
	"2":2,
	"3":3,
	"4":4,
	"5":5,
	},
		{"1":1,
	"2":2,
	"3":3,
	"4":4,
	"5":5,
	}
]
}
```javascript

```shell				 $.getJSON(url, function (data, textStatus) {

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
                            "sInfoEmtpy": "找不到相关数据",
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
                        dom: '<"html5buttons"B>lTfgitp,',
                        {#"order": [[0, 'desc']],#}
                        "ordering": false, // 禁止排序
                        buttons: ['copy', 'csv', 'excel']
                    });
                });
```
