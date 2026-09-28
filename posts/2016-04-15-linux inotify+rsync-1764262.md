---
title: "linux  inotify+rsync"
date: "2016-04-15 17:56:10"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764262"
---
> **内容介绍**
>
> 本文完整演示 CentOS 6.5 下 inotify+rsync 实时同步方案的部署:在目的服务器
> （rsync 服务端）检查/安装 rsync、编写 /etc/rsyncd.conf 并逐条解释 uid、
> max connections、log format 各字段、模块参数、auth users、secrets file、
> hosts allow 等,建立认证密码文件、motd 并启动 daemon;在更新源服务器
> （客户端）列出 inotify 可监控的事件、源码安装 inotify-tools、编写
> inotifywait 监控脚本实现事件触发的自动推送,最后做同步测试,并附 inotify 与
> rsync 参数速查表。

> **技术备注**
>
> CentOS 6 已于 2020 年 11 月停止维护（EOL）,生产环境建议迁移至 Rocky Linux /
> AlmaLinux / Ubuntu LTS。新发行版上 rsync daemon 建议由 systemd 管理,而非文中
> 的 /etc/rc.local 方式;hosts allow 支持 192.168.10.0/24 与
> 192.168.10.0/255.255.255.0 两种写法,效果相同。

---

## 1. 系统环境

- 系统:centos 6.5_64
- 更新源服务器:192.168.10.11
- 目的服务器:192.168.10.10

## 2. 目的服务器配置（rsync 服务端:192.168.10.10）

### 2.1 检查 rsync 是否安装

```shell
rpm -qa | grep rsync
```

如果没有安装,执行以下命令进行安装:

```shell
yum -y install rsync
```

### 2.2 定义 rsync 配置文件 /etc/rsyncd.conf

在目的服务器 192.168.10.10 上执行:

```shell
cat >> /etc/rsyncd.conf << EOF
uid = rsync
gid = rsync
use chroot = no
max connections = 100
timeout = 600
pid file = /var/run/rsyncd.pid
lock file = /var/run/rsync.lock
log file = /var/log/rsyncd.log

[hequan]
path = /hequan/
ignore errors
read only = no
list = no
hosts allow = 192.168.10.0/255.255.255.0
auth users = hequan
secrets file = /etc/hequan.pwd
EOF
```

### 2.3 rsyncd.conf 配置文件详解

全局参数:

- `uid = rsync` —— 运行 RSYNC 守护进程的用户
- `gid = rsync` —— 运行 RSYNC 守护进程的组
- `use chroot = 0` —— 不使用 chroot
- `max connections = 0` —— 最大连接数,0 为不限制
- `port = 873` —— 默认端口 873

下面这些文件是安装完 RSYNC 服务后自动生成的文件:

- `pid file = /var/run/rsyncd.pid` —— pid 文件的存放位置
- `lock file = /var/run/rsync.lock` —— 锁文件的存放位置。指定支持 max connections 参数的锁文件,默认值是 /var/run/rsyncd.lock。
- `log file = /var/log/rsyncd.log` —— 日志记录文件的存放位置

`Timeout = 300`:通过该选项可以覆盖客户指定的 IP 超时时间。通过该选项可以确保 rsync 服务器不会永远等待一个崩溃的客户端。超时单位为秒钟,0 表示没有超时定义,这也是默认值。对于匿名 rsync 服务器来说,一个理想的数字是 600。

`Log format = %t %a %m %f %b`:通过该选项用户在使用 transfer logging 时可以自己定制日志文件的字段。其格式是一个包含格式定义符的字符串,可以使用的格式定义符如下所示:

- `%h` 远程主机名
- `%a` 远程 IP 地址
- `%l` 文件长度字符数
- `%p` 该次 rsync 会话的进程 id
- `%o` 操作类型:" send" 或 " recv"
- `%f` 文件名
- `%P` 模块路径
- `%m` 模块名
- `%t` 当前时间
- `%u` 认证的用户名（匿名时是 null）
- `%b` 实际传输的字节数
- `%c` 当发送文件时,该字段记录该文件的校验码

默认 log 格式为:" %o %h [%a] %m (%u) %f %l",一般来说,在每行的头上会添加 " %t [%p] "。在源代码中同时发布有一个叫 rsyncstats 的 perl 脚本程序来统计这种格式的日志文件。

- `#transfer logging = yes` —— 使 rsync 服务器使用 ftp 格式的文件来记录下载和上载操作在自己单独的日志中
- `syslog facility = local3` —— 指定 rsync 发送日志消息给 syslog 时的消息级别。常见的消息级别是:auth, authpriv, cron, daemon, ftp, kern, lpr, mail, news, security, sys-log, user, uucp, local0, local1, local2, local3, local4, local5, local6 和 local7。默认值是 daemon。

模块参数:

- `[hequan]` —— 这里是认证的模块名,在 client 端需要指定
- `path = /data/` —— 需要做镜像的目录,不可缺少!
- `comment = backup web` —— 这个模块的注释信息
- `ignore errors` —— 可以忽略一些无关的 IO 错误
- `read only = yes` —— 该选项设定是否允许客户上载文件。如果为 true 那么任何上载请求都会失败,如果为 false 并且服务器目录读写权限允许那么上载是允许的。默认值为 true。
- `list = no` —— 不允许列文件
- `auth users = bak` —— 认证的用户名,如果没有这行则表明是匿名,此用户与系统无关

  该选项指定由空格或逗号分隔的用户名列表,只有这些用户才允许连接该模块。这里的用户和系统用户没有任何关系。如果 " auth users" 被设置,那么客户端发出对该模块的连接请求以后会被 rsync 请求 challenged 进行验证身份,这里使用的 challenge/response 认证协议。用户的名和密码以明文方式存放在 " secrets file" 选项指定的文件中。默认情况下无需密码就可以连接模块（也就是匿名方式）。

- `secrets file = /etc/rsync.pwd` —— 密码和用户名对比表,密码文件自己生成

  该选项指定一个包含定义用户名:密码对的文件。只有在 " auth users" 被定义时,该文件才有作用。文件每行包含一个 username:passwd 对。一般来说密码最好不要超过 8 个字符。没有默认的 secrets file 名,需要显式指定一个（例如:/etc/www1.pwd）。注意:该文件的权限一定要是 600,否则客户端将不能连接服务器。

- `hosts allow = 192.168.10.0/255.255.255.0` —— 允许主机或网段

  该选项指定哪些 IP 的客户允许连接该模块。客户模式定义可以是以下形式:

  - 单个 IP 地址,例如:192.168.10.11
  - 整个网段,例如:192.168.10.0/24,也可以是 192.168.10.0/255.255.255.0
  - 多个 IP 或网段需要用空格隔开,"*" 则表示所有,默认是允许所有主机连接

- `hosts deny = 0.0.0.0/0` —— 禁止主机

### 2.4 建立认证文件并授权

建立认证文件 /etc/hequan.pwd,此文件须与配置文件中指定的文件名保持一致。
此处格式为 username:password。出于安全问题,并不建议实际使用中使用 root 用户。

在目的服务器 192.168.10.10 上:

```shell
echo "hequan:123456" >> /etc/hequan.pwd
chmod 600 /etc/hequan.pwd
chmod 600 /etc/rsyncd.conf
```

创建用户并授权:

```shell
useradd rsync -s /sbin/nologin
chown -R rsync.rsync /hequan/
```

### 2.5 建立 motd 文件（可有可无）

rsyncd.motd 记录了 rsync 服务的欢迎信息,你可以在其中输入任何文本信息,如:

```shell
echo "Welcome to use the rsync services!" >> /var/rsyncd.motd
```

### 2.6 启动 rsync

```shell
/usr/bin/rsync --daemon
echo "/usr/bin/rsync --daemon" >> /etc/rc.local
```

## 3. 更新源服务器配置（rsync 客户端:192.168.10.11）

### 3.1 inotify 可以监视的文件系统事件

- `IN_ACCESS`,即文件被访问
- `IN_MODIFY`,文件被 write
- `IN_ATTRIB`,文件属性被修改,如 chmod、chown、touch 等
- `IN_CLOSE_WRITE`,可写文件被 close
- `IN_CLOSE_NOWRITE`,不可写文件被 close
- `IN_OPEN`,文件被 open
- `IN_MOVED_FROM`,文件被移走,如 mv
- `IN_MOVED_TO`,文件被移来,如 mv、cp
- `IN_CREATE`,创建新文件
- `IN_DELETE`,文件被删除,如 rm
- `IN_DELETE_SELF`,自删除,即一个可执行文件在执行时删除自己
- `IN_MOVE_SELF`,自移动,即一个可执行文件在执行时移动自己
- `IN_UNMOUNT`,宿主文件系统被 umount
- `IN_CLOSE`,文件被关闭,等同于（IN_CLOSE_WRITE | IN_CLOSE_NOWRITE）
- `IN_MOVE`,文件被移动,等同于（IN_MOVED_FROM | IN_MOVED_TO）

注:上面所说的文件也包括目录。

### 3.2 安装 inotify-tools

在安装 inotify-tools 前请先确认你的 linux 内核是否达到了 2.6.13,并且在编译时开启了 CONFIG_INOTIFY 选项,也可以通过以下命令检测:

```shell
ls /proc/sys/fs/inotify
```

如果有 max_queued_events、max_user_instances、max_user_watches 三项就说明支持。

编译安装（原文的 wget 下载直链已失效,原为 GitHub 上 rvoicilas/inotify-tools 项目的发布包）:

```shell
tar xvf inotify-tools-3.14.tar.gz
cd inotify-tools-3.14
./configure --prefix=/usr/local/inotify-tools-3.14
make && make install
ln -s /usr/local/inotify-tools-3.14 /usr/local/inotify
```

### 3.3 编写 rsync 监控脚本

（原文中脚本文件名缺失,以下以 /root/inotify.sh 为例）

```shell
vi /root/inotify.sh
```

```shell
#!/bin/sh
host1=192.168.10.10
src=/data/
des1=hequan
user1=hequan
/usr/local/inotify/bin/inotifywait -mrq --timefmt '%d/%m/%y %H:%M' \
    --format '%T %w%f' -e modify,delete,create,attrib ${src} | while read line
do
    rsync -vzrtopg --delete --progress ${src} ${user1}@${host1}::${des1} \
        --password-file=/etc/hequan.pwd
done
```

参数说明:

- `-m`,即 --monitor,表示始终保持事件监听状态。
- `-r`,即 --recursive,表示递归查询目录。
- `-q`,即 --quiet,表示打印出监控事件。
- `-e`,即 --event,通过此参数可以指定要监控的事件,常见的事件有 modify、delete、create、attrib 等
- `--timefmt`:指定时间的输出格式
- `--format`:指定变化文件的详细信息

建立认证文件（rsync 客户端认证文件只用加入密码）:

```shell
echo "123456" >> /etc/hequan.pwd
chmod 600 /etc/hequan.pwd
```

检查并后台启动脚本:

```shell
/bin/sh -n /root/inotify.sh      # 语法检查
chmod +x /root/inotify.sh
nohup sh /root/inotify.sh &
echo "nohup sh /root/inotify.sh &" >> /etc/rc.local
```

## 4. 同步测试

在更新源服务器上新建一个文件,运行以下的命令,看文件是否可以正常同步,看有无报错信息:

```shell
rsync -vzrtopg --delete --progress /data/ hequan@192.168.10.10::hequan \
    --password-file=/etc/hequan.pwd
```

将要更新的文件提交到更新源服务器中,这样就通过 inotify+rsync 批量的将更新文件同步到所有的目的服务器中,相当方便快捷。

## 5. inotify 参数

- `-m` 是保持一直监听
- `-r` 是递归查看目录
- `-q` 是打印出事件
- `-e create,move,delete,modify,attrib` 是指"监听 创建 移动 删除 写入 权限"事件

## 6. rsync 参数速查

- `-v, --verbose` 详细模式输出
- `-q, --quiet` 精简输出模式
- `-c, --checksum` 打开校验开关,强制对文件传输进行校验
- `-a, --archive` 归档模式,表示以递归方式传输文件,并保持所有文件属性,等于 -rlptgoD
- `-r, --recursive` 对子目录以递归模式处理
- `-R, --relative` 使用相对路径信息
- `-b, --backup` 创建备份,也就是对于目的已经存在有同样的文件名时,将老的文件重新命名为 ~filename。可以使用 --suffix 选项来指定不同的备份文件前缀。
- `--backup-dir` 将备份文件（如 ~filename）存放在目录下。
- `--suffix=SUFFIX` 定义备份文件前缀
- `-u, --update` 仅仅进行更新,也就是跳过所有已经存在于 DST,并且文件时间晚于要备份的文件。（不覆盖更新的文件）
- `-l, --links` 保留软链结
- `-L, --copy-links` 像对待常规文件一样处理软链结
- `--copy-unsafe-links` 仅仅拷贝指向 SRC 路径目录树以外的链结
- `--safe-links` 忽略指向 SRC 路径目录树以外的链结
- `-H, --hard-links` 保留硬链结
- `-p, --perms` 保持文件权限
- `-o, --owner` 保持文件属主信息
- `-g, --group` 保持文件属组信息
- `-D, --devices` 保持设备文件信息
- `-t, --times` 保持文件时间信息
- `-S, --sparse` 对稀疏文件进行特殊处理以节省 DST 的空间
- `-n, --dry-run` 显示哪些文件将被传输
- `-W, --whole-file` 拷贝文件,不进行增量检测
- `-x, --one-file-system` 不要跨越文件系统边界
- `-B, --block-size=SIZE` 检验算法使用的块尺寸,默认是 700 字节
- `-e, --rsh=COMMAND` 指定使用 rsh、ssh 方式进行数据同步
- `--rsync-path=PATH` 指定远程服务器上的 rsync 命令所在路径信息
- `-C, --cvs-exclude` 使用和 CVS 一样的方法自动忽略文件,用来排除那些不希望传输的文件
- `--existing` 仅仅更新那些已经存在于 DST 的文件,而不备份那些新创建的文件
- **`--delete` 删除那些 DST 中 SRC 没有的文件**
- `--delete-excluded` 同样删除接收端那些被该选项指定排除的文件
- `--delete-after` 传输结束以后再删除
- `--ignore-errors` 即使出现 IO 错误也进行删除
- `--max-delete=NUM` 最多删除 NUM 个文件
- `--partial` 保留那些因故没有完全传输的文件,以便加快随后的再次传输
- `--force` 强制删除目录,即使不为空
- `--numeric-ids` 不将数字的用户和组 ID 匹配为用户名和组名
- `--timeout=TIME` IP 超时时间,单位为秒
- `-I, --ignore-times` 不跳过那些有同样的时间和长度的文件
- `--size-only` 当决定是否要备份文件时,仅仅察看文件大小而不考虑文件时间
- `--modify-window=NUM` 决定文件是否时间相同时使用的时间戳窗口,默认为 0
- `-T, --temp-dir=DIR` 在 DIR 中创建临时文件
- `--compare-dest=DIR` 同样比较 DIR 中的文件来决定是否需要备份
- `-P` 等同于 --partial
- `--progress` 显示备份过程
- `-z, --compress` 对备份的文件在传输时进行压缩处理
- `--exclude=PATTERN` 指定排除不需要传输的文件模式
- `--include=PATTERN` 指定不排除而需要传输的文件模式
- `--exclude-from=FILE` 排除 FILE 中指定模式的文件
- `--include-from=FILE` 不排除 FILE 指定模式匹配的文件
- `--version` 打印版本信息
- `--address` 绑定到特定的地址
- `--config=FILE` 指定其他的配置文件,不使用默认的 rsyncd.conf 文件
- `--port=PORT` 指定其他的 rsync 服务端口
- `--blocking-io` 对远程 shell 使用阻塞 IO
- `--stats` 给出某些文件的传输状态
- **`--progress` 在传输时显示传输过程**
- `--log-format=formAT` 指定日志文件格式
- **`--password-file=FILE` 从 FILE 中得到密码**
- `--bwlimit=KBPS` 限制 I/O 带宽,KBytes per second
- `-h, --help` 显示帮助信息
