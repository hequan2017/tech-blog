---
title: "解决启用 codemirror后，jquery获取不到textarea 的值"
date: "2018-11-16 17:54:25"
category: "前端"
source: "https://blog.51cto.com/hequan/2318076"
---
> **内容介绍**
>
> 本文解决一个常见的前端小坑：对 textarea 启用 CodeMirror 编辑器后，直接用 jQuery 的 `$("#config").val()` 取不到编辑器里最新的内容。正确做法是调用 CodeMirror 实例的 getValue() 方法（或先 save() 同步回 textarea 再取值），文中给出了简短示例。

> **技术备注**
>
> 该问题至今在 CodeMirror 5 上仍然存在，解决方法通用；CodeMirror 6 已重写为模块化 API（EditorView.state.doc.toString()），如果使用新版请注意写法不同。

---

### 例子

```html
<textarea id="config" name="config"  class="form-control"></textarea>
```

```javascript
window.editor_two = CodeMirror.fromTextArea(document.getElementById("config"), {
                            lineNumbers: true,
                            matchBrackets: true,
                            styleActiveLine: true
                        });

 var d = {'config': editor_two.getValue() };
```

---
