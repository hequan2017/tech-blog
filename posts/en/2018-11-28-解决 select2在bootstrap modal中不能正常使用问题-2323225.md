---
title: "Fixing select2 Not Working Properly in a Bootstrap Modal"
date: "2018-11-28 15:57:30"
category: "frontend"
source: "https://blog.51cto.com/hequan/2323225"
lang: "en"
---
> **About this post**
>
> This post fixes two problems that occur when embedding a select2 dropdown in a Bootstrap modal: the search box cannot receive input and the dropdown layer is hidden behind the modal. On one hand, raising the z-index of elements such as .select2-drop makes the dropdown layer appear above the modal; on the other hand, setting dropdownParent to the modal container when initializing select2 keeps the dropdown menu from being hijacked by the modal's focus-control logic.

> **Technical notes**
>
> The CSS in this post is based on class names from the Bootstrap 3 + select2 3.x/4.x era (.select2-drop). select2 4.x has switched to new class names such as .select2-dropdown, and the modal stacking order in Bootstrap 5 has changed as well, so confirm the versions you are using before copying everything verbatim. The dropdownParent approach still works in select2 4.x.

---

### select2 not working properly in a Bootstrap modal

#### Set the CSS

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

        /* Prevent select2 from failing to lose focus automatically */
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

#### Set the dropdown

Specify dropdownParent when initializing select2:

```js
$(selector).select2({
    dropdownParent: $("#Modal")
});
```
