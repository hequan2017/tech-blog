---
title: "Linux inotify+rsync"
date: "2016-04-15 17:56:10"
category: "Linux"
source: "https://blog.51cto.com/hequan/1764262"
lang: "en"
---
> **About this post**
>
> This post demonstrates the complete deployment of an inotify+rsync real-time
> synchronization solution on CentOS 6.5: on the destination server (the rsync
> daemon side), check/install rsync, write /etc/rsyncd.conf and explain each
> field line by line (uid, max connections, log format, module parameters,
> auth users, secrets file, hosts allow, etc.), create the authentication
> password file and the motd, and start the daemon; on the update-source
> server (the client), list the filesystem events inotify can monitor, install
> inotify-tools from source, write an inotifywait monitoring script for
> event-triggered automatic pushing, and finally run a synchronization test,
> with an inotify and rsync parameter quick reference attached.

> **Technical notes**
>
> CentOS 6 reached end of life (EOL) in November 2020; for production
> environments, migrating to Rocky Linux / AlmaLinux / Ubuntu LTS is
> recommended. On newer distributions, the rsync daemon should be managed by
> systemd rather than the /etc/rc.local approach used in this post;
> hosts allow accepts both 192.168.10.0/24 and
> 192.168.10.0/255.255.255.0 notations, which have the same effect.

---

## 1. System Environment

- System: centos 6.5_64
- Update-source server: 192.168.10.11
- Destination server: 192.168.10.10

## 2. Destination Server Configuration (rsync daemon side: 192.168.10.10)

### 2.1 Check whether rsync is installed

```shell
rpm -qa | grep rsync
```

If it is not installed, run the following command to install it:

```shell
yum -y install rsync
```

### 2.2 Define the rsync configuration file /etc/rsyncd.conf

Run the following on the destination server 192.168.10.10:

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

### 2.3 The rsyncd.conf Configuration File Explained

Global parameters:

- `uid = rsync` — the user under which the RSYNC daemon runs
- `gid = rsync` — the group under which the RSYNC daemon runs
- `use chroot = 0` — do not use chroot
- `max connections = 0` — maximum number of connections; 0 means unlimited
- `port = 873` — default port 873

The following files are generated automatically after the RSYNC service is installed:

- `pid file = /var/run/rsyncd.pid` — where the pid file is stored
- `lock file = /var/run/rsync.lock` — where the lock file is stored. Specifies the lock file that supports the max connections parameter; the default is /var/run/rsyncd.lock.
- `log file = /var/log/rsyncd.log` — where the log file is stored

`Timeout = 300`: This option overrides the IP timeout specified by the client. It ensures that the rsync server will not wait forever for a crashed client. The timeout unit is seconds; 0 means no timeout is defined, which is also the default. For an anonymous rsync server, an ideal value is 600.

`Log format = %t %a %m %f %b`: Through this option, users can customize the fields of the log file when using transfer logging. Its value is a string containing format specifiers; the available format specifiers are as follows:

- `%h` remote host name
- `%a` remote IP address
- `%l` file length in characters
- `%p` process id of this rsync session
- `%o` operation type: " send" or " recv"
- `%f` file name
- `%P` module path
- `%m` module name
- `%t` current time
- `%u` authenticated username (null when anonymous)
- `%b` number of bytes actually transferred
- `%c` when sending a file, this field records the checksum of that file

The default log format is: " %o %h [%a] %m (%u) %f %l". Generally, " %t [%p] " is added at the head of each line. The source code also ships with a perl script called rsyncstats that produces statistics from log files in this format.

- `#transfer logging = yes` — makes the rsync server record download and upload operations in ftp format in its own separate log
- `syslog facility = local3` — specifies the message level used when rsync sends log messages to syslog. The common facilities are: auth, authpriv, cron, daemon, ftp, kern, lpr, mail, news, security, sys-log, user, uucp, local0, local1, local2, local3, local4, local5, local6, and local7. The default is daemon.

Module parameters:

- `[hequan]` — the authenticated module name, which must be specified on the client side
- `path = /data/` — the directory to be mirrored; must not be omitted!
- `comment = backup web` — a comment describing this module
- `ignore errors` — allows ignoring some unrelated IO errors
- `read only = yes` — sets whether clients are allowed to upload files. If true, any upload request fails; if false and the server directory's read/write permissions allow, uploads are permitted. The default is true.
- `list = no` — do not allow listing files
- `auth users = bak` — the authenticated usernames; if this line is absent, the module is anonymous, and these users have nothing to do with system users

  This option specifies a space- or comma-separated list of usernames; only these users are allowed to connect to the module. These users are unrelated to system users. If " auth users" is set, then when a client issues a connection request to the module, rsync will challenge it to verify its identity, using the challenge/response authentication protocol. The usernames and passwords are stored in plain text in the file specified by the " secrets file" option. By default, the module can be connected without a password (that is, anonymously).

- `secrets file = /etc/rsync.pwd` — the username/password comparison table; the password file is created by yourself

  This option specifies a file containing username:password pairs. It only takes effect when " auth users" is defined. Each line of the file contains one username:passwd pair. Generally, the password should preferably not exceed 8 characters. There is no default secrets file name; one must be specified explicitly (for example: /etc/www1.pwd). Note: the permissions of this file must be 600, otherwise clients will not be able to connect to the server.

- `hosts allow = 192.168.10.0/255.255.255.0` — allowed hosts or network segments

  This option specifies which client IPs are allowed to connect to the module. The client patterns can take the following forms:

  - a single IP address, e.g. 192.168.10.11
  - an entire network segment, e.g. 192.168.10.0/24, or 192.168.10.0/255.255.255.0
  - multiple IPs or segments separated by spaces; "*" means all; by default, all hosts are allowed to connect

- `hosts deny = 0.0.0.0/0` — denied hosts

### 2.4 Create the authentication file and grant permissions

Create the authentication file /etc/hequan.pwd; this file must match the file name specified in the configuration file. The format here is username:password. For security reasons, using the root user in real deployments is not recommended.

On the destination server 192.168.10.10:

```shell
echo "hequan:123456" >> /etc/hequan.pwd
chmod 600 /etc/hequan.pwd
chmod 600 /etc/rsyncd.conf
```

Create the user and grant permissions:

```shell
useradd rsync -s /sbin/nologin
chown -R rsync.rsync /hequan/
```

### 2.5 Create the motd file (optional)

rsyncd.motd holds the welcome message of the rsync service; you can put any text you like in it, for example:

```shell
echo "Welcome to use the rsync services!" >> /var/rsyncd.motd
```

### 2.6 Start rsync

```shell
/usr/bin/rsync --daemon
echo "/usr/bin/rsync --daemon" >> /etc/rc.local
```

## 3. Update-Source Server Configuration (rsync client: 192.168.10.11)

### 3.1 Filesystem events inotify can monitor

- `IN_ACCESS`, i.e. the file was accessed
- `IN_MODIFY`, the file was written to (write)
- `IN_ATTRIB`, the file attributes were changed, e.g. chmod, chown, touch, etc.
- `IN_CLOSE_WRITE`, a writable file was closed
- `IN_CLOSE_NOWRITE`, a non-writable file was closed
- `IN_OPEN`, the file was opened
- `IN_MOVED_FROM`, the file was moved away, e.g. mv
- `IN_MOVED_TO`, the file was moved in, e.g. mv, cp
- `IN_CREATE`, a new file was created
- `IN_DELETE`, the file was deleted, e.g. rm
- `IN_DELETE_SELF`, self-deletion, i.e. an executable deletes itself while running
- `IN_MOVE_SELF`, self-move, i.e. an executable moves itself while running
- `IN_UNMOUNT`, the host filesystem was unmounted
- `IN_CLOSE`, the file was closed; equivalent to (IN_CLOSE_WRITE | IN_CLOSE_NOWRITE)
- `IN_MOVE`, the file was moved; equivalent to (IN_MOVED_FROM | IN_MOVED_TO)

Note: "files" above also includes directories.

### 3.2 Install inotify-tools

Before installing inotify-tools, make sure your Linux kernel is at least 2.6.13 and was compiled with the CONFIG_INOTIFY option enabled; you can also check with the following command:

```shell
ls /proc/sys/fs/inotify
```

If max_queued_events, max_user_instances, and max_user_watches are all present, the kernel supports it.

Compile and install (the original wget download link is no longer valid; it was a release package of the rvoicilas/inotify-tools project on GitHub):

```shell
tar xvf inotify-tools-3.14.tar.gz
cd inotify-tools-3.14
./configure --prefix=/usr/local/inotify-tools-3.14
make && make install
ln -s /usr/local/inotify-tools-3.14 /usr/local/inotify
```

### 3.3 Write the rsync monitoring script

(The script file name is missing in the original; /root/inotify.sh is used as an example below.)

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

Parameter description:

- `-m`, i.e. --monitor, means staying in the event-listening state at all times.
- `-r`, i.e. --recursive, means recursing through directories.
- `-q`, i.e. --quiet, means printing out the monitored events.
- `-e`, i.e. --event, specifies the events to monitor through this parameter; common events include modify, delete, create, attrib, etc.
- `--timefmt`: specifies the output format of the time
- `--format`: specifies the detailed information of changed files

Create the authentication file (the rsync client authentication file only needs the password):

```shell
echo "123456" >> /etc/hequan.pwd
chmod 600 /etc/hequan.pwd
```

Check and start the script in the background:

```shell
/bin/sh -n /root/inotify.sh      # syntax check
chmod +x /root/inotify.sh
nohup sh /root/inotify.sh &
echo "nohup sh /root/inotify.sh &" >> /etc/rc.local
```

## 4. Synchronization Test

Create a new file on the update-source server, run the following command, and check whether the file syncs correctly and whether any error messages appear:

```shell
rsync -vzrtopg --delete --progress /data/ hequan@192.168.10.10::hequan \
    --password-file=/etc/hequan.pwd
```

Put the files to be updated on the update-source server, and inotify+rsync will batch-sync the updated files to all destination servers — quite convenient and fast.

## 5. inotify Parameters

- `-m` keeps listening all the time
- `-r` recurses through directories
- `-q` prints out events
- `-e create,move,delete,modify,attrib` means monitoring "create, move, delete, write, permission" events

## 6. rsync Parameter Quick Reference

- `-v, --verbose` verbose output mode
- `-q, --quiet` quiet output mode
- `-c, --checksum` turn on the checksum switch, forcing checksum verification on file transfers
- `-a, --archive` archive mode; transfers files recursively and preserves all file attributes; equals -rlptgoD
- `-r, --recursive` process subdirectories recursively
- `-R, --relative` use relative path information
- `-b, --backup` create backups: when a file with the same name already exists at the destination, rename the old file to ~filename. Use the --suffix option to specify a different backup file prefix.
- `--backup-dir` store the backup files (such as ~filename) in a directory.
- `--suffix=SUFFIX` define the backup file prefix
- `-u, --update` update only, i.e. skip all files that already exist in DST and whose file time is later than the file to be backed up. (Does not overwrite newer files.)
- `-l, --links` preserve symlinks
- `-L, --copy-links` treat symlinks like regular files
- `--copy-unsafe-links` copy only links pointing outside the SRC path directory tree
- `--safe-links` ignore links pointing outside the SRC path directory tree
- `-H, --hard-links` preserve hard links
- `-p, --perms` preserve file permissions
- `-o, --owner` preserve file owner information
- `-g, --group` preserve file group information
- `-D, --devices` preserve device file information
- `-t, --times` preserve file time information
- `-S, --sparse` handle sparse files specially to save space in DST
- `-n, --dry-run` show which files would be transferred
- `-W, --whole-file` copy whole files without incremental (delta) detection
- `-x, --one-file-system` do not cross filesystem boundaries
- `-B, --block-size=SIZE` block size used by the checksum algorithm; the default is 700 bytes
- `-e, --rsh=COMMAND` specify rsh or ssh for data synchronization
- `--rsync-path=PATH` specify the path of the rsync command on the remote server
- `-C, --cvs-exclude` auto-ignore files the same way CVS does, to exclude files you do not want to transfer
- `--existing` update only files that already exist in DST, and do not back up newly created files
- **`--delete` delete files in DST that are not in SRC**
- `--delete-excluded` also delete excluded files on the receiving side (those excluded by the specified options)
- `--delete-after` delete after the transfer finishes
- `--ignore-errors` delete even if IO errors occur
- `--max-delete=NUM` delete at most NUM files
- `--partial` keep files that were not fully transferred for some reason, to speed up subsequent re-transfers
- `--force` force deletion of directories, even if not empty
- `--numeric-ids` do not map numeric user and group IDs to user and group names
- `--timeout=TIME` IP timeout, in seconds
- `-I, --ignore-times` do not skip files that have the same time and length
- `--size-only` when deciding whether to back up a file, look only at the file size, not the file time
- `--modify-window=NUM` timestamp window used to decide whether file times are the same; the default is 0
- `-T, --temp-dir=DIR` create temporary files in DIR
- `--compare-dest=DIR` also compare files in DIR to decide whether a backup is needed
- `-P` equivalent to --partial
- `--progress` show the backup process
- `-z, --compress` compress the files being backed up during transfer
- `--exclude=PATTERN` specify patterns of files to exclude from transfer
- `--include=PATTERN` specify patterns of files that are not excluded and need to be transferred
- `--exclude-from=FILE` exclude files matching the patterns specified in FILE
- `--include-from=FILE` do not exclude files matching the patterns specified in FILE
- `--version` print version information
- `--address` bind to a specific address
- `--config=FILE` specify an alternative configuration file instead of the default rsyncd.conf
- `--port=PORT` specify an alternative rsync service port
- `--blocking-io` use blocking IO for the remote shell
- `--stats` give the transfer status of some files
- **`--progress` show the transfer progress during transfer**
- `--log-format=formAT` specify the log file format
- **`--password-file=FILE` get the password from FILE**
- `--bwlimit=KBPS` limit I/O bandwidth, KBytes per second
- `-h, --help` show help information
