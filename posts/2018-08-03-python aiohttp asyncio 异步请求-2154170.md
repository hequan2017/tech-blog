---
title: "python  aiohttp  asyncio  异步请求"
date: "2018-08-03 16:40:39"
category: "python"
source: "https://blog.51cto.com/hequan/2154170"
---
> **内容介绍**
>
> 一份 aiohttp + asyncio 异步 HTTP 请求的速查笔记：从一个最小 get 示例出发，整理了自定义 Header/Cookie、URL 参数、POST 表单与文件上传、超时、代理、读取大响应流、连接池 TCPConnector 等常用写法。代码转自 xianhu 的 LearnPython 项目。

> **技术备注**
>
> aiohttp 3.x 写法至今通用，但注意 Python 3.10 起 `asyncio.get_event_loop()` 在无运行循环时会告警，推荐改用 `asyncio.run()`；aiohttp 3.9+ 中超时建议用 `aiohttp.ClientTimeout` 对象而不是裸数字。

---

转自：https://github.com/xianhu/LearnPython（原文链接已失效，这里补全为 GitHub 项目地址）

```python
# _*_ coding: utf-8 _*_

"""
python_aiohttp.py by xianhu
"""

import asyncio
import aiohttp

# 简单实例
async def aiohttp_test01(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            print(await resp.text())

loop = asyncio.get_event_loop()
tasks = [aiohttp_test01("https://api./events")]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

# 其他Http方法
# session.post('http://httpbin.org/post', data=b'data')
# session.put('http://httpbin.org/put', data=b'data')
# session.delete('http://httpbin.org/delete')
# session.head('http://httpbin.org/get')
# session.options('http://httpbin.org/get')
# session.patch('http://httpbin.org/patch', data=b'data')

# 自定义Headers
# payload = {'some': 'data'}
# headers = {'content-type': 'application/json'}
# await session.post(url, data=json.dumps(payload), headers=headers)

# 自定义Cookie
# cookies = {'cookies_are': 'working'}
# async with ClientSession(cookies=cookies) as session:
# 访问Cookie: session.cookie_jar

# 在URLs中传递参数
# 1. params = {'key1': 'value1', 'key2': 'value2'}
# 2. params = [('key', 'value1'), ('key', 'value2')]
# async with session.get('http://httpbin.org/get', params=params) as resp:
#     assert resp.url == 'http://httpbin.org/get?key2=value2&key1=value1'

# 发送数据
# payload = {'key1': 'value1', 'key2': 'value2'}
# async with session.post('http://httpbin.org/post', data=payload) as resp:
# async with session.post(url, data=json.dumps(payload)) as resp:
#     print(await resp.text())

# 发送文件(1)
# files = {'file': open('report.xls', 'rb')}
# await session.post(url, data=files)

# 发送数据(2)
# data = FormData()
# data.add_field('file',
#                open('report.xls', 'rb'),
#                filename='report.xls',
#                content_type='application/vnd.ms-excel')
# await session.post(url, data=data)

# 超时设置
# aync with session.get('https://', timeout=60) as r:

# 代理支持
# async with aiohttp.ClientSession() as session:
#     async with session.get("http://python.org", proxy="http://") as resp:
#         print(resp.status)

# async with aiohttp.ClientSession() as session:
#     proxy_auth = aiohttp.BasicAuth('user', 'pass')
#     async with session.get("http://python.org", proxy="http://", proxy_auth=proxy_auth) as resp:
#         print(resp.status)
# session.get("http://python.org", proxy="http://user:pass@")

# 返回的内容
# async with session.get('https://api./events') as resp:
#     print(await resp.text())
#     print(await resp.text(encoding='gbk'))
#     print(await resp.read())
#     print(await resp.json())

# 返回内容较大
# with open(filename, 'wb') as fd:
#     while True:
#         chunk = await resp.content.read(chunk_size)
#         if not chunk:
#             break
#         fd.write(chunk)

# 返回的其他变量
# async with session.get('http://httpbin.org/get') as resp:
#     print(resp.status)        # 状态码
#     print(resp.headers)       # Headers
#     print(resp.raw_headers)   # 原始Headers
#     print(resp.cookies)       # 返回的Cookie

# 访问历史History
# resp = await session.get('http://example.com/some/redirect/')
# resp: <ClientResponse(http://example.com/some/other/url/) [200]>
# resp.history: (<ClientResponse(http://example.com/some/redirect/) [301]>,)

# 释放返回的Response
# 1. async with session.get(url) as resp: pass
# 2. await resp.release()

# 连接器: Connectors
# conn = aiohttp.TCPConnector()
# session = aiohttp.ClientSession(connector=conn)

# 限制连接池大小:
# conn = aiohttp.TCPConnector(limit=30)
# conn = aiohttp.TCPConnector(limit=None)
```
