---
title: "python--learning--day14--web basics: html|css"
date: "2017-03-17 21:12:21"
category: "python"
source: "https://blog.51cto.com/hequan/1907759"
lang: "en"
---
> **About this post**
>
> Notes from day14 of learning Python (web basics): common HTML tags (block-level div/p/h series and inline span, links and line breaks), the various form controls (text/password/radio/checkbox/file/select/textarea/label/fieldset), and list and table structures; the CSS part covers six types of selectors (id/class/tag/descendant/grouped/attribute) and nearest-wins precedence, plus common properties such as border, font and text, float, display, and padding/margin, ending with a top-bar + three-column float layout example.

> **Technical notes**
>
> The basic HTML/CSS syntax here is still valid today, but the notes are written in an HTML4 style (`<br />` closing tags, `checked="checked"` paired assignment); in HTML5 boolean attributes can simply be written as `checked` or `selected`. The example layout uses `float + margin: 0 auto`, which was the mainstream approach at the time; modern pages mostly replace float with flex/grid layouts, and beginners are better off learning flex directly.

---

## 1. Basic HTML Tags (3.15)

Common tag examples:

```html
<a href="http://www.baidu.com">he&nbsp;quan</a>   <!-- link -->
<h1>123</h1>   <!-- heading: larger font, up to h6 -->
<p>123<br></p>   <!-- paragraph; br for a line break <br /> -->
<span>hequan</span>   <!-- inline tag -->
<div id="1" style="position: fixed;top:0; right: 0;">1</div>   <!-- attributes -->
```

All tags fall into two categories:

- Block-level tags: `div` (blank slate), the `H` series (larger and bolder), `p` (spacing between paragraphs)
- Inline tags: `span` (blank slate)

Tags can be nested. The whole point of tags: CSS manipulation and JS manipulation.

PS: using Chrome's Inspect Element:

- Locating elements
- Inspecting styles

## 2. Forms and Common Tags (3.16)

A login form, submitted to the backend via GET:

```html
<form action="http://localhost:8888/index" method="get">
    <input type="text" name="user" />
    <input type="password" name="pwd"/>
    <input type="text" name="email"/>
    <input type="submit" value="Login"/>
</form>
```

A form submitted to the backend (with examples of the various controls):

```html
<form enctype="multipart/form-data">
    <div>
        Account:<input type="text" name="user" >
      <p> Password:<input type="password" name="pwd"></p>
        <p>Please select your gender</p>
        Male:<input type="radio" name="gender" value="1" checked="checked">
        Female:<input type="radio" name="gender" value="1">
        <p>Hobbies</p>
        Basketball:<input type="checkbox" name="favor" value="1" >
        Football:<input type="checkbox" name="favor" value="1" >
        <p>Skills</p>
        Coding:<input type="checkbox" name="skill" checked="checked">
        Server setup:<input type="checkbox" name="skill" >
        <p>Upload a file</p>
        <input type="file" name="fname">
    </div>
    <textarea name="meno" >Please enter your content here</textarea>
    <p>Province
    <select name="shengfen" size="2" multiple="multiple" >
        <option value="1" selected="selected">Beijing</option>
        <option value="2">Shanghai</option>
    </select>
    </p>
    <input type="submit" value="Submit">
    <input type="reset" value="Reset">
</form>
```

Other common tags:

- `img`: `src` (address), `alt` (text shown when loading fails), `title` (tooltip on hover)
- Lists: `ul > li` (unordered), `ol > li` (ordered), `dl > dt / dd` (definition list)
- Tables: `table > thead > tr > th`, `tbody > tr > td`; `colspan=''` spans columns, `rowspan=''` spans rows
- `label`: clicking the text gives focus to the associated input

```html
<label for="username">Username:</label>
<input id="username" type="text" name="user" />
```

- `fieldset` groups content with a border, and `legend` is the group title

## 3. CSS Basics (3.17)

Setting the style attribute on a tag:

```css
background-color: #2459a2;
height: 48px;
```

Several ways to write CSS styles:

1. The tag's `style` attribute
2. In a `style` tag inside `head`; common selectors:

```css
/* id selector */
#i1{
  background-color: #2459a2;
  height: 48px;
}
/* class selector ******: .name{}, written in the tag as <tag class='name'> </tag> */
/* tag selector: div{}, applies this style to all divs */
/* descendant selector (space) ****** */
.c1 .c2 div{
}
/* grouped selector (comma) ****** */
#c1,.c2,div{
}
/* attribute selector ******: further filters the selected tags by attribute */
.c1[n='alex']{ width:100px; height:200px; }
```

PS: precedence — an inline style on the tag wins; for the rest, order of writing applies, nearest wins.

2.5 CSS can also be placed in a separate file:

```html
<link rel="stylesheet" href="commons.css" />
```

3. Comments: `/*  */`

4. Borders:

- Width, style, color (`border: 4px dotted red;`)
- Single sides such as `border-left`

5. Dimensions and text:

- `height` (percentages allowed); `width` (pixels, percentages)
- `text-align: center` centers horizontally
- `line-height` centers vertically based on the tag's height
- `color` font color; `font-size` font size; `font-weight` bold text

6. float: lets tags cut loose — block-level tags can stack too, and nothing can rein them in:

7. display:

```css
display: none;          /* makes the tag disappear */
display: inline;
display: block;
display: inline-block;  /* inline: by default takes up only as much width as it needs;
                           block: height, width, padding and margin can be set */
```

`******`: inline tags cannot be given height, width, padding or margin; block-level tags can.

8. `padding` (inner spacing) and `margin` (outer spacing; `margin: 0 auto` is commonly used for horizontal centering); `padding-top` is the padding inside the element itself.

Page layout example (top bar + three-column float):

```html
<body style="margin: 0;auto:0;">
<div class="pg-header">
    <div style="width: 980px;margin: 0 auto;">   <!-- centered -->
        <div style="float: left;">Bookmark this site</div>
        <div style="float: right;">
            <a>Login</a>
            <a>Register</a>
        </div>
    </div>
</div>
<div style="width: 300px;border:0px solid red;">   <!-- float -->
    <div style="width: 96px;height:30px;border:1px solid green;float: left">1</div>
    <div style="width: 96px;height:30px;border:1px solid green;float: left">2</div>
    <div style="width: 96px;height:30px;border:1px solid green;float: left">3</div>
</div>
```
