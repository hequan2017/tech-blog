---
title: "day15CSS+JavaScript+DOM"
date: "2017-03-21 09:29:13"
category: "python"
source: "https://blog.51cto.com/hequan/1908641"
---
> **内容介绍**
>
> 前端学习笔记 day15：CSS 补充部分讲 position 定位、opacity 透明度、
> z-index 层级、overflow、:hover 伪类与背景图（background-image /
> repeat / position）；JavaScript 部分过变量作用域、数字/字符串/字典/
> 数组、函数、定时器并附跑马灯小例；DOM 部分整理按 id/tag/class 直接
> 与间接查找标签、innerText/className/checkbox 三类操作，末尾是模态框、
> 表格全选、多级菜单切换的函数示例。

> **技术备注**
>
> 1. 原文 `background-p_w_picpath`、`p_w_picpath/4.gif` 系 51cto 编辑器对
>    `image` 一词的转义错误，已修正为 `background-image`、`image/4.gif`。
> 2. 已修正常见笔误：`fiexd`→`fixed`、`opcity`→`opacity`、`hiddon`→
>    `hidden`、`nextElementtSibling`→`nextElementSibling`、"重新复制"→
>    "重新赋值"。
> 3. `setInterval('func()',500)` 传字符串的写法已不推荐，现代写法为
>    `setInterval(func, 500)`；文中 var 全局/局部变量说法沿用 ES5，
>    ES6 之后建议用 let/const。

---

## 1. CSS 补充

- `position`（多层定位）：
  - `fixed`：固定在页面的某个位置（如返回顶端）
  - `relative + absolute`：`absolute` 以外面的父级（`position:relative`）div 框为标准定位自己
- `opacity: 0.5`：透明度
- `z-index`：层级顺序，大的在上面（如点击弹出一个框、背景变成灰色透明）
- `overflow: hidden / auto`：`hidden` 超过规定的范围就隐藏，`auto` 出现滚动条（图片常用）
- `:hover`：当鼠标移动到当前标签上时，以下 css 属性才生效

```css
.pg-header .menu:hover{
    background-color: blue;
}
```

背景图相关：

- `background-image: url('image/4.gif');`：默认情况下 div 大、图片重复放置
- `background-repeat: repeat-y;`：图片只竖着堆叠；`no-repeat` 不堆叠
- `background-position-x` / `background-position-y`：移动背景图，正向下、负向上（扣图标时配合图片大小）
- `background-position: 10px 10px;`

示例：输入框最右边有一个图片（图标）：

```html
<div style="height: 35px;width: 400px;position: relative;">
    <input type="text" style="height: 35px;width: 370px;padding-right: 30px" />
    <span style="position:absolute;right:3px;top:10px;background-image: url(i_name.jpg);height: 16px;width: 16px;display: inline-block;"></span>
</div>
```

## 2. JavaScript 基础

在页面中引入：

```html
<script src="路径">
//javascript
</script>
```

- 变量：`name = 'hequan'` 全局变量；`var name='hequan'` 局部变量
- 数字：`age = 18; i = parseInt(age);`
- 字符串：`a = "hequan"`；`a.length` 长度；`a.substring(起始位置, 结束位置)`；`a.charAt(索引位置)`
- 布尔类型：小写（true / false）
- 字典：`a = {'k1':'v1'}`
- 列表（数组）：`a = [11,22,33]`
- 函数：

```javascript
function 函数名(){
}
```

## 3. 定时器与跑马灯示例

定时器：`setInterval('执行的代码', 间隔时间5000);`

查找：`document.getElementById('i1').innerText;`

自动滚动（跑马灯）：

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

## 4. 循环与条件语句

```javascript
for (var item in a) {        // 循环默认都是 key
    console.log(a[item]);
}

for (var i=0;i<a.length;i++){   // 数组可以，字典不可以
}
```

```javascript
if (条件) {
} else if (条件) {
} else {
}
```

- `==`：只要值相等；`===`：值相等、类型也要相等
- `&&`：and；`||`：or

## 5. DOM 查找与操作

### 1. 找到标签

- 获取单个元素：`document.getElementById('i1')`
- 获取多个元素（列表）：`document.getElementsByTagName('div')`、`document.getElementsByClassName('c1')`

a. 直接找：

- `document.getElementById`：根据 ID 获取一个标签
- `document.getElementsByName`：根据 name 属性获取标签集合
- `document.getElementsByClassName`：根据 class 属性获取标签集合
- `document.getElementsByTagName`：根据标签名获取标签集合

b. 间接找：

```javascript
tag = document.getElementById('i1')
tag.parentElement           // 父节点标签元素
tag.children                // 所有子标签
tag.firstElementChild       // 第一个子标签元素
tag.lastElementChild        // 最后一个子标签元素
tag.nextElementSibling      // 下一个兄弟标签元素
tag.previousElementSibling  // 上一个兄弟标签元素
```

### 2. 操作标签

a. `innerText`：获取标签中的文本内容（`标签.innerText`）；对标签内部文本进行重新赋值（`标签.innerText = ""`）。

b. `className`（样式名字）：`tag.className` 直接整体做操作；

```javascript
tag.classList.add('样式名')    // 添加指定样式
tag.classList.remove('样式名') // 删除指定样式
```

PS：事件绑定——

```html
<div onclick='func();'>点我</div>
<script>
    function func(){
    }
</script>
```

c. checkbox：获取值 `checkbox对象.checked`；设置值 `checkbox对象.checked = true`。

## 6. 综合示例

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
    // 获取所有的tr
    var tr_list = tbody.children;
    for(var i=0;i<tr_list.length;i++){
        // 循环所有的tr，current_tr
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
