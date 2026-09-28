# -*- coding: utf-8 -*-
"""把 tmp_imgdesc/result_*.txt 中的图片描述写回 posts/*.md 的 alt 文本.
result 行格式: src<TAB>描述
"""
import os, re, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(ROOT, 'posts')

mapping = {}
for rf in sorted(glob.glob(os.path.join(ROOT, 'tmp_imgdesc', 'result_*.txt'))):
    for line in open(rf, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or '\t' not in line:
            continue
        src, desc = line.split('\t', 1)
        mapping[src.strip()] = desc.strip()

print(f'mapping entries: {len(mapping)}')

changed = 0
for f in sorted(os.listdir(POSTS)):
    if not f.endswith('.md'):
        continue
    p = os.path.join(POSTS, f)
    raw = open(p, encoding='utf-8', newline='').read()
    m = re.match(r'^---\r?\n[\s\S]*?\r?\n---\r?\n', raw)
    head, body = (raw[:m.end()], raw[m.end():]) if m else ('', raw)

    def repl(mm):
        alt, src = mm.group(1), mm.group(2)
        new = mapping.get(src)
        if not new or new == alt:
            return mm.group(0)
        return f'![{new}]({src})'

    new_body = re.sub(r'!\[([^\]]*)\]\((assets/[^)]+)\)', repl, body)
    if new_body != body:
        open(p, 'w', encoding='utf-8', newline='\n').write(head + new_body)
        changed += 1
        print(f'updated {f}')

print(f'files updated: {changed}')
