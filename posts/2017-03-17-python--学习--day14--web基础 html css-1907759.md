---
title: "python--学习--day14--web基础:html|css"
date: "2017-03-17 21:12:21"
category: "python"
source: "https://blog.51cto.com/hequan/1907759"
---
> **内容介绍**
>
> Python 学习 day14（web 基础）笔记：HTML 常用标签（块级 div/p/h 系列与行内 span、链接与换行）、表单各类控件（text/password/radio/checkbox/file/select/textarea/label/fieldset）、列表与表格结构；CSS 部分涵盖六类选择器（id/class/标签/层级/组合/属性）与就近优先级，以及边框、字体文本、float、display、padding/margin 等常用属性，末尾附顶栏+三栏浮动布局示例。

> **技术备注**
>
> HTML/CSS 基础语法至今通用，但笔记写法偏 HTML4 风格（`<br />` 闭合、`checked="checked"` 成对赋值），HTML5 中布尔属性直接写 `checked`、`selected` 即可。示例布局用 `float + margin: 0 auto` 是当年主流做法，现代页面多以 flex/grid 布局替代 float，初学建议直接学 flex。

---

## 1. HTML 基础标签（3.15）

常用标签示例：

```html
<a href="http://www.baidu.com">he&nbsp;quan</a>   <!-- 链接 -->
<h1>123</h1>   <!-- 标题字体加大，到 h6 -->
<p>123<br></p>   <!-- 段落，br 换行 <br /> -->
<span>hequan</span>   <!-- 行内标签 -->
<div id="1" style="position: fixed;top:0; right: 0;">1</div>   <!-- 属性 -->
```

所有标签分为两类：

- 块级标签：`div`（白板）、`H` 系列（加大加粗）、`p`（段落和段落之间有间距）
- 行内标签：`span`（白板）

标签之间可以嵌套。标签存在的意义：css 操作、js 操作。

ps：chrome 审查元素的使用：

- 定位
- 查看样式

## 2. 表单与常用标签（3.16）

登录表单，get 方式提交到后台：

```html
<form action="http://localhost:8888/index" method="get">
    <input type="text" name="user" />
    <input type="password" name="pwd"/>
    <input type="text" name="email"/>
    <input type="submit" value="登陆"/>
</form>
```

提交后台的表单（含各类控件示例）：

```html
<form enctype="multipart/form-data">
    <div>
        帐号:<input type="text" name="user" >
      <p> 密码:<input type="password" name="pwd"></p>
        <p>请选择性别</p>
        男：<input type="radio" name="gender" value="1" checked="checked">
        女：<input type="radio" name="gender" value="1">
        <p>爱好</p>
        篮球:<input type="checkbox" name="favor" value="1" >
        足球:<input type="checkbox" name="favor" value="1" >
        <p>技能</p>
        写代码:<input type="checkbox" name="skill" checked="checked">
        搭服务:<input type="checkbox" name="skill" >
        <p>上传文件</p>
        <input type="file" name="fname">
    </div>
    <textarea name="meno" >请在这里填写内容</textarea>
    <p>省份
    <select name="shengfen" size="2" multiple="multiple" >
        <option value="1" selected="selected">北京</option>
        <option value="2">上海</option>
    </select>
    </p>
    <input type="submit" value="提交">
    <input type="reset" value="重置">
</form>
```

其余常用标签：

- `img`：`src`（地址）、`alt`（加载失败提示）、`title`（悬停提示）
- 列表：`ul > li`（无序）、`ol > li`（有序）、`dl > dt / dd`（定义列表）
- 表格：`table > thead > tr > th`、`tbody > tr > td`；`colspan=''` 跨列、`rowspan=''` 跨行
- `label`：用于点击文字，使得关联的标签获取光标

```html
<label for="username">用户名：</label>
<input id="username" type="text" name="user" />
```

- `fieldset`（边框）分组，`legend` 为组标题

## 3. CSS 基础（3.17）

在标签上设置 style 属性：

```css
background-color: #2459a2;
height: 48px;
```

编写 css 样式的几种方式：

1. 标签的 style 属性
2. 写在 head 里面的 style 标签中，常用选择器：

```css
/* id 选择器 */
#i1{
  background-color: #2459a2;
  height: 48px;
}
/* class 选择器 ******：.名称{}，标签写 <标签 class='名称'> </标签> */
/* 标签选择器：div{}，所有 div 设置上此样式 */
/* 层级选择器（空格）****** */
.c1 .c2 div{
}
/* 组合选择器（逗号）****** */
#c1,.c2,div{
}
/* 属性选择器 ******：对选择到的标签再通过属性进行一次筛选 */
.c1[n='alex']{ width:100px; height:200px; }
```

PS：优先级——标签上 style 优先，其余看编写顺序，就近原则。

2.5 css 样式也可以写在单独的文件中：

```html
<link rel="stylesheet" href="commons.css" />
```

3、注释：`/*  */`

4、边框：

- 宽度，样式，颜色（`border: 4px dotted red;`）
- `border-left` 等单边

5、尺寸与文本：

- `height` 高度（可百分比）；`width` 宽度（像素、百分比）
- `text-align: center` 水平方向居中
- `line-height` 垂直方向根据标签高度居中
- `color` 字体颜色；`font-size` 字体大小；`font-weight` 字体加粗

6、float：让标签浪起来，块级标签也可以堆叠，老子管不住：

7、display：

```css
display: none;          /* 让标签消失 */
display: inline;
display: block;
display: inline-block;  /* 具有 inline：默认自己有多少占多少；
                           具有 block：可以设置高度、宽度、padding、margin */
```

`******`：行内标签无法设置高度、宽度、padding、margin；块级标签可以设置。

8、`padding`（内边距）与 `margin`（外边距，`margin: 0 auto` 常用于水平居中）；
`padding-top` 为自身内部边距。

页面布局示例（顶栏 + 三栏浮动）：

```html
<body style="margin: 0;auto:0;">
<div class="pg-header">
    <div style="width: 980px;margin: 0 auto;">   <!-- 居中 -->
        <div style="float: left;">收藏本站</div>
        <div style="float: right;">
            <a>登陆</a>
            <a>注册</a>
        </div>
    </div>
</div>
<div style="width: 300px;border:0px solid red;">   <!-- 浮动 -->
    <div style="width: 96px;height:30px;border:1px solid green;float: left">1</div>
    <div style="width: 96px;height:30px;border:1px solid green;float: left">2</div>
    <div style="width: 96px;height:30px;border:1px solid green;float: left">3</div>
</div>
```
