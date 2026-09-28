---
title: "'Worker' object has no attribute '_config'"
date: "2018-01-22 13:45:49"
category: "ansible"
source: "https://blog.51cto.com/hequan/2063631"
---

celery  调用 ansbile api 报错

```python
  File "/usr/local/lib/python3.6/multiprocessing/synchronize.py", line 117, in _make_name
    return '%s-%s' % (process.current_process()._config['semprefix'],
AttributeError: 'Worker' object has no attribute '_config'
```

处理方法：

在任务里面加一句

```python
 from multiprocessing import current_process
 
 
@app.task
def  ansbile():

        current_process()._config = {'semprefix': '/mp'}
		
		print(123)
```
