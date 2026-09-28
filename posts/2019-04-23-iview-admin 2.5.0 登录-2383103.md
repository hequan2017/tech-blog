---
title: "iview-admin 2.5.0  登录"
date: "2019-04-23 11:04:47"
category: "vue"
source: "https://blog.51cto.com/hequan/2383103"
---
> **内容介绍**
>
> 记录 iview-admin 2.5.0 对接后端登录接口的改造点：api/user.js 中 login 请求改为 POST /api/token 提交用户名密码，config/index.js 配置 baseUrl，libs/axios.js 在请求头中自动附带 `Authorization: token xxx`，store/module/user.js 中处理登录返回数据。
>
> **技术备注**
>
> iview-admin 基于 Vue 2 + iview（View UI），该项目官方已停止维护，新项目建议用 vue-element-admin（Vue 2）或 vue-vben-admin / soybean-admin（Vue 3）。

---

api/user.js：

```javascript
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
```

config/index.js 中配置 `baseUrl`。

libs/axios.js：

```javascript
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
```

store/module/user.js 中处理登录返回：`const data = res.data`。
