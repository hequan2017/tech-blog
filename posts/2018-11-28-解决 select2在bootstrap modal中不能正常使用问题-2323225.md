---
title: "解决 select2在bootstrap modal中不能正常使用问题"
date: "2018-11-28 15:57:30"
category: "前端"
source: "https://blog.51cto.com/hequan/2323225"
---

### select2在bootstrap modal中不能正常使用问题

#### 设置CSS

```
        .select2-drop {
            z-index: 10050 !important;
        }

        .select2-search-choice-close {
            margin-top: 0 !important;
            right: 2px !important;
            min-height: 10px;
        }

        .select2-search-choice-close:before {
            color: black !important;
        }

        /*防止select2不会自动失去焦点*/
        .select2-container {
            z-index: 16000 !important;
        }

        .select2-drop-mask {
            z-index: 15990 !important;
        }

        .select2-drop-active {
            z-index: 15995 !important;
        }
```

#### 设置下拉

```
$("#User").select2(
  {dropdownParent: $("#Modal")}
)
```
