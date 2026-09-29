---
title: "element-plus 中  使用 antd vue"
date: "2021-12-28 17:54:12"
category: "vue"
source: "https://blog.51cto.com/hequan/4853299"
---
> **内容介绍**
>
> 在 Vue 3 + Element Plus 项目里同时引入 Ant Design Vue 的入口配置：在 `main.js` 中引入 `ant-design-vue` 及其样式文件，然后链式 `app.use(Antd)`，与 ElementPlus（含 zh-cn 语言包）一起挂载到同一个应用实例上，实现两套组件库共存。

> **技术备注**
>
> 示例基于 Vue 3 + ant-design-vue 2.x（样式文件为 `ant-design-vue/dist/antd.css`）。ant-design-vue 3.x 起样式改为 `dist/antd.css` 迁移后的 `dist/reset.css`（4.x 更是转向 cssinjs、无需手动引入全量样式），升级时注意调整引入路径。两套组件库混用会显著增大打包体积，且主题风格不统一，仅建议过渡期使用，长期最好收敛到其中一套。

---

#### main.js

```js
import { createApp } from 'vue'
import 'element-plus/dist/index.css'
import './style/element_visiable.scss'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
// 引入search前端初始化相关内容
import './core/search'
// 引入封装的router
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

#### 主要

```js
import App from './App.vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';

   .use(Antd)
```
