---
title: "go 根据jumpserver api 获取所有资产信息(后续可导入cmdb)"
date: "2021-07-02 15:23:54"
category: "go"
source: "https://blog.51cto.com/hequan/2970605"
---
> **内容介绍**
>
> 通过 JumpServer REST API 自动拉取全部资产信息：先调用 `/api/v1/authentication/auth/` 登录获取 Token，再携带 `Authorization: Bearer <token>` 访问 `/api/v1/assets/assets/` 分页接口，最后用 `gjson`/`gofasion` 解析 JSON 并打印主机名，方便后续导入 CMDB。

> **技术备注**
>
> 示例基于 JumpServer v2 API（2021 年）；JumpServer v3 起 API 路径、认证方式与分页字段均有调整，建议参考对应版本的官方 API 文档。`gofasion` 与 `gjson` 的 import 路径原文被截断，实际应为 `github.com/Anderson-Lu/gofasion/gofasion` 与 `github.com/tidwall/gjson`。

---

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/Anderson-Lu/gofasion/gofasion"
	"github.com/tidwall/gjson"
)

// Get 发送GET请求
// url：         请求地址
// response：    请求返回的内容
func Get(url string,token string) interface{} {

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := http.NewRequest("GET", url, nil)
	resp.Header.Set("Authorization", fmt.Sprintf("Bearer %s",token))

	if err != nil {
		panic(err)
	}
	response, _ := (resp)

	body, _ := ioutil.ReadAll(response.Body)
	return string(body)
}

// Post 发送POST请求
// url：         请求地址
// data：        POST请求提交的数据
// contentType： 请求体格式，如：application/json
// content：     请求放回的内容
func Post(url string, data interface{}, contentType string) string {

	// 超时时间：5秒
	client := &http.Client{Timeout: 5 * time.Second}
	jsonStr, _ := json.Marshal(data)
	resp, err := client.Post(url, contentType, bytes.NewBuffer(jsonStr))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	result, _ := ioutil.ReadAll(resp.Body)

	return string(result)
}

func main()  {
	info :=  map[string]string{
		"username":"root",
		"password":"123456",
	}

	re := Post("http://192.168.1.1/api/v1/authentication/auth/",info,"application/json")
	value := gjson.Get(re, "token")
	token := value.String()

	jmsHost :=Get("http://192.168.1.1/api/v1/assets/assets/",token)
	fmt.Println(jmsHost)

	data := gofasion.NewFasion(jmsHost)
	dataHost := data.Array()
	for _,v :=range dataHost {
		fmt.Println(v)
		fmt.Println(v.Get("hostname").ValueStr())
	}

}
```
