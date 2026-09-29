---
title: "'Worker' object has no attribute '_config'"
date: "2018-01-22 13:45:49"
category: "ansible"
source: "https://blog.51cto.com/hequan/2063631"
lang: "en"
---
> **About this post**
>
> How to fix the `AttributeError: 'Worker' object has no attribute '_config'` raised when calling the Ansible API inside a Celery task: Celery's billiard process is not a standard multiprocessing.Process and lacks the `_config` attribute, while Ansible internally calls `multiprocessing.current_process()._config['semprefix']` to build semaphore names, which causes the crash. The workaround is to assign `_config` manually inside the task function.

> **Technical notes**
>
> This is a compatibility issue from the Celery 3.x + Ansible 2.4 era; the root cause is the behavioral difference between billiard and multiprocessing. With Celery 4+, the officially recommended approach is to avoid relying on multiprocessing private attributes in workers, and Ansible 2.9+ switched to ansible_runner, so this problem no longer occurs. Python 3.6 is already EOL.

---

Error when calling the Ansible API from Celery

```python
  File "/usr/local/lib/python3.6/multiprocessing/synchronize.py", line 117, in _make_name
    return '%s-%s' % (process.current_process()._config['semprefix'],
AttributeError: 'Worker' object has no attribute '_config'
```

How to fix it:

Add one line inside the task

```python
 from multiprocessing import current_process


@app.task
def  ansible_task():

        current_process()._config = {'semprefix': '/mp'}

        print(123)
```
