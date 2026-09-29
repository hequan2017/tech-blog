---
title: "Day 15: CSS + JavaScript + DOM"
date: "2017-03-21 09:29:13"
category: "python"
source: "https://blog.51cto.com/hequan/1908641"
lang: "en"
---
> **About this post**
>
> Front-end study notes, day 15: the CSS supplement covers position, opacity,
> z-index, overflow, the :hover pseudo-class, and background images
> (background-image / repeat / position); the JavaScript part goes over
> variable scope, numbers/strings/dictionaries/arrays, functions, and timers,
> with a small marquee example; the DOM part organizes direct and indirect
> tag lookups by id/tag/class and three kinds of operations — innerText,
> className, and checkbox — ending with function examples for a modal dialog,
> select-all in a table, and multi-level menu switching.

> **Technical notes**
>
> 1. In the original, `background-p_w_picpath` and `p_w_picpath/4.gif` were
>    escaping errors introduced by the 51cto editor for the word `image`;
>    they have been corrected to `background-image` and `image/4.gif`.
> 2. Common typos fixed: `fiexd` → `fixed`, `opcity` → `opacity`, `hiddon` →
>    `hidden`, `nextElementtSibling` → `nextElementSibling`, and in the
>    Chinese text "recopy" → "reassign".
> 3. Passing a string as in `setInterval('func()',500)` is no longer
>    recommended; the modern form is `setInterval(func, 500)`. The discussion
>    of `var` global/local variables follows ES5; from ES6 onward, prefer
>    let/const.

---

## 1. More CSS

- `position` (multi-layer positioning):
  - `fixed`: fixed at a spot on the page (e.g. a back-to-top button)
  - `relative + absolute`: `absolute` positions itself relative to the enclosing parent (`position:relative`) div box
- `opacity: 0.5`: transparency
- `z-index`: stacking order; higher values sit on top (e.g. clicking pops up a box while the background turns gray and translucent)
- `overflow: hidden / auto`: `hidden` clips anything beyond the specified area; `auto` shows a scrollbar (commonly used for images)
- `:hover`: the following CSS properties take effect only when the mouse moves over the current tag

```css
.pg-header .menu:hover{
    background-color: blue;
}
```

Background image related:

- `background-image: url('image/4.gif');`: by default, when the div is larger, the image is placed repeatedly
- `background-repeat: repeat-y;`: the image stacks vertically only; `no-repeat` disables stacking
- `background-position-x` / `background-position-y`: shift the background image; positive moves down, negative moves up (coordinate with the image size when slicing icons)
- `background-position: 10px 10px;`

Example: an image (icon) at the far right of an input box:

```html
<div style="height: 35px;width: 400px;position: relative;">
    <input type="text" style="height: 35px;width: 370px;padding-right: 30px" />
    <span style="position:absolute;right:3px;top:10px;background-image: url(i_name.jpg);height: 16px;width: 16px;display: inline-block;"></span>
</div>
```

## 2. JavaScript Basics

Including it in a page:

```html
<script src="path">
//javascript
</script>
```

- Variables: `name = 'hequan'` is a global variable; `var name='hequan'` is a local variable
- Numbers: `age = 18; i = parseInt(age);`
- Strings: `a = "hequan"`; `a.length` for the length; `a.substring(start, end)`; `a.charAt(index)`
- Booleans: lowercase (true / false)
- Dictionaries: `a = {'k1':'v1'}`
- Lists (arrays): `a = [11,22,33]`
- Functions:

```javascript
function functionName(){
}
```

## 3. Timers and a Marquee Example

Timer: `setInterval('code to execute', interval 5000);`

Lookup: `document.getElementById('i1').innerText;`

Auto-scrolling (marquee):

```javascript
function func() {
    var tag = document.getElementById('i1')
    var content = tag.innerText
    var f = content.charAt(0);
    var l = content.substring(1, tag.length)
    var new_content = l + f;
    tag.innerText = new_content
}
setInterval('func()',500);
```

## 4. Loops and Conditionals

```javascript
for (var item in a) {        // loops default to keys
    console.log(a[item]);
}

for (var i=0;i<a.length;i++){   // works for arrays, not dictionaries
}
```

```javascript
if (condition) {
} else if (condition) {
} else {
}
```

- `==`: values equal only; `===`: values equal and types must be equal too
- `&&`: and; `||`: or

## 5. DOM Lookup and Manipulation

### 1. Finding tags

- Get a single element: `document.getElementById('i1')`
- Get multiple elements (a list): `document.getElementsByTagName('div')`, `document.getElementsByClassName('c1')`

a. Direct lookup:

- `document.getElementById`: get one tag by ID
- `document.getElementsByName`: get a collection of tags by the name attribute
- `document.getElementsByClassName`: get a collection of tags by the class attribute
- `document.getElementsByTagName`: get a collection of tags by tag name

b. Indirect lookup:

```javascript
tag = document.getElementById('i1')
tag.parentElement           // parent node tag element
tag.children                // all child tags
tag.firstElementChild       // first child tag element
tag.lastElementChild        // last child tag element
tag.nextElementSibling      // next sibling tag element
tag.previousElementSibling  // previous sibling tag element
```

### 2. Manipulating tags

a. `innerText`: reads the text content of a tag (`tag.innerText`); reassigns the text inside the tag (`tag.innerText = ""`).

b. `className` (style name): `tag.className` operates on the whole thing at once;

```javascript
tag.classList.add('styleName')    // add the given style
tag.classList.remove('styleName') // remove the given style
```

PS: event binding —

```html
<div onclick='func();'>Click me</div>
<script>
    function func(){
    }
</script>
```

c. checkbox: get the value with `checkboxObj.checked`; set it with `checkboxObj.checked = true`.

## 6. Complete Examples

```javascript
function ShowModel(){
    document.getElementById('i1').classList.remove('hide');
    document.getElementById('i2').classList.remove('hide');
}
function HideModel(){
    document.getElementById('i1').classList.add('hide');
    document.getElementById('i2').classList.add('hide');
}
function ChooseAll(){
    var tbody = document.getElementById('tb');
    // get all the tr rows
    var tr_list = tbody.children;
    for(var i=0;i<tr_list.length;i++){
        // loop over all tr rows, current_tr
        var current_tr = tr_list[i];
        var checkbox = current_tr.children[0].children[0];
        checkbox.checked = true;
    }
}
function ChangeMenu(nid){
    var current_header = document.getElementById(nid);
    var item_list = current_header.parentElement.parentElement.children;
    for(var i=0;i<item_list.length;i++){
        var current_item = item_list[i];
        current_item.children[1].classList.add('hide');
    }
    current_header.nextElementSibling.classList.remove('hide');
}
```
