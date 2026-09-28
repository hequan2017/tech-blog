---
title: "iview-admin 2.5.0  登录"
date: "2019-04-23 11:04:47"
category: "vue"
source: "https://blog.51cto.com/hequan/2383103"
---
> **内容介绍**
>
> 本文是Vue 前端工程化实践,记录了「iview-admin 2.5.0  登录」的相关内容。

---

```python
api /user.js

export const login = ({ userName, password }) => {
  const data = {
    username: userName,
    password
  }
  return axios.request({
    url: '/api/token',
    data,
    method: 'post'
  })
}

config/index.js

baseUrl:

libs/axios.js

import { getToken } from '@/libs/util'

  getInsideConfig () {
    const config = {
      baseURL: this.baseUrl,
      headers: {
        //
      }
    }
    if (getToken()) {
      config.headers['Authorization'] = `token ${getToken()}`
    }
    return config
  }


store/module/user.js

const data = res.data
```
