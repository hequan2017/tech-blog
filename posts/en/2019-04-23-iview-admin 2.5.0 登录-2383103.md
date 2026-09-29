---
title: "iview-admin 2.5.0 Login"
date: "2019-04-23 11:04:47"
category: "vue"
source: "https://blog.51cto.com/hequan/2383103"
lang: "en"
---
> **About this post**
>
> A record of the changes needed to hook iview-admin 2.5.0 up to a backend login API: in api/user.js, the login request is changed to POST /api/token, submitting the username and password; baseUrl is configured in config/index.js; libs/axios.js automatically attaches `Authorization: token xxx` to request headers; and the login response is handled in store/module/user.js.
>
> **Technical notes**
>
> iview-admin is based on Vue 2 + iview (View UI), and the project is no longer officially maintained. For new projects, consider vue-element-admin (Vue 2) or vue-vben-admin / soybean-admin (Vue 3).

---

api/user.js:

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

Configure `baseUrl` in config/index.js.

libs/axios.js:

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

In store/module/user.js, handle the login response: `const data = res.data`.
