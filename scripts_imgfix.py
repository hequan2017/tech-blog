# -*- coding: utf-8 -*-
"""生成图片清单 manifest.json: 每张图的文章、上下文、当前 alt"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posts')
IMG_RE = re.compile(r'(!\[(.*?)\]\((assets/[^)]+)\))')

manifest = []
for f in sorted(os.listdir(POSTS)):
    if not f.endswith('.md'):
        continue
    p = os.path.join(POSTS, f)
    lines = open(p, encoding='utf-8').read().splitlines()
    for i, line in enumerate(lines):
        for mm in IMG_RE.finditer(line):
            ctx_before = lines[i-1].strip()[:60] if i > 0 else ''
            ctx_after = lines[i+1].strip()[:60] if i+1 < len(lines) else ''
            manifest.append({
                'file': f,
                'src': mm.group(3),
                'alt': mm.group(2),
                'ctx_before': ctx_before,
                'ctx_after': ctx_after,
            })

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_manifest.json')
json.dump(manifest, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'total refs: {len(manifest)}')
uniq = {m["src"] for m in manifest}
print(f'unique imgs: {len(uniq)}')
from collections import Counter
c = Counter(m['file'] for m in manifest)
print(f'articles: {len(c)}')
for k, v in c.most_common():
    print(f'  {v:3d}  {k}')
