---
title: "Kubernetes WebSSH Management (Developed with Django, Implemented via the K8s API)"
date: "2019-06-10 17:30:35"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2406980"
lang: "en"
---
> **About this post**
>
> This post introduces seal, a K8s WebSSH management project developed by the author: it uses Django + Channels (WebSocket) for front-end interaction, while the back end calls the Kubernetes API (the exec interface) directly to run commands in Pods from the browser, achieving a login-free container terminal. The post provides the project URL and demo screenshots.

> **Technical notes**
>
> The core of this kind of "browser connects directly to the container terminal" solution is the K8s exec API (SPDY/WebSocket streaming channels). Note: (1) the `stream()` wrapper in the new official Python client (the kubernetes package) is essentially the same as the interface from that era, but Channels has moved from 1.x to 3.x/4.x and the way consumers are written has changed considerably; (2) for production use, be sure to add authentication, authorization, and auditing around the exec channel to prevent unauthorized access to containers.

---

### Project URL

> https://github.com/hequan2017/seal/

### Demo

![Pod list page of the WebSSH management console](../assets/2406980/01_2237982917e751bc6099ba36cca1ca66.jpg)

![Terminal running commands inside a container via WebSSH](../assets/2406980/02_e1333df55574b0501ae37675b3ef1ff1.jpg)

### Description

> Mainly built with django+channels
> Calls the k8s api directly to execute commands
