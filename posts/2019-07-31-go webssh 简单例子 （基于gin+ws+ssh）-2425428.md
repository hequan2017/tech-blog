---
title: "go webssh  简单例子 （基于gin+ws+ssh）"
date: "2019-07-31 22:00:42"
category: "go"
source: "https://blog.51cto.com/hequan/2425428"
---
> **内容介绍**
>
> 本文介绍作者的开源小项目 go-webssh:从 dejavuzhou/felix 项目中抽出
> webssh 模块修改而成,基于 gin + websocket + crypto/ssh,在浏览器网页
> 里连接 Linux 服务器终端。使用时修改 core/ssh.go 里的账号、密码、地址
> (也可改成密钥登录),go run main.go 启动;前端提供 vue 版
> (index.vue,记得改后端地址)与普通 index.html 版本两种选择。

> **技术备注**
>
> 原文两处项目地址的 `github.com/` 前缀被编辑器吃掉,已补全。示例用
> ssh.InsecureIgnoreHostKey() 跳过主机密钥校验,生产环境应改用
> HostKeyCallback 正常校验;项目基于 2019 年前后的 gin / x/crypto 依赖,
> 现在编译前需自行升级依赖版本。

---

## 1. 项目地址

go-webssh:https://github.com/hequan2017/go-webssh (go 语言版 webssh)。

## 2. 来源与安装

本项目代码来自 https://github.com/dejavuzhou/felix ,只是把里面的 webssh 拿出来,修改了一下,做成 webssh,特此说明。有需要可以查看此项目。

安装:修改 core/ssh.go 里面的账号密码地址等信息。也可以自己修改成用密钥登录:

```go
func NewSshClient() (*ssh.Client, error) {
	config := &ssh.ClientConfig{
		Timeout:         time.Second * 5,
		User:            "root",
		HostKeyCallback: ssh.InsecureIgnoreHostKey(), //这个可以， 但是不够安全
		//HostKeyCallback: hostKeyCallBackFunc(h.Host),
	}
	//if h.Type == "password" {
	config.Auth = []ssh.AuthMethod{ssh.Password("123456")}
	//} else {
	//	config.Auth = []ssh.AuthMethod{publicKeyAuthFunc(h.Key)}
	//}
	addr := fmt.Sprintf("%s:%d", "192.168.100.200", 22)
	c, err := ssh.Dial("tcp", addr, config)
	if err != nil {
		return nil, err
	}
	return c, nil
}
```

然后运行:

```shell
go install
go run main.go
```

## 3. 前端

我测试的时候用的是 vue,你可以放进你们项目里面。在 web/vue/index.vue 里面,记得修改 32 行的后端地址。

也可以自己弄个普通 index.html,放一个 websocket 连接即可。

web/html 是普通版本 index.html,未测试,仅供参考!
