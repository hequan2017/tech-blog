---
title: "kubernetes webssh  管理  (django开发/通过调用K8S API实现)"
date: "2019-06-10 17:30:35"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2406980"
---
> **内容介绍**
>
> 本文介绍了作者开发的 K8s WebSSH 管理项目 seal：基于 Django + Channels（WebSocket）做前端交互，后端直接调用 Kubernetes API（exec 接口）在浏览器里对 Pod 执行命令，实现免登录容器终端的效果。文章给出项目地址与演示截图。

> **技术备注**
>
> 这类"浏览器直连容器终端"的方案核心是用 K8s exec API（SPDY/WebSocket 流式通道）。注意：① 新版官方 Python 客户端（kubernetes package）的 `stream()` 封装与此文时代接口基本一致，但 channels 1.x 已升级到 3.x/4.x，消费者（consumer）写法变化很大；② 生产使用务必在 exec 通道外层加认证鉴权与审计，避免未授权进入容器。

---

### 项目地址

> https://github.com/hequan2017/seal/

### demo

![](assets/2406980/01_2237982917e751bc6099ba36cca1ca66.jpg)

![](assets/2406980/02_e1333df55574b0501ae37675b3ef1ff1.jpg)

### 说明

> 主要使用 django+channels
> 直接调用 k8s api 执行命令
