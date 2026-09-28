---
title: "python--学习--day14--web基础:html|css"
date: "2017-03-17 21:12:21"
category: "python"
source: "https://blog.51cto.com/hequan/1907759"
---
> **内容介绍**
>
> 本文是Python 编程实战笔记,记录了「python--学习--day14--web基础:html|css」的相关内容。

> **技术备注**
>
> 本文写于较早年代,文中软件版本与命令在新系统上可能有差异,执行前请核对当前环境。

---

3.15

```html
<a href="http://www.baidu.com">he&nbsp;quan</a> ##连接
<p>123<br></p>    段落   br换行 <br />
<h1>123</h1>   标题字体加大，到h6
<span>hequan</span>  内链标签
所有标签分为：
    块级标签： div（白板），H系列（加大加粗），p标签（段落和段落之间有间距）
    行内标签： span（白板）
标签之间可以嵌套
标签存在的意义，css操作，js操作
ps:chorme审查元素的使用
- 定位
- 查看样式
<div id="1"  style="position: fixed;top:0; right: 0;">1</div>   属性
```

---

3.16

```html
登录
<form action="http://localhost:8888/index"  method="get">
    <input type="text"  name="user" />
    <input type="password" name="pwd"/>
    <input type="text" name="email"/>
    <input type="submit" value="登陆"/>
</form>
提交后台的
<form  enctype="multipart/form-data">
    <div>
        帐号:<input  type="text"  name="user" >
      <p> 密码:<input type="password" name="pwd"></p>
        <p>请选择性别</p>
        男：<input type="radio"  name="gender"  value="1"  checked="checked">
        女：<input type="radio"  name="gender"  value="1">
        <p>爱好</p>
        篮球:<input type="checkbox"  name="favor"  value="1" >
        足球:<input type="checkbox"  name="favor"  value="1" >
        <p>技能</p>
        写代码:<input type="checkbox" name="skill"  checked="checked">
        搭服务:<input type="checkbox" name="skill"  >
        <p>上传文件</p>
        <input type="file" name="fname">
    </div>
    <textarea name="meno" >请在这里填写内容</textarea>
    <p>省份
    <select name="shengfen" size="2" multiple="multiple" >
        <option value="1" selected="selected">北京</option> 
        <option value="2">上海</option>
    </select>
    </p>
    <input type="submit"  value="提交">
    <input type="reset" value="重置">
</form>
- img
    src
    alt
    title
- 列表
    ul
        li
    ol
        li
    dl
        dt
        dd
- 表格
    table
        thead
            tr
                th
        tbody
            tr
                td
    colspan = ''
    rowspan = ''
- label
    用于点击文件，使得关联的标签获取光标
    <label for="username">用户名：</label>
    <input id="username" type="text" name="user" />
- fieldset  ##边款
    legend
```

---

3.17

```html
CSS
    在标签上设置style属性：
        background-color: #2459a2;
        height: 48px;
        ...
    编写css样式：
        1. 标签的style属性
        2. 写在head里面 style标签中写样式
            - id选择区
                  #i1{
                    background-color: #2459a2;
                    height: 48px;
                  }
            - class选择器 ******
                  .名称{
                    ...
                  }
                  <标签 class='名称'> </标签>
            - 标签选择器
                    div{
                        ...
                    }
                    所有div设置上此样式
            - 层级选择器（空格） ******
                  .c1 .c2 div{
                  }
            - 组合选择器（逗号） ******
                    #c1,.c2,div{
                  }
            - 属性选择器 ******
                  对选择到的标签再通过属性再进行一次筛选
                  .c1[n='alex']{ width:100px; height:200px; }
            PS:
                - 优先级，标签上style优先，编写顺序，就近原则
        2.5 css样式也可以写在单独文件中
            <link rel="stylesheet" href="commons.css" />
        3、注释
            /*  */
        4、边框
            - 宽度，样式，颜色  (border: 4px dotted red;)
            - border-left
        5、
            height，        高度 百分比
            width，          宽度 像素，百分比
            text-align:ceter, 水平方向居中
            line-height，垂直方向根据标签高度
            color、    字体颜色
            font-size、 字体大小
            font-weight 字体加粗
        6、float
            让标签浪起来，块级标签也可以堆叠
            老子管不住：
                7、display
            display: none; -- 让标签消失
            display: inline;
            display: block;
            display: inline-block;
                    具有inline,默认自己有多少占多少
                    具有block，可以设置无法设置高度，宽度，padding  margin
            ******
            行内标签：无法设置高度，宽度，padding  margin
            块级标签：设置高度，宽度，padding  margin
        8、   padding       margin(0,auto)
         边距: 内边距        外边距
           padding-top:自身内部边距
<body style="margin: 0;auto:0;">
<div class="pg-header">
    <div style="width: 980px;margin: 0 auto;">  ##居中
        <div style="float: left;">收藏本站</div>
        <div style="float: right;">
            <a>登陆</a>
            <a>注册</a>
        </div>
    </div>
</div>
<div style="width: 300px;border:0px solid red;">
    <div style="width: 96px;height:30px;border:1px solid green;float: left">1</div>
    <div style="width: 96px;height:30px;border:1px solid green;float: left">2</div>
    <div style="width: 96px;height:30px;border:1px solid green;float: left">3</div>
    ##浮动
</div>
```
