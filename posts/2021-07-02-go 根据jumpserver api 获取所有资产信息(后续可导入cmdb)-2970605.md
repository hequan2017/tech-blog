---
title: "go 根据jumpserver api 获取所有资产信息(后续可导入cmdb)"
date: "2021-07-02 15:23:54"
category: "go"
source: "https://blog.51cto.com/hequan/2970605"
---

```markup
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"/Anderson-Lu/gofasion/gofasion"
	"/tidwall/gjson"
	"io/ioutil"
	"net/http"
	"time"
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
