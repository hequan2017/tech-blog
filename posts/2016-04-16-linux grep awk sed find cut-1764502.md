---
title: "linux grep awk sed  find  cut"
date: "2016-04-16 16:12:06"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764502"
---
> **内容介绍**
>
> 文本处理五件套速查笔记:grep 的基础正则（^ $ . * [] \? \{m,n\} \< \> \(\)
> 分组等）与 -v/-o/-i/-A/-B/-C/-E 等选项;sed 的 -n/-e/-f/-r/-i 选项和
> a/c/d/i/p/s 动作;awk 详解——语法结构、BEGIN/END、-F/-v 参数、
> NR/FNR/FS/OFS/NF/RS/ORS 内置变量、关联数组与多维数组、读取 shell 变量、
> getline、输出重定向、管道与 system 调用 shell 命令;find 按名称/权限/属主/
> 类型/大小/时间（-amin/-atime/-cmin/-ctime/-mmin/-mtime）查找与 -exec/-ok;
> cut 按字节（-b）、字符（-c）、域（-d/-f）三种定位方式的详细示例与缺陷。

> **技术备注**
>
> 内容取自 2009 年前后的经典教程（鸟哥私房菜、《UNIX Shells By Example》等）,
> 命令本身沿用至今。三点更新:现代发行版已默认为 grep 配置 `--color=auto` 别名;
> 文中"awk 数组遍历顺序与 python 字典一致"的说法基于 Python 3.6 之前,Python
> 3.7+ 字典已保证按插入顺序遍历;示例中 `sort +1` 为旧式语法,GNU sort 应写作
> `sort -k2`。

---

## 1. grep

### 1.1 基本正则

- `^`:锚定行首的符合条件的内容,用法格式"^pattern";
- `$`:锚定行尾的符合条件的内容,用法格式"pattern$";
- `.`:匹配任意单个字符;
- `*`:匹配紧挨在其前面的字符任意次;
  - `a*b`:ab, aab, acb, b
- `.*`:匹配任意长度的任意字符;
- `[]`:匹配指定范围内的任意单个字符;
- `[^]`:匹配指定范围外的任意单个字符;
- `\?`:匹配紧挨在其前面的字符 0 次或 1 次;
- `\{m,n\}`:匹配其前面的字符至少 m 次,至多 n 次;
- `\{0,n\}`:至多 n 次;0-n 次;
- `\{m,\}`:至少 m 次;
- `\{m\}`:精确匹配 m 次;
- `\<`:锚定词首,用法格式:\<pattern
- `\>`:锚定词尾,用法格式:pattern\>
- `\(\)`:分组,用法格式: \(pattern\)

### 1.2 grep 的选项

- `--color=auto`:自动为匹配的字符附色

```shell
export GREP_COLOR='01;36'
```

- `-r`:递归搜索,用法同 `-d recurse`（递归）
- `-v`:反向选取,只显示不符合模式的行;
- `-o`:只显示被模式匹配到的字串,而不是整个行;
- `-i`:不区分字符大小写;
- `-A #`:显示匹配到的行时,顺带显示其后面的 # 个行;
- `-B #`:前面的 # 行;
- `-C #`:前后的 # 行;
- `-E`:使用扩展的正则表达式

## 2. sed

sed 命令行格式为:

```shell
sed [-nefri] 'command' 输入文本
```

常用选项:

- `-n`:使用安静（silent）模式。在一般 sed 的用法中,所有来自 STDIN 的资料一般都会被列出到萤幕上。但如果加上 -n 参数后,则只有经过 sed 特殊处理的那一行（或者动作）才会被列出来。
- `-e`:直接在指令列模式上进行 sed 的动作编辑;
- `-f`:直接将 sed 的动作写在一个档案内,-f filename 则可以执行 filename 内的 sed 动作;
- `-r`:sed 的动作支援的是延伸型正规表示法的语法。（预设是基础正规表示法语法）
- `-i`:直接修改读取的档案内容,而不是由萤幕输出。

常用命令（动作）:

- `a`:新增,a 的后面可以接字串,而这些字串会在新的一行出现（目前的下一行）;
- `c`:取代,c 的后面可以接字串,这些字串可以取代 n1,n2 之间的行;
- `d`:删除,因为是删除啊,所以 d 后面通常不接任何咚咚;
- `i`:插入,i 的后面可以接字串,而这些字串会在新的一行出现（目前的上一行）;
- `p`:列印,亦即将某个选择的资料印出。通常 p 会与参数 sed -n 一起运作;
- `s`:取代,可以直接进行取代的工作哩!通常这个 s 的动作可以搭配正规表示法!例如 1,20s/old/new/g 就是啦!

## 3. awk

### 3.1 简介与开胃例子

awk 非常的优秀,运行效率高,而且代码简单,对格式化的文本处理能力超强。基本上 grep 和 sed 能干的活 awk 全部都能干,而且干得更好。

先来一个很爽的例子:文件 a,统计文件 a 的第一列中是浮点数的行的浮点数的平均值。用 awk 来实现只需要一句话就可以搞定（当然,这个东东用 python 也可以很轻松的实现,只是无论如何都得新建一个文件;别妄想用 bash shell 来做,那可是浮点数!!!）

```shell
cat a
```

```text
1.021 33
1#.ll   44
2.53 6
ss    7
```

```shell
awk 'BEGIN{total = 0;len = 0} {if($1~/^[0-9]+\.[0-9]*/){total += $1; len++}} END{print total/len}' a
```

niubility!

### 3.2 语法

```shell
awk [-F re] [parameter...] ['program'] [-f 'programfile'] [in_file_list]
```

awk 里面的 BEGIN、END 结构:BEGIN 和 END 中的语句分别在开始读取文件（in_file）之前和读取完文件之后发挥作用,可以理解为初始化和扫尾。

awk 里面的 if..else、while、do..while、for、break、continue、printf 语法都和 C 语言的语法一致;而且 awk 支持使用 `if (key in array)` 这样的判断语句（其中,array 是数组,这一点和 python 的语法非常相像。）;awk 支持使用 `for (key in array)` 这样的语法来遍历数组（也是和 python 的语法很相像。）。

### 3.3 常用参数

- `-F re`:允许 awk 更改其字段分隔符
- `-v var=val`:把 val 值赋值给 var（变量通信的好方法啊～～今天才知道这个选项,想想之前写的代码,抓狂啊～～）。如果有多个变量要赋值,那么就写多个 -v,每个变量赋值对应一个 -v

例如要打印文件 a 的第 num 行到 num+num1 行之间的行:

```shell
awk -v num=$num -v num1=$num1 'NR==num,NR==num+num1{print}' a
```

- `-f progfile`:允许 awk 调用并执行 progfile 程序文件,当然 progfile 必须是一个符合 awk 语法的程序文件

### 3.4 常用内置变量

- **ARGC**:命令行参数的个数
- **ARGV**:命令行参数数组
- **ARGIND**:当前被处理文件的 ARGV 标志符

例如有两个文件 a 和 b:

```shell
awk '{if(ARGIND==1){print "处理a文件"} if(ARGIND==2){print "处理b文件"}}' a b
```

文件处理的顺序是先扫描完 a 文件,再扫描 b 文件。

- **NR**:已经读出的记录数
- **FNR**:当前文件的记录数

上面的例子也可以写成这样:

```shell
awk 'NR==FNR{print "处理文件a"} NR > FNR{print "处理文件b"}' a b
```

输入文件 a 和 b,由于先扫描 a,所以扫描 a 的时候必然有 NR==FNR,然后扫描 b 的时候,FNR 从 1 开始计数,而 NR 则接着 a 的行数继续计数,所以 NR > FNR。

例如要显示文件的第 10 行至第 15 行:

```shell
awk 'NR==10,NR==15{print}' a
```

- **FS**:输入字段分隔符（缺省为 space）,相当于 -F 选项

```shell
awk -F ':' '{print}' a
awk 'BEGIN{FS=":"}{print}' a    # 两者是一样的
```

- **OFS**:输出字段分隔符（缺省为 space）

```shell
awk -F ':' 'BEGIN{OFS=";"}{print $1,$2,$3}' b
```

如果 cat b 为:

```text
1:2:3
4:5:6
```

那么把 OFS 设置成 ";" 后就会输出:

```text
1;2;3
4;5;6
```

（小注释:awk 把分割后的第 1、2、3 个字段用 $1,$2,$3... 表示,$0 表示整个记录（一般就是一整行））

- **NF**:当前记录中的字段个数

```shell
awk -F ':' '{print NF}' b
```

输出为:

```text
3
3
```

表明 b 的每一行用分隔符 ":" 分割后都有 3 个字段。

可以用 NF 来控制输出符合要求的字段数的行,这样可以处理掉一些异常的行:

```shell
awk -F ':' '{if (NF == 3) print}' b
```

- **RS**:输入记录分隔符,缺省为 "\n"

缺省情况下,awk 把一行看作一个记录;如果设置了 RS,那么 awk 按照 RS 来分割记录。

例如文件 c,cat c 为:

```text
hello world; I want to go swimming tomorrow;hiahia
```

运行 `awk 'BEGIN{ RS = ";" } {print}' c` 的结果为:

```text
hello world
I want to go swimming tomorrow
hiahia
```

合理的使用 RS 和 FS 可以使得 awk 处理更多模式的文档,例如可以一次处理多行。例如文档 d,cat d 的输出为（每个记录使用空行分割,每个字段使用换行符分割）:

```text
1 2
3 4 5

6 7
8 9 10
11 12

hello
```

这样的 awk 也很好写:

```shell
awk 'BEGIN{ FS = "\n"; RS = ""} {print NF}' d
```

输出:

```text
2
3
1
```

- **ORS**:输出记录分隔符,缺省为换行符,控制每个 print 语句后的输出符号

```shell
awk 'BEGIN{ FS = "\n"; RS = ""; ORS = ";"} {print NF}' d
```

输出:

```text
2;3;1
```

### 3.5 awk 的数组

awk 的数组是一个很值得一说的东东。awk 的数组从行为上看的话更像关联数组,或者说 map、字典,或者说散列。awk 的数组接受字符串下标,并接受速度很快的 in 查询。

文件 e 是由小写的字母组成,cat e 输出为:

```text
a
b
z
...
```

如果要统计不同的字母出现的个数,那么可以使用数组来实现:

```shell
awk '{arr[$0]++} END{ for (key in arr) print key, "-->",arr[key] }' e
```

使用 `for(key in arr)` 来遍历数组的时候,输出的次序是不可预测的,这一点跟 python 的字典遍历是一致的。

在 gawk 中,可以使用 asort 内置函数实现数组的排序,其他的 awk 版本中还没有发现有类似的排序函数。一个折中的办法是先 awk 完再用管道传给 sort 来排序。sort 使用 -k 选项可以控制使用指定列排序。

### 3.6 awk 的多维数组

awk 的多维数组在本质上是一维数组,更确切一点,awk 在存储上并不支持多维数组。awk 提供了逻辑上模拟二维数组的访问方式。例如,`array[2,4] = 1` 这样的访问是允许的。awk 使用一个特殊的字符串 SUBSEP (\034) 作为分割字段,在上面的例子中,关联数组 array 存储的键值实际上是 2\0344。

类似一维数组的成员测试,多维数组可以使用 `if ( (i,j) in array)` 这样的语法,但是下标必须放置在圆括号中。

类似一维数组的循环访问,多维数组使用 `for ( item in array )` 这样的语法遍历数组。与一维数组不同的是,多维数组必须使用 split() 函数来访问单独的下标分量。`split ( item, subscr, SUBSEP)`。

### 3.7 awk 读取 shell 中的变量

可以使用 -v 选项实现功能:

```shell
b=1
cat f           # 输出: apple
awk -v var=$b '{print var, $var}' f    # 输出: 1 apple
```

除了使用 -v 选项外,还可以使用 `"'$variable'"` 的方式从 shell 往 awk 传递变量（注意:这里是单引号）:

```shell
awk '{print $b, '$b'}' f    # 输出: apple 1
```

至于有没有办法把 awk 中的变量传给 shell 呢,这个问题我是这样理解的。shell 调用 awk 实际上是 fork 一个子进程出来,而子进程是无法向父进程传递变量的,除非用重定向（包括管道）:

```shell
a=$(awk '{print $b, '$b'}' f)
echo $a         # 输出: apple 1
```

### 3.8 getline

getline 为 awk 所提供的输入指令。其语法如下:

```shell
awk 'BEGIN{ "date" | getline d; close("date");print d}'
# Sun Nov 9 20:55:12 CST 2008

awk 'BEGIN{getline name < "/dev/tty"} '

awk 'BEGIN{while(getline < "/etc/passwd" > 0) { lc++ }; print lc }' f
```

只要 getline 的返回值大于 0,即读入一行,循环就会继续。

getline 如果读取成功,返回 1,否则返回 -1,如果遇到 EOF,则返回 0。getline 在读取的同时会设置 NF、NR、FNR 等内置变量。

如果 getline 后没有变量,则默认置于 $0:

```shell
awk 'BEGIN{ while(("ls" | getline) > 0) print}' f
```

（以上 3 个例子来自《UNIX Shells By Example》Fourth Edition, Section 6.26.4）

### 3.9 输出重定向

awk 的输出重定向类似于 shell 的重定向。重定向的目标文件名必须用双引号引用起来。

```shell
awk '$4 >=70 {print $1,$2 > "destfile" }' filename
awk '$4 >=70 {print $1,$2 >> "destfile" }' filename
```

### 3.10 awk 中调用 shell 命令

（1）使用管道

awk 中的管道概念和 shell 的管道类似,都是使用 "|" 符号,在上面 getline 中 `{"date" | getline d;}` 就是使用了管道。如果在 awk 程序中打开了管道,必须先关闭该管道才能打开另一个管道。也就是说一次只能打开一个管道。shell 命令必须被双引号引用起来。"如果打算再次在 awk 程序中使用某个文件或管道进行读写,则可能要先关闭程序,因为其中的管道会保持打开状态直至脚本运行结束。注意,管道一旦被打开,就会保持打开状态直至 awk 退出。因此 END 块中的语句也会收到管道的影响。（可以在 END 的第一行关闭管道）"

awk 中使用管道有两种语法,分别是:

```text
awk output | shell input
shell output | awk input
```

对于 `awk output | shell input` 来说,shell 接收 awk 的输出,并进行处理。需要注意的是,awk 的 output 是先缓存在 pipe 中,等输出完毕后再调用 shell 命令处理,shell 命令只处理一次,而且处理的时机是"awk 程序结束时,或者管道关闭时（需要显式的关闭管道）":

```shell
awk '/west/{count++} {printf "%s %s\t\t%-15s\n", $3,$4,$1 | "sort +1"} END{close "sort +1"; printf "The number of sales pers in the western"; printf "region is " count "." }' datafile
```

printf 函数用于将输出格式化并发送给管道。所有输出集齐后,被一同发送给 sort 命令。必须用与打开时完全相同的命令来关闭管道（sort +1）,否则 END 块中的语句将与前面的输出一起被排序。此处的 sort 命令只执行一次。

在 `shell output | awk input` 中 awk 的 input 只能是 getline 函数。shell 执行的结果缓存于 pipe 中,再传送给 awk 处理,如果有多行数据,awk 的 getline 命令可能调用多次:

```shell
awk 'BEGIN{ while(("ls" | getline d) > 0) print d}' f
```

（2）使用 system 命令

```shell
awk 'BEGIN{system("echo abc")}'
```

需要注意的是 system 中应该使用 shell 命令的对应字符串。awk 直接把 system 中的内容传递给 shell,作为 shell 的命令行。

（3）system 命令中使用 awk 的变量

空格是 awk 中的字符串连接符,如果 system 中需要使用 awk 中的变量可以使用空格分隔,或者说除了 awk 的变量外其他一律用 "" 引用起来。

```shell
awk 'BEGIN{a = 12; system("echo " a) }'
```

还有好多呀,以后再补充:

- awk 的运算符
- next 等函数
- 更多的输入输出（输出到多个文件,关闭文件,输出到命令）

awk 的内置函数:

```text
gsub, index, length, match, printf, split, sprintf, substr,
tolower, toupper, atan, cos, exp, int, log, rand, sin, sqrt,
srand, system
```

## 4. find

### 4.1 命令格式

```shell
find pathname -options [-print -exec -ok ...]
```

### 4.2 命令功能

用于在文件树中查找文件,并作出相应的处理。

### 4.3 命令参数

- `pathname`:find 命令所查找的目录路径。例如用 . 来表示当前目录,用 / 来表示系统根目录。
- `-print`:find 命令将匹配的文件输出到标准输出。
- `-exec`:find 命令对匹配的文件执行该参数所给出的 shell 命令。相应命令的形式为 'command' { } \;,注意 { } 和 \; 之间的空格。
- `-ok`:和 -exec 的作用相同,只不过以一种更为安全的模式来执行该参数所给出的 shell 命令,在执行每一个命令之前,都会给出提示,让用户来确定是否执行。

### 4.4 命令选项

- `-name`:按照文件名查找文件。
- `-perm`:按照文件权限来查找文件。
- `-prune`:使用这一选项可以使 find 命令不在当前指定的目录中查找,如果同时使用 -depth 选项,那么 -prune 将被 find 命令忽略。
- `-user`:按照文件属主来查找文件。
- `-group`:按照文件所属的组来查找文件。
- `-mtime -n +n`:按照文件的更改时间来查找文件,-n 表示文件更改时间距现在 n 天以内,+n 表示文件更改时间距现在 n 天以前。find 命令还有 -atime 和 -ctime 选项,但它们都和 -mtime 选项类似。
- `-nogroup`:查找无有效所属组的文件,即该文件所属的组在 /etc/groups 中不存在。
- `-nouser`:查找无有效属主的文件,即该文件的属主在 /etc/passwd 中不存在。
- `-newer file1 ! file2`:查找更改时间比文件 file1 新但比文件 file2 旧的文件。
- `-type`:查找某一类型的文件,诸如:
  - b —— 块设备文件。
  - d —— 目录。
  - c —— 字符设备文件。
  - p —— 管道文件。
  - l —— 符号链接文件。
  - f —— 普通文件。
- `-size n:[c]`:查找文件长度为 n 块的文件,带有 c 时表示文件长度以字节计。
- `-depth`:在查找文件时,首先查找当前目录中的文件,然后再在其子目录中查找。
- `-fstype`:查找位于某一类型文件系统中的文件,这些文件系统类型通常可以在配置文件 /etc/fstab 中找到,该配置文件中包含了本系统中有关文件系统的信息。
- `-mount`:在查找文件时不跨越文件系统 mount 点。
- `-follow`:如果 find 命令遇到符号链接文件,就跟踪至链接所指向的文件。
- `-cpio`:对匹配的文件使用 cpio 命令,将这些文件备份到磁带设备中。

另外,下面三个（组）选项的区别:

- `-amin n`:查找系统中最后 N 分钟访问的文件
- `-atime n`:查找系统中最后 n*24 小时访问的文件
- `-cmin n`:查找系统中最后 N 分钟被改变文件状态的文件
- `-ctime n`:查找系统中最后 n*24 小时被改变文件状态的文件
- `-mmin n`:查找系统中最后 N 分钟被改变文件数据的文件
- `-mtime n`:查找系统中最后 n*24 小时被改变文件数据的文件

## 5. cut

### 5.1 语法与主要参数

其语法格式为:

```shell
cut [-bn] [file] 或 cut [-c] [file] 或 cut [-df] [file]
```

使用说明:cut 命令从文件的每一行剪切字节、字符和字段并将这些字节、字符和字段写至标准输出。如果不指定 File 参数,cut 命令将读取标准输入。必须指定 -b、-c 或 -f 标志之一。

主要参数:

- `-b`:以字节为单位进行分割。这些字节位置将忽略多字节字符边界,除非也指定了 -n 标志。
- `-c`:以字符为单位进行分割。
- `-d`:自定义分隔符,默认为制表符。
- `-f`:与 -d 一起使用,指定显示哪个区域。
- `-n`:取消分割多字节字符。仅和 -b 标志一起使用。如果字符的最后一个字节落在由 -b 标志的 List 参数指示的范围之内,该字符将被写出;否则,该字符将被排除。

### 5.2 三种定位方法

cut 命令主要是接受三个定位方法:

1. 字节（bytes）,用选项 -b
2. 字符（characters）,用选项 -c
3. 域（fields）,用选项 -f

### 5.3 以"字节"定位

举个例子吧,当你执行 who 命令时,会输出类似如下的内容:

```shell
who
```

```text
rocrocket :0           2009-01-08 11:07
rocrocket pts/0        2009-01-08 11:23 (:0.0)
rocrocket pts/1        2009-01-08 14:15 (:0.0)
```

如果我们想提取每一行的第 3 个字节,就这样:

```shell
who | cut -b 3
```

```text
c
c
c
```

如果"字节"定位中,想提取第 3、第 4、第 5 和第 8 个字节,怎么办?-b 支持形如 3-5 的写法,而且多个定位之间用逗号隔开就成了。看看例子吧:

```shell
who | cut -b 3-5,8
```

```text
croe
croe
croe
```

但有一点要注意,cut 命令如果使用了 -b 选项,那么执行此命令时,cut 会先把 -b 后面所有的定位进行从小到大排序,然后再提取。可不能颠倒定位的顺序哦。这个例子就可以说明这个问题:

```shell
who | cut -b 8,3-5
```

```text
croe
croe
croe
```

### 5.4 "3-5"之类的小技巧

```shell
who | cut -b -3
```

```text
roc
roc
roc
```

```shell
who | cut -b 3-
```

```text
crocket :0           2009-01-08 11:07
crocket pts/0        2009-01-08 11:23 (:0.0)
crocket pts/1        2009-01-08 14:15 (:0.0)
```

想必你也看到了,-3 表示从第一个字节到第三个字节,而 3- 表示从第三个字节到行尾。如果你细心,你可以看到这两种情况下,都包括了第三个字节"c"。

如果我执行 `who|cut -b -3,3-`,你觉得会如何呢?答案是输出整行,不会出现连续两个重叠的 c 的。看:

```shell
who | cut -b -3,3-
```

```text
rocrocket :0           2009-01-08 11:07
rocrocket pts/0        2009-01-08 11:23 (:0.0)
rocrocket pts/1        2009-01-08 14:15 (:0.0)
```

### 5.5 以"字符"为定位标志

下面例子你似曾相识,提取第 3、第 4、第 5 和第 8 个字符:

```shell
who | cut -c 3-5,8
```

```text
croe
croe
croe
```

不过,看着怎么和 -b 没有什么区别啊?莫非 -b 和 -c 作用一样?其实不然,看似相同,只是因为这个例子举的不好,who 输出的都是单字节字符,所以用 -b 和 -c 没有区别,如果你提取中文,区别就看出来了,来,看看中文提取的情况:

```shell
cat cut_ch.txt
```

```text
星期一
星期二
星期三
星期四
```

```shell
cut -b 3 cut_ch.txt     # 无输出(乱码,下同)
cut -c 3 cut_ch.txt
```

```text
一
二
三
四
```

看到了吧,用 -c 则会以字符为单位,输出正常;而 -b 只会傻傻的以字节（8 位二进制位）来计算,输出就是乱码。

既然提到了这个知识点,就再补充一句,如果你学有余力,就提高一下。当遇到多字节字符时,可以使用 -n 选项,-n 用于告诉 cut 不要将多字节字符拆开。例子如下:

```shell
cat cut_ch.txt | cut -b 2          # 无输出
cat cut_ch.txt | cut -nb 2         # 无输出
cat cut_ch.txt | cut -nb 1,2,3
```

```text
星
星
星
星
```

### 5.6 域的提取

为什么会有"域"的提取呢?因为刚才提到的 -b 和 -c 只能在固定格式的文档中提取信息,而对于非固定格式的信息则束手无策。这时候"域"就派上用场了。如果你观察过 /etc/passwd 文件,你会发现,它并不像 who 的输出信息那样具有固定格式,而是比较零散的排放。但是,冒号在这个文件的每一行中都起到了非常重要的作用,冒号用来隔开每一个项。

我们很幸运,cut 命令提供了这样的提取方式,具体的说就是设置"间隔符",再设置"提取第几个域",就 OK 了!

以 /etc/passwd 的前五行内容为例:

```shell
cat /etc/passwd | head -n 5
```

```text
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
```

```shell
cat /etc/passwd | head -n 5 | cut -d : -f 1
```

```text
root
bin
daemon
adm
lp
```

看到了吧,用 -d 来设置间隔符为冒号,然后用 -f 来设置我要取的是第一个域,再按回车,所有的用户名就都列出来了!呵呵,有成就感吧!

当然,在设定 -f 时,也可以使用例如 3-5 或者 4- 类似的格式:

```shell
cat /etc/passwd | head -n 5 | cut -d : -f 1,3-5
```

```text
root:0:0:root
bin:1:1:bin
daemon:2:2:daemon
adm:3:4:adm
lp:4:7:lp
```

```shell
cat /etc/passwd | head -n 5 | cut -d : -f 1,3-5,7
```

```text
root:0:0:root:/bin/bash
bin:1:1:bin:/sbin/nologin
daemon:2:2:daemon:/sbin/nologin
adm:3:4:adm:/sbin/nologin
lp:4:7:lp:/sbin/nologin
```

```shell
cat /etc/passwd | head -n 5 | cut -d : -f -2
```

```text
root:x
bin:x
daemon:x
adm:x
lp:x
```

### 5.7 空格和制表符的分辨

有时候制表符确实很难辨认,有一个方法可以看出一段空格到底是由若干个空格组成的还是由一个制表符组成的。

```shell
cat tab_space.txt
```

```text
this is tab finish.
this is several space      finish.
```

```shell
sed -n l tab_space.txt
```

```text
this is tab\tfinish.$
this is several space      finish.$
```

看到了吧,如果是制表符（TAB）,那么会显示为 \t 符号,如果是空格,就会原样显示。通过此方法即可以判断制表符和空格了。

注意,上面 sed -n 后面的字符是 L 的小写字母哦,不要看错。

### 5.8 cut -d 中如何设定制表符或空格

其实 cut 的 -d 选项的默认间隔符就是制表符,所以当你就是要使用制表符的时候,完全就可以省略 -d 选项,而直接用 -f 来取域就可以了。

如果你设定一个空格为间隔符,那么就这样:

```shell
cat tab_space.txt | cut -d ' ' -f 1
```

```text
this
this
```

注意,两个单引号之间可确实要有一个空格哦,不能偷懒。而且,你只能在 -d 后面设置一个空格,可不许设置多个空格,因为 cut 只允许间隔符是一个字符:

```shell
cat tab_space.txt | cut -d '  ' -f 1
```

```text
cut: the delimiter must be a single character
Try `cut --help' for more information.
```

### 5.9 cut 有哪些缺陷和不足

猜出来了吧?对,就是在处理多空格时。

如果文件里面的某些域是由若干个空格来间隔的,那么用 cut 就有点麻烦了,因为 cut 只擅长处理"以一个字符间隔"的文本内容。
