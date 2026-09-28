---
title: "gocelery 测试例子(windows会有报错，建议linux执行)"
date: "2021-10-15 10:58:13"
category: "go"
source: "https://blog.51cto.com/hequan/4221137"
---
> **内容介绍**
>
> 本文是Go 语言后端开发实战,记录了「gocelery 测试例子(windows会有报错，建议linux执行)」的相关内容。主要涉及:### celery > python也可以调用 go的server，具体方法 可以看github ### server…

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

### celery

> python也可以调用 go的server，具体方法 可以看github

### server

```go
package main

import (
	"fmt"
	"/gocelery/gocelery"
	"/gomodule/redigo/redis"
	"time"
)

func main() {
	// create redis connection pool
	redisPool := &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL("redis://127.0.0.1:6379")
			if err != nil {
				return nil, err
			}
			return c, err
		},
	}

	// initialize celery client
	cli, _ := gocelery.NewCeleryClient(
		gocelery.NewRedisBroker(redisPool),
		&gocelery.RedisCeleryBackend{Pool: redisPool},
		500, // number of workers
	)

	// task
	add := func(a, b int) int {
		fmt.Println(a + b)
		return a + b
	}

	// register task
	cli.Register("worker.add", add)

	// start workers (non-blocking call)
	cli.StartWorker()

	// wait for client request
	time.Sleep(1000000 * time.Hour)

	//// stop workers gracefully (blocking call)
	cli.StopWorker()

}
```

### client

```go
package main

import (
	"/gocelery/gocelery"
	"/gomodule/redigo/redis"
	"math/rand"
)

func main() {
	redisPool1 := &redis.Pool{
		Dial: func() (redis.Conn, error) {
			c, err := redis.DialURL("redis://127.0.0.1:6379")
			if err != nil {
				return nil, err
			}
			return c, err
		},
	}

	// initialize celery client
	cli, _ := gocelery.NewCeleryClient(
		gocelery.NewRedisBroker(redisPool1),
		&gocelery.RedisCeleryBackend{Pool: redisPool1},
		1,
	)

	// prepare arguments
	taskName := "worker.add"
	argA := rand.Intn(10)
	argB := rand.Intn(10)

	// run task
	_, err := cli.Delay(taskName, argA, argB)
	if err != nil {
		panic(err)
	}

	//// get results from backend with timeout
	//res, err := asyncResult.Get(10 * time.Second)
	//if err != nil {
	//	panic(err)
	//}
	//
	//fmt.Printf("result: %+v of type %+v", res, reflect.TypeOf(res))
}
```
