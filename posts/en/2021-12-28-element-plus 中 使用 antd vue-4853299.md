---
title: "Using Ant Design Vue with Element Plus"
date: "2021-12-28 17:54:12"
category: "vue"
source: "https://blog.51cto.com/hequan/4853299"
lang: "en"
---
> **About this post**
>
> Entry configuration for bringing Ant Design Vue into a Vue 3 + Element Plus project: import `ant-design-vue` and its stylesheet in `main.js`, then chain `app.use(Antd)` and mount it on the same application instance together with ElementPlus (including the zh-cn locale), so that the two component libraries coexist.

> **Technical notes**
>
> The example is based on Vue 3 + ant-design-vue 2.x (with the stylesheet `ant-design-vue/dist/antd.css`). Starting from ant-design-vue 3.x, the stylesheet changed to `dist/reset.css`, which `dist/antd.css` was migrated into (4.x went further and moved to cssinjs, with no need to manually import the full stylesheet), so pay attention to adjusting the import path when upgrading. Mixing the two component libraries significantly increases the bundle size and leads to inconsistent theming; it is only recommended for a transition period — in the long run it is best to converge on one of them.

---

#### main.js

```js
import { createApp } from 'vue'
import 'element-plus/dist/index.css'
import './style/element_visiable.scss'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
// Import the search frontend initialization
import './core/search'
// Import the encapsulated router
import router from '@/router/index'
import run from '@/core/search.js'
import auth from '@/directive/auth'

import '@/permission'
import { store } from '@/store/index'

import App from './App.vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';

const app = createApp(App)
app.config.productionTip = false
app.use(run)
  .use(auth)
  .use(store)
  .use(router)
   .use(Antd)
  .use(ElementPlus, { locale: zhCn }).mount('#app')

export default app
```

#### Key parts

```js
import App from './App.vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';

   .use(Antd)
```
