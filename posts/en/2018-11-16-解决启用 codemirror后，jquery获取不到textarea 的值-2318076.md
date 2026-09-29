---
title: "Fix: jQuery Can't Get the textarea Value After Enabling CodeMirror"
date: "2018-11-16 17:54:25"
category: "frontend"
source: "https://blog.51cto.com/hequan/2318076"
lang: "en"
---
> **About this post**
>
> This post solves a common frontend pitfall: after enabling the CodeMirror editor on a textarea, calling jQuery's `$("#config").val()` directly no longer returns the latest content in the editor. The right approach is to call the CodeMirror instance's getValue() method (or call save() first to sync the content back to the textarea and then read it). A short example is included.

> **Technical notes**
>
> This issue still exists in CodeMirror 5 today, and the fix is universally applicable. CodeMirror 6 has been rewritten with a modular API (EditorView.state.doc.toString()), so be aware that the code differs if you use the new version.

---

### Example

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
