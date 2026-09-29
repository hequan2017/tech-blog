---
title: "jQuery DataTables: Load Data via Ajax and Reload"
date: "2019-07-02 14:20:24"
category: "frontend"
source: "https://blog.51cto.com/hequan/2416184"
lang: "en"
---
> **About this post**
>
> This post records the Ajax dynamic loading and re-initialization of a jQuery
> DataTables table: it first presents a Bootstrap-style table skeleton and the
> JSON format returned by the backend (keys "1"~"5" map to the five columns),
> then uses $.getJSON to fetch the data, calling fnClearTable() / fnDestroy()
> first to clear and destroy the old table, and then re-initializes the
> DataTable with the returned data; it also includes the Chinese-localized
> oLanguage configuration and copy/csv/excel export buttons.

> **Technical notes**
>
> Two typos have been fixed: the oLanguage key "sInfoEmtpy" should be
> sInfoEmpty; the trailing comma at the end of the first line of the JSON
> example has been removed. fnClearTable/fnDestroy are legacy DataTables 1.9
> APIs; for 1.10+ it is recommended to use `table.ajax.reload()` or
> `table.clear().rows.add(data).draw()`. The `{#"order": [[0, 'desc']],#}` in
> the code is Django template comment syntax, used to comment out the default
> sorting configuration.

---

## 1. Table HTML

```html
<table class="table table-striped table-bordered table-hover " style="width: 100%;" id="table1">
    <thead>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Nullable</th>
        <th>Default</th>
        <th>Remarks</th>
    </tr>
    </thead>

    <tbody></tbody>
</table>
```

## 2. Returned Data Format

The JSON returned by the API, where the keys "1"~"5" correspond one-to-one with the `data` of the columns below:

```json
{
    "data": [
        {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5},
        {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
    ]
}
```

## 3. JS: Fetch Data via Ajax and Reload

Before reloading, first call fnClearTable() to clear the data and fnDestroy() to destroy the old instance, then re-initialize:

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
            "sLengthMenu": "Show _MENU_ records per page",
            "sZeroRecords": "Sorry, no matching data found",
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "No matching data found",
            "sInfoFiltered": " filtered from _MAX_ total records",
            "sProcessing": "Loading...",
            "sSearch": "Search",
            "oPaginate": {
                "sFirst": "First",
                "sPrevious": " Previous ",
                "sNext": " Next ",
                "sLast": " Last "
            }
        },
        dom: '<"html5buttons"B>lTfgitp',
        {#"order": [[0, 'desc']],#}
        "ordering": false, // disable sorting
        buttons: ['copy', 'csv', 'excel']
    });
});
```
