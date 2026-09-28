---
title: "解决启用 codemirror后，jquery获取不到textarea 的值"
date: "2018-11-16 17:54:25"
category: "前端"
source: "https://blog.51cto.com/hequan/2318076"
---

### 例子

```
 <textarea id="config" name="config"  class="form-control"></textarea>
```

```
 window.editor_two = CodeMirror.fromTextArea(document.getElementById("config"), {
                            lineNumbers: true,
                            matchBrackets: true,
                            styleActiveLine: true
                        });
												
 var d = {'config': editor_two.getValue() };
```

---
