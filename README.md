# 📚 技术博客

> hequan 的 51CTO 博客文章全集备份与再整理 · 共 **416** 篇 · 时间跨度 **2016–2025** 十年

[![在线阅读](https://img.shields.io/badge/在线阅读-hequan2017.github.io%2Ftech--blog-42b883?style=for-the-badge)](https://hequan2017.github.io/tech-blog/)
[![文章总数](https://img.shields.io/badge/文章总数-416-blue?style=flat-square)](INDEX.md)
[![分类](https://img.shields.io/badge/分类-20-green?style=flat-square)](INDEX.md)
[![License](https://img.shields.io/badge/版权归原作者所有-orange?style=flat-square)](https://blog.51cto.com/hequan)

**[简体中文](README.md)** · **[English](README.en.md)**

---

## 🌐 在线阅读

**👉 <https://hequan2017.github.io/tech-blog/>**

Vue 文档风格界面,开箱即用:

- 🗂️ 左侧分类目录 + 当前分类文章列表
- 🔍 即时搜索(按 `/` 快速聚焦)
- 🧭 文章页右侧本页大纲,滚动自动高亮
- 🌗 明暗双主题,跟随系统 / 手动切换
- 🌐 中英双语界面切换(右上角 EN / 中)
- 📋 代码块一键复制 + 语言标注 + 语法高亮
- 📊 首页年份分布图、分类卡片直达
- 📝 每篇文章顶部附 **内容介绍** 与 **技术演进备注**(如 CentOS 7 EOL、MySQL 5.7 EOL 等提示)

---

## 📖 项目简介

本仓库将博主在 [51CTO 博客](https://blog.51cto.com/hequan) 发布的全部技术文章抓取并转换为 Markdown,
图片已本地化至 `posts/assets/`,可**离线阅读、全文检索**。
每篇文章的 front-matter 保留原标题、发布时间、分类与原文链接(`source`)。

内容覆盖运维与后端开发的主要方向,适合作为实战参考资料:

| 方向 | 关键词 |
| --- | --- |
| 后端开发 | Go、Python、Django、TypeScript、Node |
| 系统运维 | Linux、Shell、Nginx、LNMP/LAMP、Tomcat |
| 云原生 | Kubernetes、Docker、OpenStack、Etcd |
| 自动化运维 | Ansible、Zabbix、Cobbler、Jenkins、AutoOps |
| 前端 | Vue、TypeScript、iview-admin、element |

---

## 📊 年份分布

| 年份 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 合计 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 篇数 | 112 | 55 | 78 | 55 | 12 | 20 | 40 | 34 | 9 | 1 | **416** |

---

## 🗂️ 分类目录(点击直达)

[python(88)](INDEX.md#python88-篇) · [go(67)](INDEX.md#go67-篇) · [Linux(64)](INDEX.md#linux64-篇) · [集群(41)](INDEX.md#集群41-篇) · [lnmp(33)](INDEX.md#lnmp33-篇) · [kubernetes(24)](INDEX.md#kubernetes24-篇) · [openstack(21)](INDEX.md#openstack21-篇) · [前端(13)](INDEX.md#前端13-篇) · [vue(10)](INDEX.md#vue10-篇) · [shell(9)](INDEX.md#shell9-篇) · [随笔(9)](INDEX.md#随笔9-篇) · [autoops(7)](INDEX.md#autoops7-篇) · [tomcat(6)](INDEX.md#tomcat6-篇) · [运维基础(5)](INDEX.md#运维基础5-篇) · [ansible(5)](INDEX.md#ansible5-篇) · [zabbix(4)](INDEX.md#zabbix4-篇) · [后端(3)](INDEX.md#后端3-篇) · [typescript(3)](INDEX.md#typescript3-篇) · [cobbler(2)](INDEX.md#cobbler2-篇) · [安全(2)](INDEX.md#安全2-篇)

📖 完整目录:[INDEX.md](INDEX.md) — 分类 × 年份双视图 + 按年总表

---

## 📁 目录结构

```
tech-blog/
├── index.html            # 单文件前端(Vue 文档风格,无构建依赖)
├── posts-index.json      # 文章索引(标题/日期/分类/原文链接)
├── INDEX.md              # 完整目录(分类×年份)
├── README.md             # 本文件
├── scripts/              # 工具链(抓取/组装/索引生成/文章校验)
└── posts/                # 全部 416 篇文章
    ├── YYYY-MM-DD-标题-文章ID.md
    └── assets/           # 本地化图片资源
```

文章文件名格式:`YYYY-MM-DD-标题-文章ID.md`

每篇文章 front-matter 示例:

```yaml
---
title: "k8s kubeadm v1.30.2部署"
date: "2024-07-30 11:31:58"
category: "集群"
source: "https://blog.51cto.com/hequan/11608966"
---
```

---

## ⚠️ 说明

- **抓取时间**:2026-09-28
- **版权**:原文版权归博主 [hequan](https://blog.51cto.com/hequan) 所有,转载注明出处
- **抓取工具**:Python + BeautifulSoup
- **时效提示**:部分文章写于较早年代,软件版本与命令在新系统上可能有差异;每篇顶部的"技术备注"会给出相应的演进提示,执行前请核对当前环境
