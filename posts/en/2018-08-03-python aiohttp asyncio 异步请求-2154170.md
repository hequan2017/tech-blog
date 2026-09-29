---
title: "Python Async HTTP Requests with aiohttp and asyncio"
date: "2018-08-03 16:40:39"
category: "python"
source: "https://blog.51cto.com/hequan/2154170"
lang: "en"
---
> **About this post**
>
> A quick-reference cheat sheet for async HTTP requests with aiohttp + asyncio: starting from a minimal GET example, it collects common recipes for custom Headers/Cookies, URL parameters, POST forms and file uploads, timeouts, proxies, streaming large responses, and the TCPConnector connection pool. Code adapted from xianhu's LearnPython project.

> **Technical notes**
>
> The aiohttp 3.x style shown here still works today, but note that since Python 3.10, `asyncio.get_event_loop()` emits a warning when there is no running loop — prefer `asyncio.run()` instead; in aiohttp 3.9+, pass timeouts as an `aiohttp.ClientTimeout` object rather than a bare number.

---

Adapted from: https://github.com/xianhu/LearnPython (the original link is dead; it has been replaced with the GitHub project URL here)

```python
# _*_ coding: utf-8 _*_

"""
python_aiohttp.py by xianhu
"""

import asyncio
import aiohttp

# Simple example
async def aiohttp_test01(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            print(await resp.text())

loop = asyncio.get_event_loop()
tasks = [aiohttp_test01("https://api./events")]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

# Other HTTP methods
# session.post('http://httpbin.org/post', data=b'data')
# session.put('http://httpbin.org/put', data=b'data')
# session.delete('http://httpbin.org/delete')
# session.head('http://httpbin.org/get')
# session.options('http://httpbin.org/get')
# session.patch('http://httpbin.org/patch', data=b'data')

# Custom headers
# payload = {'some': 'data'}
# headers = {'content-type': 'application/json'}
# await session.post(url, data=json.dumps(payload), headers=headers)

# Custom cookies
# cookies = {'cookies_are': 'working'}
# async with ClientSession(cookies=cookies) as session:
# Access cookies: session.cookie_jar

# Passing parameters in URLs
# 1. params = {'key1': 'value1', 'key2': 'value2'}
# 2. params = [('key', 'value1'), ('key', 'value2')]
# async with session.get('http://httpbin.org/get', params=params) as resp:
#     assert resp.url == 'http://httpbin.org/get?key2=value2&key1=value1'

# Sending data
# payload = {'key1': 'value1', 'key2': 'value2'}
# async with session.post('http://httpbin.org/post', data=payload) as resp:
# async with session.post(url, data=json.dumps(payload)) as resp:
#     print(await resp.text())

# Sending files (1)
# files = {'file': open('report.xls', 'rb')}
# await session.post(url, data=files)

# Sending data (2)
# data = FormData()
# data.add_field('file',
#                open('report.xls', 'rb'),
#                filename='report.xls',
#                content_type='application/vnd.ms-excel')
# await session.post(url, data=data)

# Timeout settings
# aync with session.get('https://', timeout=60) as r:

# Proxy support
# async with aiohttp.ClientSession() as session:
#     async with session.get("http://python.org", proxy="http://") as resp:
#         print(resp.status)

# async with aiohttp.ClientSession() as session:
#     proxy_auth = aiohttp.BasicAuth('user', 'pass')
#     async with session.get("http://python.org", proxy="http://", proxy_auth=proxy_auth) as resp:
#         print(resp.status)
# session.get("http://python.org", proxy="http://user:pass@")

# Response content
# async with session.get('https://api./events') as resp:
#     print(await resp.text())
#     print(await resp.text(encoding='gbk'))
#     print(await resp.read())
#     print(await resp.json())

# Large responses
# with open(filename, 'wb') as fd:
#     while True:
#         chunk = await resp.content.read(chunk_size)
#         if not chunk:
#             break
#         fd.write(chunk)

# Other response attributes
# async with session.get('http://httpbin.org/get') as resp:
#     print(resp.status)        # status code
#     print(resp.headers)       # Headers
#     print(resp.raw_headers)   # raw headers
#     print(resp.cookies)       # response cookies

# Accessing history
# resp = await session.get('http://example.com/some/redirect/')
# resp: <ClientResponse(http://example.com/some/other/url/) [200]>
# resp.history: (<ClientResponse(http://example.com/some/redirect/) [301]>,)

# Releasing the response
# 1. async with session.get(url) as resp: pass
# 2. await resp.release()

# Connectors
# conn = aiohttp.TCPConnector()
# session = aiohttp.ClientSession(connector=conn)

# Limiting the connection pool size:
# conn = aiohttp.TCPConnector(limit=30)
# conn = aiohttp.TCPConnector(limit=None)
```
