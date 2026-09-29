# -*- coding: utf-8 -*-
"""精读提交前校验: 用法 python scripts_check_article.py <posts/*.md ...>"""
import re, sys

OK = True
for path in sys.argv[1:]:
    s = open(path, encoding='utf-8', newline='').read()
    probs = []
    if '\u00a0' in s:
        probs.append(f'NBSP x{s.count(chr(160))}')
    if re.search(r'^```shel\s*$', s, re.M):
        probs.append('broken ```shel fence')
    if re.search(r'^```shell\r?\nl\s*$', s, re.M):
        probs.append('stray l fragment after fence')
    fences = re.findall(r'^```.*$', s, re.M)
    if len(fences) % 2:
        probs.append(f'odd fences {len(fences)}')
    langs = [f[3:].strip() for f in fences]
    empty_open = sum(1 for i, l in enumerate(langs) if l == '' and i % 2 == 0)
    if empty_open:
        probs.append(f'{empty_open} fence(s) without language')
    if re.search(r'[ \t]+$', s, re.M):
        probs.append('trailing whitespace')
    if probs:
        OK = False
        print(f'FAIL {path}: ' + '; '.join(probs))
    else:
        print(f'OK   {path}')
sys.exit(0 if OK else 1)
