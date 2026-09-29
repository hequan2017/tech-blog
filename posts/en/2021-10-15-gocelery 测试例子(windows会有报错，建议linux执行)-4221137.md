---
title: "gocelery Test Example (Errors on Windows; Run on Linux Instead)"
date: "2021-10-15 10:58:13"
category: "go"
source: "https://blog.51cto.com/hequan/4221137"
lang: "en"
---
> **About this post**
>
> Demonstrates the basic usage of the Go Celery client/server (`gocelery`): the server uses Redis as both Broker and Backend, registers the `worker.add` task, and starts the Worker; the client likewise connects to Redis and dispatches tasks with random arguments to the queue. Python Celery can also act as a client to invoke the Go Worker, enabling a cross-language task queue.

> **Technical notes**
>
> The examples are based on `gocelery/gocelery` and `gomodule/redigo`; the import paths in the original text are truncated and should actually be `github.com/gocelery/gocelery` and `github.com/gomodule/redigo/redis`. `gocelery` has not been actively maintained for years and has compatibility issues on Windows, so it is recommended to run it in a Linux environment, or consider more actively maintained Go task queues such as `Asynq` and `Machinery`.

---

### celery

> Python can also call the Go server; see GitHub for the details.

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
