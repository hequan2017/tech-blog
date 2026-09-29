---
title: "A Simple go webssh Example (Based on gin+ws+ssh)"
date: "2019-07-31 22:00:42"
category: "go"
source: "https://blog.51cto.com/hequan/2425428"
lang: "en"
---
> **About this post**
>
> This post introduces the author's small open-source project go-webssh, extracted
> from the webssh module of the dejavuzhou/felix project and modified. Built on
> gin + websocket + crypto/ssh, it connects to a Linux server terminal from a web
> page in the browser. To use it, change the account, password, and address in
> core/ssh.go (you can also switch to key-based login), then start it with
> go run main.go; the frontend offers two options: a vue version
> (index.vue, remember to change the backend address) and a plain index.html version.

> **Technical notes**
>
> In the original post, the `github.com/` prefix of the two project URLs was
> stripped by the editor; it has been restored here. The example uses
> ssh.InsecureIgnoreHostKey() to skip host key verification; in production you
> should use a HostKeyCallback that verifies properly. The project is based on
> gin / x/crypto dependencies from around 2019, so before building it now you
> need to upgrade the dependency versions yourself.

---

## 1. Project address

go-webssh: https://github.com/hequan2017/go-webssh (the Go version of webssh).

## 2. Origin and installation

The code of this project comes from https://github.com/dejavuzhou/felix; I only took the webssh part out of it, modified it a bit, and turned it into a webssh — noted here for attribution. Feel free to check out that project if needed.

Installation: change the account, password, address, and other information in core/ssh.go. You can also modify it yourself to log in with a key:

```go
func NewSshClient() (*ssh.Client, error) {
	config := &ssh.ClientConfig{
		Timeout:         time.Second * 5,
		User:            "root",
		HostKeyCallback: ssh.InsecureIgnoreHostKey(), // This works, but it is not secure enough
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

Then run:

```shell
go install
go run main.go
```

## 3. Frontend

I used vue for my tests; you can put it into your own project. It is in web/vue/index.vue — remember to change the backend address on line 32.

You can also make a plain index.html yourself and just put in a websocket connection.

web/html is the plain index.html version; it is untested and for reference only!
