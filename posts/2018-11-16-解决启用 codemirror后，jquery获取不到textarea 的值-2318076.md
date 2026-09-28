---
title: "解决启用 codemirror后，jquery获取不到textarea 的值"
date: "2018-11-16 17:54:25"
category: "前端"
source: "https://blog.51cto.com/hequan/2318076"
---
> **内容介绍**
>
> 本文是前端开发学习与实践,记录了「解决启用 codemirror后，jquery获取不到textarea 的值」的相关内容。

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

### 例子

```html <textarea id="config" name="config"  class="form-control"></textarea>
```javascript

```shell window.editor_two = CodeMirror.fromTextArea(document.getElementById("config"), {
                            lineNumbers: true,
                            matchBrackets: true,
                            styleActiveLine: true
                        });

 var d = {'config': editor_two.getValue() };
```

---
