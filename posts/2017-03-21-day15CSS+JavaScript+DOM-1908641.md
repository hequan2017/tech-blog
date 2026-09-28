---
title: "day15CSS+JavaScript+DOM"
date: "2017-03-21 09:29:13"
category: "python"
source: "https://blog.51cto.com/hequan/1908641"
---

```js
CSS补充
    position:  ##多层
        a. fiexd => 固定在页面的某个位置         ##返回顶端
        b. relative + absolute          
            <div style='position:relative;'>
                ##以外面的父级div框为标准，定位自己
            </div>
    opcity: 0.5 透明度
    z-index: 层级顺序，大的在上面   ##点击，弹出一个框，背景变成灰色透明
    overflow: hidden,auto  ##图片  hiddon，超过规定的范围就隐藏，auto出现滚动条
/*当鼠标移动到当前标签上时，以下css属性才生效*/
.pg-header .menu:hover{
    background-color: blue;
}
    background-p_w_picpath:url('p_w_picpath/4.gif'); # 默认，div大，图片重复访
    background-repeat: repeat-y;  # 图片应用只竖着加，背景色   no-repeat不堆叠
    background-position-x: ##移动   
    background-position-y: ##移动  正向下，负向上     扣图标  加图片大小
    background-position: 10px 10px;
   
示例：输入框  最右边有一个图片
<div style="height: 35px;width: 400px;position: relative;">
    <input type="text" style="height: 35px;width: 370px;padding-right: 30px" />
    <span style="position:absolute;right:3px;top:10px;background-p_w_picpath: url(i_name.jpg);height: 16px;width: 16px;display: inline-block;"></span>
</div>
```

```js
<script  src="路径">
//javascript
</script>

变量
     name = 'hequan'   全局变量
     var name='hequan' 局部变量
数字
     age = 18;
     i = parseInt(age);
字符串
     a = "hequan"
     a.length 长度
     a.substring(起始位置，结束位置)
     a.charAt(索引位置)
函数
     function func(){
}
布尔类型
     小写
字典
    a={'k1':'v1'}
列表（数组）
     a = [11,22,33]
函数
     function  函数名(){
     }
```

```js
定时器：
     setInterval('执行的代码',间隔时间5000);
查找：
     document.getElementById('i1').innerText;
自动滚动:
function func() {
    var tag = document.getElementById('i1')
    var content = tag.innerText
    var f = content.charAt(0);
    var l = content.substring(1, tag.length)
    var new_content = l + f;
    tag.innerText = new_content
}
setInterval('func()',500);
```

```js
for循环
     a = [11,22,33,44]
     for (var item in  a ){     //循环默认都是 key
          console.log(a[item]);
     }

     for (var i=0;i<a.length;i++){   //数组可以，字典不可以
    
     }

条件语句
     if(条件){
    
     }else  if（条件）{
    
     }else{
    
     }
     
     == 只要值相等
     === 值相等 类型也要相等
     &&  and
     ||   or
```

```js
1、找到标签
    获取单个元素        document.getElementById('i1')
    获取多个元素（列表）document.getElementsByTagName('div')
    获取多个元素（列表）document.getElementsByClassName('c1')
    a. 直接找
        document.getElementById            根据ID获取一个标签
        document.getElementsByName          根据name属性获取标签集合
        document.getElementsByClassName    根据class属性获取标签集合
        document.getElementsByTagName      根据标签名获取标签集合
    b. 间接
        tag = document.getElementById('i1')
        parentElement          // 父节点标签元素
        children                // 所有子标签
        firstElementChild      // 第一个子标签元素
        lastElementChild        // 最后一个子标签元素
        nextElementtSibling    // 下一个兄弟标签元素
        previousElementSibling  // 上一个兄弟标签元素
2、操作标签
    a. innerText
        获取标签中的文本内容
        标签.innerText
        对标签内部文本进行重新复制
        标签.innerText = ""
    b. className  //样式名字
        tag.className =》 直接整体做操作
        tag.classList.add('样式名')  添加指定样式
        tag.classList.remove('样式名')  删除指定样式
        PS：
            <div onclick='func();'>点我</div>
            <script>
                function func(){

                }

            </script>
    c. checkbox
            获取值
            checkbox对象.checked
            设置值
            checkbox对象.checked = true
```

```js
例子
function ShowModel(){
    document.getElementById('i1').classList.remove('hide');
    document.getElementById('i2').classList.remove('hide');
}
function HideModel(){
    document.getElementById('i1').classList.add('hide');
    document.getElementById('i2').classList.add('hide');
}
function ChooseAll(){
    var tbody = document.getElementById('tb');
    // 获取所有的tr
    var tr_list = tbody.children;
    for(var i=0;i<tr_list.length;i++){
        // 循环所有的tr，current_tr
        var current_tr = tr_list[i];
        var checkbox = current_tr.children[0].children[0];
        checkbox.checked = true;
    }
}
     function ChangeMenu(nid){
        var current_header = document.getElementById(nid);
        var item_list = current_header.parentElement.parentElement.children;
        for(var i=0;i<item_list.length;i++){
            var current_item = item_list[i];
            current_item.children[1].classList.add('hide');
        }
        current_header.nextElementSibling.classList.remove('hide');
     }
```
