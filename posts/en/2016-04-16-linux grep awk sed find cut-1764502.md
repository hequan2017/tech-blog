---
title: "Linux Text Processing: grep, awk, sed, find, cut"
date: "2016-04-16 16:12:06"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764502"
lang: "en"
---
> **About this post**
>
> Quick-reference notes on the five text-processing tools: grep's basic regular
> expressions (^ $ . * [] \? \{m,n\} \< \> \(\) grouping, etc.) together with
> options such as -v/-o/-i/-A/-B/-C/-E; sed's -n/-e/-f/-r/-i options and its
> a/c/d/i/p/s commands; awk in depth — syntax structure, BEGIN/END, the -F/-v
> parameters, the NR/FNR/FS/OFS/NF/RS/ORS built-in variables, associative and
> multidimensional arrays, reading shell variables, getline, output redirection,
> pipes, and calling shell commands via system; find by name/permissions/owner/
> type/size/time (-amin/-atime/-cmin/-ctime/-mmin/-mtime) plus -exec/-ok;
> and cut's three positioning methods — by byte (-b), character (-c), and
> field (-d/-f) — with detailed examples and their shortcomings.

> **Technical notes**
>
> The material comes from classic tutorials of around 2009 (Vbird's Linux
> Private Kitchen, "UNIX Shells By Example", etc.); the commands themselves are
> still in use today. Three updates: modern distributions now configure a
> `--color=auto` alias for grep by default; the remark that "awk iterates arrays
> in the same order as python dicts" was based on pre-3.6 Python — Python 3.7+
> dicts guarantee insertion-order iteration; and `sort +1` in the examples is
> old-style syntax — with GNU sort it should be written as `sort -k2`.

---

## 1. grep

### 1.1 Basic Regular Expressions

- `^`: anchors the matching content at the start of a line; usage: "^pattern";
- `$`: anchors the matching content at the end of a line; usage: "pattern$";
- `.`: matches any single character;
- `*`: matches the character immediately before it any number of times;
  - `a*b`: ab, aab, acb, b
- `.*`: matches any characters of any length;
- `[]`: matches any single character within the specified range;
- `[^]`: matches any single character outside the specified range;
- `\?`: matches the character immediately before it 0 or 1 times;
- `\{m,n\}`: matches the preceding character at least m times and at most n times;
- `\{0,n\}`: at most n times; 0 to n times;
- `\{m,\}`: at least m times;
- `\{m\}`: exactly m times;
- `\<`: anchors the start of a word; usage: \<pattern
- `\>`: anchors the end of a word; usage: pattern\>
- `\(\)`: grouping; usage: \(pattern\)

### 1.2 grep Options

- `--color=auto`: automatically color the matched characters

```shell
export GREP_COLOR='01;36'
```

- `-r`: recursive search; same usage as `-d recurse` (recursive)
- `-v`: invert the match; show only lines that do not match the pattern;
- `-o`: show only the part of the line matched by the pattern, not the whole line;
- `-i`: case-insensitive;
- `-A #`: when showing matched lines, also show the # lines after them;
- `-B #`: the preceding # lines;
- `-C #`: the # lines before and after;
- `-E`: use extended regular expressions

## 2. sed

The sed command-line format is:

```shell
sed [-nefri] 'command' input-text
```

Commonly used options:

- `-n`: use quiet (silent) mode. In ordinary sed usage, everything coming from STDIN is normally printed to the screen. But with the -n option added, only the line (or action) that sed specially processes is printed.
- `-e`: perform the sed action editing directly on the command line;
- `-f`: write the sed actions directly into a file; with -f filename, the sed actions inside filename are executed;
- `-r`: the sed actions support extended regular expression syntax. (The default is basic regular expression syntax.)
- `-i`: directly modify the contents of the file being read, instead of outputting to the screen.

Commonly used commands (actions):

- `a`: append; a string can follow a, and it appears on a new line (the line after the current one);
- `c`: replace; a string can follow c, and it replaces the lines between n1 and n2;
- `d`: delete; since it is a deletion, d is usually not followed by anything;
- `i`: insert; a string can follow i, and it appears on a new line (the line above the current one);
- `p`: print, i.e. print out the selected data. p usually works together with the sed -n option;
- `s`: substitute; it performs the replacement directly! This s action can usually be combined with regular expressions! For example, 1,20s/old/new/g is exactly that!

## 3. awk

### 3.1 Introduction and an Appetizer Example

awk is truly excellent: it runs efficiently, the code is simple, and its ability to process formatted text is extremely strong. Basically, awk can do everything grep and sed can do — and do it better.

Let's start with a very satisfying example: given file a, compute the average of the floating-point numbers on the lines whose first column is a float. With awk, one line of code does it (of course, python can also do this easily, but you would have to create a new file no matter what; and don't even dream of doing it in the bash shell — those are floating-point numbers!!!)

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

### 3.2 Syntax

```shell
awk [-F re] [parameter...] ['program'] [-f 'programfile'] [in_file_list]
```

The BEGIN and END structures in awk: the statements inside BEGIN and END take effect before the file (in_file) starts being read and after the file has been fully read, respectively — think of them as initialization and wrap-up.

The if..else, while, do..while, for, break, continue, and printf syntax in awk matches the C language. awk also supports decision statements like `if (key in array)` (where array is an array — very much like python's syntax), and it supports `for (key in array)` to iterate over arrays (also very much like python).

### 3.3 Common Parameters

- `-F re`: allows awk to change its field separator
- `-v var=val`: assigns the value val to var (a great way to communicate variables~ I only learned about this option today — thinking of the code I wrote before makes me want to tear my hair out~). If several variables need values, write multiple -v options, one -v per assignment

For example, to print the lines from line num through line num+num1 of file a:

```shell
awk -v num=$num -v num1=$num1 'NR==num,NR==num+num1{print}' a
```

- `-f progfile`: allows awk to call and execute the program file progfile; of course, progfile must be a program file that conforms to awk syntax

### 3.4 Common Built-in Variables

- **ARGC**: the number of command-line arguments
- **ARGV**: the array of command-line arguments
- **ARGIND**: the ARGV index of the file currently being processed

For example, with two files a and b:

```shell
awk '{if(ARGIND==1){print "processing file a"} if(ARGIND==2){print "processing file b"}}' a b
```

Files are processed in order: file a is scanned completely first, then file b.

- **NR**: the number of records read so far
- **FNR**: the number of records in the current file

The example above can also be written as:

```shell
awk 'NR==FNR{print "processing file a"} NR > FNR{print "processing file b"}' a b
```

With the input files a and b: since a is scanned first, NR==FNR necessarily holds while scanning a; then when scanning b, FNR starts counting from 1 while NR continues from where a's line count left off, so NR > FNR.

For example, to display lines 10 through 15 of a file:

```shell
awk 'NR==10,NR==15{print}' a
```

- **FS**: the input field separator (defaults to space), equivalent to the -F option

```shell
awk -F ':' '{print}' a
awk 'BEGIN{FS=":"}{print}' a    # the two are the same
```

- **OFS**: the output field separator (defaults to space)

```shell
awk -F ':' 'BEGIN{OFS=";"}{print $1,$2,$3}' b
```

If cat b gives:

```text
1:2:3
4:5:6
```

then after setting OFS to ";" the output is:

```text
1;2;3
4;5;6
```

(A small note: awk refers to the first, second, third... fields after splitting as $1,$2,$3..., and $0 is the entire record (usually a whole line).)

- **NF**: the number of fields in the current record

```shell
awk -F ':' '{print NF}' b
```

The output is:

```text
3
3
```

showing that each line of b has 3 fields after being split on the ":" separator.

You can use NF to keep only lines whose field count meets the requirement, which filters out some malformed lines:

```shell
awk -F ':' '{if (NF == 3) print}' b
```

- **RS**: the input record separator, default "\n"

By default, awk treats one line as one record; if RS is set, awk splits records according to RS.

For example, file c — cat c gives:

```text
hello world; I want to go swimming tomorrow;hiahia
```

Running `awk 'BEGIN{ RS = ";" } {print}' c` gives:

```text
hello world
I want to go swimming tomorrow
hiahia
```

Using RS and FS wisely lets awk handle more document patterns — for example, processing multiple lines at once. For instance, document d; cat d outputs (records separated by blank lines, fields separated by newlines):

```text
1 2
3 4 5

6 7
8 9 10
11 12

hello
```

The awk for this is also easy to write:

```shell
awk 'BEGIN{ FS = "\n"; RS = ""} {print NF}' d
```

Output:

```text
2
3
1
```

- **ORS**: the output record separator, default a newline; it controls the output symbol after each print statement

```shell
awk 'BEGIN{ FS = "\n"; RS = ""; ORS = ";"} {print NF}' d
```

Output:

```text
2;3;1
```

### 3.5 awk Arrays

awk's arrays deserve a good discussion. Behaviorally, awk arrays are more like associative arrays — or call them maps, dictionaries, or hashes. awk arrays accept string subscripts and support very fast `in` lookups.

File e consists of lowercase letters; cat e outputs:

```text
a
b
z
...
```

To count how many times each distinct letter appears, you can use an array:

```shell
awk '{arr[$0]++} END{ for (key in arr) print key, "-->",arr[key] }' e
```

When you iterate over the array with `for(key in arr)`, the output order is unpredictable — the same is true of python's dict iteration.

In gawk, the asort built-in function can sort an array; no similar sorting function has been found in other awk versions. A workaround is to finish with awk first and then pipe the output to sort. sort's -k option lets you control which column to sort by.

### 3.6 awk's Multidimensional Arrays

awk's multidimensional arrays are essentially one-dimensional arrays; more precisely, awk does not support multidimensional arrays at the storage level. Instead, awk provides a way to logically emulate two-dimensional array access. For example, an access like `array[2,4] = 1` is allowed. awk uses a special string SUBSEP (\034) as the field separator; in the example above, the key actually stored in the associative array is 2\0344.

Like membership tests on one-dimensional arrays, multidimensional arrays can use syntax like `if ( (i,j) in array)`, but the subscripts must be placed in parentheses.

Like iteration over one-dimensional arrays, multidimensional arrays are traversed with syntax like `for ( item in array )`. Unlike one-dimensional arrays, multidimensional arrays must use the split() function to access the individual subscript components: `split ( item, subscr, SUBSEP)`.

### 3.7 Reading Shell Variables in awk

This can be done with the -v option:

```shell
b=1
cat f           # output: apple
awk -v var=$b '{print var, $var}' f    # output: 1 apple
```

Besides the -v option, you can also pass variables from the shell into awk using the `"'$variable'"` form (note: single quotes here):

```shell
awk '{print $b, '$b'}' f    # output: apple 1
```

As for whether there is a way to pass an awk variable back to the shell, here is how I understand the question: when the shell calls awk, it actually forks a child process, and a child process cannot pass variables back to its parent — except through redirection (including pipes):

```shell
a=$(awk '{print $b, '$b'}' f)
echo $a         # output: apple 1
```

### 3.8 getline

getline is an input facility provided by awk. Its syntax is as follows:

```shell
awk 'BEGIN{ "date" | getline d; close("date");print d}'
# Sun Nov 9 20:55:12 CST 2008

awk 'BEGIN{getline name < "/dev/tty"} '

awk 'BEGIN{while(getline < "/etc/passwd" > 0) { lc++ }; print lc }' f
```

As long as getline returns a value greater than 0 — meaning a line was read — the loop keeps going.

getline returns 1 on a successful read, -1 otherwise, and 0 at EOF. While reading, getline also sets built-in variables such as NF, NR, and FNR.

If no variable follows getline, the line is placed in $0 by default:

```shell
awk 'BEGIN{ while(("ls" | getline) > 0) print}' f
```

(The three examples above come from "UNIX Shells By Example", Fourth Edition, Section 6.26.4.)

### 3.9 Output Redirection

awk's output redirection is similar to the shell's. The target file name of the redirection must be enclosed in double quotes.

```shell
awk '$4 >=70 {print $1,$2 > "destfile" }' filename
awk '$4 >=70 {print $1,$2 >> "destfile" }' filename
```

### 3.10 Calling Shell Commands from awk

(1) Using pipes

The concept of a pipe in awk is similar to that of the shell — both use the "|" symbol; in the getline section above, `{"date" | getline d;}` used a pipe. If a pipe is opened in an awk program, it must be closed before another pipe can be opened; in other words, only one pipe can be open at a time. The shell command must be enclosed in double quotes. "If you intend to read or write a file or pipe again in an awk program, you may have to close it first, because the pipe stays open until the script finishes. Note that once a pipe is opened, it stays open until awk exits. Therefore, statements in the END block are also affected by the pipe. (You can close the pipe on the first line of the END block.)"

There are two syntaxes for using pipes in awk:

```text
awk output | shell input
shell output | awk input
```

For `awk output | shell input`, the shell receives awk's output and processes it. Note that awk's output is first buffered in the pipe, and the shell command is invoked to process it only after the output is complete. The shell command runs only once, and the timing is "when the awk program ends, or when the pipe is closed (the pipe must be closed explicitly)":

```shell
awk '/west/{count++} {printf "%s %s\t\t%-15s\n", $3,$4,$1 | "sort +1"} END{close "sort +1"; printf "The number of sales pers in the western"; printf "region is " count "." }' datafile
```

The printf function formats the output and sends it to the pipe. Once all the output has been collected, it is sent to the sort command in one batch. The pipe must be closed with exactly the same command used to open it (sort +1); otherwise, the statements in the END block will be sorted together with the preceding output. The sort command here executes only once.

In `shell output | awk input`, awk's input can only be the getline function. The shell's results are buffered in the pipe and then passed to awk for processing; if there are multiple lines of data, awk's getline command may be invoked multiple times:

```shell
awk 'BEGIN{ while(("ls" | getline d) > 0) print d}' f
```

(2) Using the system command

```shell
awk 'BEGIN{system("echo abc")}'
```

Note that system should be given the string corresponding to the shell command. awk passes the content of system directly to the shell as a shell command line.

(3) Using awk variables inside the system command

A space is awk's string-concatenation operator. If you need to use an awk variable inside system, separate it with spaces — or put another way, quote everything except the awk variables with "":

```shell
awk 'BEGIN{a = 12; system("echo " a) }'
```

There is much more — to be added later:

- awk's operators
- functions such as next
- more on input/output (writing to multiple files, closing files, sending output to a command)

awk's built-in functions:

```text
gsub, index, length, match, printf, split, sprintf, substr,
tolower, toupper, atan, cos, exp, int, log, rand, sin, sqrt,
srand, system
```

## 4. find

### 4.1 Command Format

```shell
find pathname -options [-print -exec -ok ...]
```

### 4.2 Command Function

Searches a file tree for files and performs the corresponding processing.

### 4.3 Command Parameters

- `pathname`: the directory path for find to search. For example, . means the current directory and / means the system root.
- `-print`: the find command sends the matching files to standard output.
- `-exec`: the find command executes the shell command given with this parameter on the matching files. The corresponding command takes the form 'command' { } \; — note the space between { } and \;.
- `-ok`: works the same as -exec, except that the shell command given with this parameter is executed in a safer mode: before running each command it prompts, letting the user decide whether to execute it.

### 4.4 Command Options

- `-name`: search for files by file name.
- `-perm`: search for files by file permissions.
- `-prune`: this option makes find skip the currently specified directory; if the -depth option is used at the same time, -prune is ignored by find.
- `-user`: search for files by owner.
- `-group`: search for files by the group a file belongs to.
- `-mtime -n +n`: search for files by modification time; -n means the file was modified within the last n days, +n means the file was modified more than n days ago. The find command also has the -atime and -ctime options, both similar to -mtime.
- `-nogroup`: search for files with no valid group, i.e. the file's group does not exist in /etc/groups.
- `-nouser`: search for files with no valid owner, i.e. the file's owner does not exist in /etc/passwd.
- `-newer file1 ! file2`: search for files modified more recently than file1 but earlier than file2.
- `-type`: search for files of a particular type, such as:
  - b — block device files.
  - d — directories.
  - c — character device files.
  - p — pipe files.
  - l — symbolic link files.
  - f — regular files.
- `-size n:[c]`: search for files of n blocks in length; with c, the file length is measured in bytes.
- `-depth`: when searching, examine the files in the current directory first, then look in its subdirectories.
- `-fstype`: search for files on a particular type of file system; these file system types can usually be found in the configuration file /etc/fstab, which contains the file system information for this system.
- `-mount`: do not cross file system mount points while searching for files.
- `-follow`: if find encounters a symbolic link, follow it to the file the link points to.
- `-cpio`: use the cpio command on the matching files to back them up to a tape device.

In addition, the differences among the following three (groups of) options:

- `-amin n`: find files in the system accessed within the last N minutes
- `-atime n`: find files in the system accessed within the last n*24 hours
- `-cmin n`: find files in the system whose file status was changed within the last N minutes
- `-ctime n`: find files in the system whose file status was changed within the last n*24 hours
- `-mmin n`: find files in the system whose file data was changed within the last N minutes
- `-mtime n`: find files in the system whose file data was changed within the last n*24 hours

## 5. cut

### 5.1 Syntax and Main Parameters

Its syntax format is:

```shell
cut [-bn] [file] or cut [-c] [file] or cut [-df] [file]
```

Usage notes: the cut command cuts bytes, characters, and fields from each line of a file and writes those bytes, characters, and fields to standard output. If the File parameter is not specified, cut reads from standard input. One of the -b, -c, or -f flags must be specified.

Main parameters:

- `-b`: split by bytes. These byte positions ignore multi-byte character boundaries unless the -n flag is also specified.
- `-c`: split by characters.
- `-d`: custom delimiter; the default is the tab character.
- `-f`: used together with -d to specify which field to display.
- `-n`: do not split multi-byte characters. Used only with the -b flag. If the last byte of a character falls within the range indicated by the List parameter of the -b flag, the character is written out; otherwise, it is excluded.

### 5.2 Three Positioning Methods

The cut command mainly accepts three positioning methods:

1. bytes, with the option -b
2. characters, with the option -c
3. fields, with the option -f

### 5.3 Positioning by "Byte"

For example, when you run the who command, it prints something like the following:

```shell
who
```

```text
rocrocket :0           2009-01-08 11:07
rocrocket pts/0        2009-01-08 11:23 (:0.0)
rocrocket pts/1        2009-01-08 14:15 (:0.0)
```

If we want to extract the 3rd byte of each line, we do this:

```shell
who | cut -b 3
```

```text
c
c
c
```

What if, in "byte" positioning, you want to extract the 3rd, 4th, 5th, and 8th bytes? -b supports ranges like 3-5, and multiple positions are simply separated by commas. Look at the example:

```shell
who | cut -b 3-5,8
```

```text
croe
croe
croe
```

But one thing to note: if cut uses the -b option, it first sorts all the positions after -b in ascending order before extracting. You cannot rely on reversing the order of the positions. This example illustrates the point:

```shell
who | cut -b 8,3-5
```

```text
croe
croe
croe
```

### 5.4 Little Tricks Like "3-5"

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

As you have surely noticed, -3 means from the first byte through the third byte, while 3- means from the third byte to the end of the line. If you look carefully, you can see that in both cases the third byte "c" is included.

If I run `who|cut -b -3,3-`, what do you think happens? The answer is that the whole line is printed — there are no two overlapping c's in a row. Look:

```shell
who | cut -b -3,3-
```

```text
rocrocket :0           2009-01-08 11:07
rocrocket pts/0        2009-01-08 11:23 (:0.0)
rocrocket pts/1        2009-01-08 14:15 (:0.0)
```

### 5.5 Positioning by "Character"

The following example looks familiar — extracting the 3rd, 4th, 5th, and 8th characters:

```shell
who | cut -c 3-5,8
```

```text
croe
croe
croe
```

But how is this any different from -b? Could -b and -c do the same thing? Not really — they only look the same because this example is poorly chosen: who's output is entirely single-byte characters, so there is no difference between -b and -c here. If you extract Chinese text, the difference shows up. Come and see how Chinese extraction goes:

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
cut -b 3 cut_ch.txt     # no output (garbled, same below)
cut -c 3 cut_ch.txt
```

```text
一
二
三
四
```

See? With -c the extraction is per character and the output is correct, while -b just dumbly counts bytes (8-bit units) and the output is garbled.

Since this point has come up, one more remark — a step up if you have the bandwidth. When multi-byte characters are involved, you can use the -n option; -n tells cut not to split multi-byte characters. Example:

```shell
cat cut_ch.txt | cut -b 2          # no output
cat cut_ch.txt | cut -nb 2         # no output
cat cut_ch.txt | cut -nb 1,2,3
```

```text
星
星
星
星
```

### 5.6 Extracting Fields

Why is there field extraction at all? Because the -b and -c options mentioned above can only extract information from documents with a fixed format, and they are helpless against non-fixed-format information. That is where "fields" come in handy. If you have ever looked at the /etc/passwd file, you will have noticed that, unlike who's output, it does not have a fixed layout — its items are rather scattered. But the colon plays a vital role on every line of this file: it separates each item.

We are in luck: the cut command provides exactly this way of extracting. To be specific, you set the "delimiter" and then set "which field to extract" — and that is it!

Take the first five lines of /etc/passwd as an example:

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

See? Use -d to set the delimiter to a colon, then use -f to say I want the first field, hit Enter, and all the user names are listed! Quite satisfying, isn't it!

Of course, when setting -f you can also use formats like 3-5 or 4-:

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

### 5.7 Telling Spaces and Tabs Apart

Sometimes a tab really is hard to make out. There is a way to see whether a stretch of whitespace consists of several spaces or of a single tab.

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

See? If it is a tab (TAB), it shows up as the \t symbol; if it is a space, it is displayed as-is. This method lets you tell tabs and spaces apart.

Note: the character after sed -n above is the lowercase letter L — do not misread it.

### 5.8 Specifying a Tab or Space in cut -d

In fact, cut's -d option defaults to the tab as its delimiter, so when a tab is exactly what you want, you can simply omit -d and take fields directly with -f.

If you want to set a space as the delimiter, do this:

```shell
cat tab_space.txt | cut -d ' ' -f 1
```

```text
this
this
```

Note that there really must be one space between the two single quotes — no slacking off. Moreover, you may put only one space after -d; multiple spaces are not allowed, because cut only permits a delimiter of one character:

```shell
cat tab_space.txt | cut -d '  ' -f 1
```

```text
cut: the delimiter must be a single character
Try `cut --help' for more information.
```

### 5.9 cut's Shortcomings and Limitations

You guessed it: handling runs of multiple spaces.

If some fields in a file are separated by several spaces, cut becomes a bit of a hassle, because cut is only good at handling text "separated by a single character".
