---
title: "kubectl  proxy  加token 验证"
date: "2019-09-05 10:35:07"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2435698"
---
> **内容介绍**
>
> `kubectl proxy` 本身不支持对请求做 token 鉴权，作者的做法是：先在本机 8089
> 端口开启 proxy，再用 Go 的 goproxy 库在 8000 端口封装一层代理，在
> BeforeRequest 钩子中校验请求头 `token` 是否为 `1234`，不通过则中止请求，
> 通过后转发给 kubectl proxy。全文依次为：开启代理、完整的 Go 示例代码、
> 需要按环境修改的两处位置、以及请求方式（请求头带 `token: 1234`）。

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。
>
> 本文成文于 2019 年（Kubernetes 约 1.15/1.16 时代）。`kubectl proxy` 至今
> 仍可用、用法基本未变，它依旧不支持对请求做鉴权，本文"在外层再套一层带
> 校验的代理"的做法仍然适用。
>
> Kubernetes 自 1.24 起不再为 ServiceAccount 自动生成永久 Token Secret，
> 需要时可用 `kubectl create token` 签发短期令牌，或手工创建
> `kubernetes.io/service-account-token` 类型的 Secret。
>
> 示例代码使用了已废弃的 `ioutil.ReadAll` / `ioutil.NopCloser`，Go 1.16+
> 建议改用 `io.ReadAll` / `io.NopCloser`；token「1234」为明文硬编码，
> 仅作演示，生产环境请改用强随机密钥并启用 HTTPS。

---

> proxy 不支持 token 加验证，只能再封装一层代理，进行加验证。

## 1. 开启代理

```shell
kubectl proxy --port=8089 --address=127.0.0.1 --accept-hosts='^*$'  # 后面这个可以去掉，不用允许所有
```

## 2. 封装代理的 Go 代码

先初始化 Go 模块并创建 main.go：

```shell
mkdir go-proxy
cd go-proxy
go mod init go-proxy

vim main.go
```

main.go 完整内容如下，核心校验逻辑在 BeforeRequest 中：

```go
package main

import (
   "bytes"
   "fmt"
   "github.com/ouqiang/goproxy"
   "io/ioutil"
   "log"
   "net"
   "net/http"
   "net/url"
   "strings"
   "time"
)

type EventHandler struct{}

func (e *EventHandler) Connect(ctx *goproxy.Context, rw http.ResponseWriter) {

}

func (e *EventHandler) Auth(ctx *goproxy.Context, rw http.ResponseWriter) {

}

func (e *EventHandler) BeforeRequest(ctx *goproxy.Context) {

   if clientIP, _, err := net.SplitHostPort(ctx.Req.RemoteAddr); err == nil {
      if prior, ok := ctx.Req.Header["X-Forwarded-For"]; ok {
         clientIP = strings.Join(prior, ", ") + ", " + clientIP
      }
      ctx.Req.Header.Set("X-Forwarded-For", clientIP)
   }
   // 读取Body
   body, err := ioutil.ReadAll(ctx.Req.Body)
   if err != nil {
      // 错误处理
      return
   }
   if ctx.Req.Header.Get("token") != "1234" {
      fmt.Println("没有权限，禁止登录")
      ctx.Abort()
      return
   }
   // Request.Body只能读取一次, 读取后必须再放回去
   // Response.Body同理
   ctx.Req.Body = ioutil.NopCloser(bytes.NewReader(body))
}

func (e *EventHandler) BeforeResponse(ctx *goproxy.Context, resp *http.Response, err error) {
   if err != nil {
      return
   }
   // 修改response
}

// 设置上级代理
func (e *EventHandler) ParentProxy(req *http.Request) (*url.URL, error) {
   return url.Parse("http://127.0.0.1:8089")
}

func (e *EventHandler) Finish(ctx *goproxy.Context) {
   log.Printf("请求结束 URL:%s\n", ctx.Req.URL)
}

// 记录错误日志
func (e *EventHandler) ErrorLog(err error) {
   log.Println(err)
}

func main() {
   proxy := goproxy.New(goproxy.WithDelegate(&EventHandler{}))
   server := &http.Server{
      Addr:         ":8000",
      Handler:      proxy,
      ReadTimeout:  1 * time.Minute,
      WriteTimeout: 1 * time.Minute,
   }
   err := server.ListenAndServe()
   if err != nil {
      panic(err)
   }
}
```

启动封装代理（默认监听 :8000）：

```shell
go run main.go  # 启动封装代理，默认监听 :8000
```

## 3. 需要修改的两处

主要修改的地方有 2 个：

```go
if ctx.Req.Header.Get("token") != "1234" {  // 这里是输入你的 token 密码

	return url.Parse("http://127.0.0.1:8089")  // 这里是你本地的 proxy 接口
```

## 4. 请求

发起请求时，在请求头添加 `token: 1234`。
