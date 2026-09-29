# -*- coding: utf-8 -*-
# 一次性修复 2017-11-24-python 基础-2043852.md 的排版与被吃掉内容
import re
from pathlib import Path

P = r"D:\devops\test-2026\tech-blog\posts\2017-11-24-python 基础-2043852.md"
_P = Path(P).resolve()
_P.relative_to(Path(__file__).resolve().parents[2])
s = open(P, encoding='utf-8', newline='').read()
s = s.replace('\r\n', '\n').replace('\u00a0', ' ')

# 1) 还原被 51cto 编辑器吃掉的双下划线: **init** -> __init__ 等
s = re.sub(r'\*\*(\w+)\*\*', r'__\1__', s)

# 2) 头部: 原地址补全 github.com; 被吃掉的编码声明还原
s = s.replace('原地址：https:///xianhu/LearnPython/blob/master/python_base.py',
              '原地址：https://github.com/xianhu/LearnPython/blob/master/python_base.py')
s = s.replace('### *** coding: utf-8 ***',
              '源码首行为编码声明 `# -*- coding: utf-8 -*-`。')
s = s.replace('# *** coding: utf-8 ***\n', '# -*- coding: utf-8 -*-\n')

# 3) 十个 """X----X----""" 分隔注释 -> ## N. 标题 + python 代码块
names = ['类型和运算', '语法和语句', '函数语法规则', '函数例子', '模块Moudle',
         '类与面向对象', '类的高级话题', '异常相关', 'Unicode和字节字符串', '其他']
heads = ['类型和运算', '语法和语句', '函数语法规则', '函数例子:内置函数速查',
         '模块 Module', '类与面向对象', '类的高级话题', '异常相关',
         'Unicode 和字节字符串', '其他']
cnt = 0
out = []
for line in s.split('\n'):
    m = re.match(r'^"""(.+?)-{3,}.*"""$', line)
    if m and m.group(1) in names:
        idx = names.index(m.group(1))
        if idx == 0:
            out.append('## 1. ' + heads[0])
            out.append('')
            out.append('```python')
        else:
            out.append('```')
            out.append('')
            out.append('## %d. %s' % (idx + 1, heads[idx]))
            out.append('')
            out.append('```python')
        cnt += 1
    else:
        out.append(line)
s = '\n'.join(out)
assert cnt == 10, 'divider count = %d' % cnt

# 4) 去掉正文里原有的零散围栏(现已并入大代码块), 合并重复围栏
s = s.replace("```shell\nM.__dict__['name']\nsys.modules['M'].name\ngetattr(M, 'name')\n```",
              "M.__dict__['name']\nsys.modules['M'].name\ngetattr(M, 'name')")
s = s.replace('```python\n\n```python', '```python')      # 函数例子小节原有开栏
s = s.replace('```\n\n```\n\n##', '```\n\n##')            # 函数例子小节原有闭栏
# 文末补闭栏
s = s.rstrip('\n') + '\n```\n'

# 5) 明显笔误 / 被吃掉的内容(逐字替换)
fixes = [
    ('eval（expression)', 'eval' + '(expression)'),
    ('c = t – s;', 'c = t - s;'),
    ('S[len(S)–1]', 'S[len(S)-1]'),
    ('collections.defalutdict', 'collections.defaultdict'),
    ('# d导入包', '# 导入包'),
    ('# 这里实在原有列表的基础上', '# 这里是在原有列表的基础上'),
    ('D.keys()), D.items()', 'D.keys(), D.items()'),
    ('B = B"""', 'B = b"""'),
    ('def __getattr(self, attrname):', 'def __getattr__(self, attrname):'),
    ('L.extend(interable)', 'L.extend(iterable)'),
    ('yield i** 2', 'yield i ** 2'),
    ('name = "wang"\n\n"hong"                          # 多行，name = "wanghong"',
     'name = "wang" \\\n       "hong"                    # 多行，name = "wanghong"'),
    (" = 'qi', a.age = 9", "a.name = 'qi', a.age = 9"),
    ('\n= name\n', '\nself.name = name\n'),
    ('print("goodbey ", )', 'print("goodbye ", self.name)'),
    ("return ' = %s' % self.__name", "return 'name = %s' % self.__name"),
    ('# 返回  = tom', '# 返回 name = tom'),
    ('# 这里可以修改成功  = jeey', '# 这里可以修改成功 name = jeey'),
    ("= 'Michael'                  # 动态给实例绑定一个属性",
     "s.name = 'Michael'           # 动态给实例绑定一个属性"),
    ("self.parent = 'I'm the Parent.'", 'self.parent = "I\'m the Parent."'),
]
for old, new in fixes:
    if old not in s:
        print('MISS:', old[:50])
    s = s.replace(old, new)

# 6) 校验: 无残留 **xx**, 围栏成对
assert not re.search(r'\*\*\w+\*\*', s), 'leftover **xx**'
fences = [l for l in s.split('\n') if l.startswith('```')]
assert len(fences) % 2 == 0, 'unbalanced fences %d' % len(fences)

_P.write_text(s, encoding='utf-8', newline='\n')
print('OK, lines:', s.count('\n') + 1, 'fences:', len(fences))
