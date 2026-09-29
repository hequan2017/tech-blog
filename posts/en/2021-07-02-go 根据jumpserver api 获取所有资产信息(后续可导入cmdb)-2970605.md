---
title: "go: Fetch All Asset Information via the JumpServer API (for Later Import into a CMDB)"
date: "2021-07-02 15:23:54"
category: "go"
source: "https://blog.51cto.com/hequan/2970605"
lang: "en"
---
> **About this post**
>
> Automatically pull all asset information through the JumpServer REST API: first call `/api/v1/authentication/auth/` to log in and obtain a Token, then access the paginated `/api/v1/assets/assets/` endpoint with `Authorization: Bearer <token>`, and finally parse the JSON with `gjson`/`gofasion` and print the hostnames, making it easy to import into a CMDB later.

> **Technical notes**
>
> The example is based on the JumpServer v2 API (2021). Since JumpServer v3, the API paths, authentication method, and pagination fields have all changed, so refer to the official API documentation for the corresponding version. The import paths for `gofasion` and `gjson` were truncated in the original source; they should actually be `github.com/Anderson-Lu/gofasion/gofasion` and `github.com/tidwall/gjson`.

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

// Get sends a GET request
// url:      the request URL
// response: the response body
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

// Post sends a POST request
// url:         the request URL
// data:        the data submitted by the POST request
// contentType: the request body format, e.g. application/json
// content:     the response body
func Post(url string, data interface{}, contentType string) string {

	// Timeout: 5 seconds
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
