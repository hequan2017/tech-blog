---
title: "element-plus 中  使用 antd vue"
date: "2021-12-28 17:54:12"
category: ""
source: "https://blog.51cto.com/hequan/4853299"
---
> **内容介绍**
>
> 本文是技术实践笔记,记录了「element-plus 中  使用 antd vue」的相关内容。主要涉及:#### main.js #### 主要…

---

#### main.js

```pythonimport { createApp } from 'vue'
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
```python

#### 主要

```pythonimport App from './App.vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';

   .use(Antd)
```
