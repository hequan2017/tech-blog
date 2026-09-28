---
title: "kubectl  proxy  加token 验证"
date: "2019-09-05 10:35:07"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2435698"
---

### kubectl  proxy  加token 验证

> proxy 不支持token加验证，只能再封装了一层代理，进行加验证。

#### 开启代理

```
kubectl  proxy  --port=8089  --address=127.0.0.1   --accept-hosts='^*$'　　# 后面这个可以去掉，不用允许所有
```

#### 代码

```
mkdir go-proxy
cd go-proxy
go mod init go-proxy

vim main.go

package main

import (
   "bytes"
   "fmt"
   "/ouqiang/goproxy"
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

func (e *EventHandler) Auth(ctx *goproxy.Context, rw http.ResponseWriter)  {

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
   if  ctx.Req.Header.Get("token") != "1234" {
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

```
go run  main.go
```

#### 注意

> 主要修改的地方有２个

```
  if  ctx.Req.Header.Get("token") != "1234" {    这里是输入你的token密码
	
	return url.Parse("http://127.0.0.1:8089")   这里是你本地的 proxy　接口
	
```

#### 请求

> 请求头　　添加　 token  : 1234
