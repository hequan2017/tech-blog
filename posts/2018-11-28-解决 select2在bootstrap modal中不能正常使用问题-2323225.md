---
title: "解决 select2在bootstrap modal中不能正常使用问题"
date: "2018-11-28 15:57:30"
category: "前端"
source: "https://blog.51cto.com/hequan/2323225"
---
> **内容介绍**
>
> 本文是前端开发学习与实践,记录了「解决 select2在bootstrap modal中不能正常使用问题」的相关内容。主要涉及:### select2在bootstrap modal中不能正常使用问题 #### 设置CSS #### 设置下拉…

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

### select2在bootstrap modal中不能正常使用问题

#### 设置CSS

```shell
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

#### 设置下拉

  {dropdownParent: $("#Modal")}
)
```
