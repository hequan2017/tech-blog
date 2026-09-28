---
title: "解决 select2在bootstrap modal中不能正常使用问题"
date: "2018-11-28 15:57:30"
category: "前端"
source: "https://blog.51cto.com/hequan/2323225"
---
> **内容介绍**
>
> 本文解决 select2 下拉框嵌入 Bootstrap modal 时搜索框无法输入、下拉层被遮挡的问题：一方面通过提高 .select2-drop 等元素的 z-index 让下拉层显示在 modal 之上，另一方面在初始化 select2 时设置 dropdownParent 指向 modal 容器，避免下拉菜单被 modal 的焦点控制逻辑劫持。

> **技术备注**
>
> 文中 CSS 基于 Bootstrap 3 + select2 3.x/4.x 时代的类名（.select2-drop），select2 4.x 已改用 .select2-dropdown 等新类名，Bootstrap 5 的 modal 层级也有变化，照搬时请先确认所用版本；dropdownParent 方案在 select2 4.x 中依然有效。

---

### select2在bootstrap modal中不能正常使用问题

#### 设置CSS

```css
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

初始化 select2 时指定 dropdownParent：

```js
$(selector).select2({
    dropdownParent: $("#Modal")
});
```
