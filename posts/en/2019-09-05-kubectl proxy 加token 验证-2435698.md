---
title: "Adding token authentication to kubectl proxy"
date: "2019-09-05 10:35:07"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2435698"
lang: "en"
---
> **About this post**
>
> `kubectl proxy` itself does not support token-based authentication of requests. The author's approach: first start the proxy locally on port 8089, then use Go's goproxy library to wrap another proxy layer on port 8000. In the BeforeRequest hook, it checks whether the request header `token` equals `1234`; if not, the request is aborted; once it passes, the request is forwarded to kubectl proxy. The post covers, in order: starting the proxy, the complete Go sample code, the two places that need to be adapted per environment, and how to make requests (with the header `token: 1234`).

> **Technical notes**
>
> CentOS 7 reached end of life (EOL) on June 30, 2024; consider migrating to Rocky Linux 9 / AlmaLinux 9 or the domestic openEuler.
>
> This post was written in 2019 (around the Kubernetes 1.15/1.16 era). `kubectl proxy` still works today with essentially unchanged usage; it still does not support authenticating requests, so the approach of "wrapping another validating proxy layer around it" remains applicable.
>
> Since Kubernetes 1.24, permanent Token Secrets are no longer auto-generated for ServiceAccounts; when needed, you can use `kubectl create token` to issue short-lived tokens, or manually create a Secret of type `kubernetes.io/service-account-token`.
>
> The sample code uses the deprecated `ioutil.ReadAll` / `ioutil.NopCloser`; on Go 1.16+, prefer `io.ReadAll` / `io.NopCloser`. The token "1234" is hardcoded in plain text for demonstration only; in production, use a strong random key and enable HTTPS.

---

> kubectl proxy does not support token-based authentication, so the only option is to wrap another proxy layer that performs the authentication.

## 1. Start the proxy

```shell
kubectl proxy --port=8089 --address=127.0.0.1 --accept-hosts='^*$'  # The latter can be removed; no need to allow all
```

## 2. Go code for the wrapper proxy

First initialize the Go module and create main.go:

```shell
mkdir go-proxy
cd go-proxy
go mod init go-proxy

vim main.go
```

The full content of main.go is as follows; the core validation logic lives in BeforeRequest:

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
   // Read the body
   body, err := ioutil.ReadAll(ctx.Req.Body)
   if err != nil {
      // error handling
      return
   }
   if ctx.Req.Header.Get("token") != "1234" {
      fmt.Println("没有权限，禁止登录")
      ctx.Abort()
      return
   }
   // Request.Body can only be read once; it must be put back after reading
   // Same for Response.Body
   ctx.Req.Body = ioutil.NopCloser(bytes.NewReader(body))
}

func (e *EventHandler) BeforeResponse(ctx *goproxy.Context, resp *http.Response, err error) {
   if err != nil {
      return
   }
   // modify the response
}

// Set the parent proxy
func (e *EventHandler) ParentProxy(req *http.Request) (*url.URL, error) {
   return url.Parse("http://127.0.0.1:8089")
}

func (e *EventHandler) Finish(ctx *goproxy.Context) {
   log.Printf("请求结束 URL:%s\n", ctx.Req.URL)
}

// Log errors
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

Start the wrapper proxy (listens on :8000 by default):

```shell
go run main.go  # start the wrapper proxy, listens on :8000 by default
```

## 3. The two places to modify

There are two main places to modify:

```go
if ctx.Req.Header.Get("token") != "1234" {  // enter your token password here

	return url.Parse("http://127.0.0.1:8089")  // your local proxy endpoint here
```

## 4. Making requests

When making a request, add `token: 1234` to the request headers.
