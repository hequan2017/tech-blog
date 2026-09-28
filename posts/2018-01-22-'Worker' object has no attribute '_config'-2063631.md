---
title: "'Worker' object has no attribute '_config'"
date: "2018-01-22 13:45:49"
category: "ansible"
source: "https://blog.51cto.com/hequan/2063631"
---
> **内容介绍**
>
> 在 Celery 任务里调用 Ansible API 时报 `AttributeError: 'Worker' object has no attribute '_config'` 的解决方法：这是因为 Celery 的 billiard 进程不是标准 multiprocessing.Process，缺少 `_config` 属性，而 Ansible 内部用 `multiprocessing.current_process()._config['semprefix']` 生成信号量名导致崩溃。规避方式是在任务函数里手动给 `_config` 赋值。

> **技术备注**
>
> 这是 Celery 3.x + Ansible 2.4 时代的兼容问题，根因是 billiard 与 multiprocessing 的行为差异。Celery 4+ 后官方推荐的写法是避免在 worker 中依赖 multiprocessing 私有属性；Ansible 2.9+ 改用 ansible_runner 已不会再触发该问题。Python 3.6 已 EOL。

---

celery  调用 ansible api 报错

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
def  ansible_task():

        current_process()._config = {'semprefix': '/mp'}

        print(123)
```
