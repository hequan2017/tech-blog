---
title: "gocelery 测试例子(windows会有报错，建议linux执行)"
date: "2021-10-15 10:58:13"
category: "go"
source: "https://blog.51cto.com/hequan/4221137"
---
> **内容介绍**
>
> 演示 Go 版 Celery 客户端/服务端（`gocelery`）的基本用法：服务端通过 Redis 作为 Broker 与 Backend 注册 `worker.add` 任务并启动 Worker；客户端同样连接 Redis，向队列投递随机参数的任务。Python Celery 也可以作为客户端调用 Go 的 Worker，实现跨语言任务队列。

> **技术备注**
>
> 示例基于 `gocelery/gocelery` 与 `gomodule/redigo` 编写；原文 import 路径被截断，实际应为 `github.com/gocelery/gocelery` 与 `github.com/gomodule/redigo/redis`。`gocelery` 已多年未活跃更新，Windows 下存在兼容性问题，建议在 Linux 环境运行或考虑 `Asynq`、`Machinery` 等更活跃的 Go 任务队列。

---

### celery

> python也可以调用 go的server，具体方法 可以看github

### server

```go
package main

import (
	"fmt"
	"time"

	"github.com/gocelery/gocelery"
	"github.com/gomodule/redigo/redis"
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
	"math/rand"

	"github.com/gocelery/gocelery"
	"github.com/gomodule/redigo/redis"
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
