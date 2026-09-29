# -*- coding: utf-8 -*-
"""排版清理:
1. 解开包在失效 51cto 外链里的本地图片 [![alt](assets/..)](http://..) -> ![alt](assets/..)
2. 删除自引用的失效 51cto 图片/附件链接 [https://sN.51cto..](https://sN.51cto..)
3. 去除行尾空白
用法: python scripts_cleanup.py [--apply]  (默认 dry-run)
"""
import os, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(ROOT, 'posts')
ROOT_DIR = Path(ROOT).resolve()
APPLY = '--apply' in sys.argv

def safe_write(p, text):
    rp = Path(p).resolve()
    rp.relative_to(ROOT_DIR)
    rp.write_text(text, encoding='utf-8', newline='\n')

RE_UNWRAP = re.compile(r'\[(!\[[^\]]*\]\(assets/[^)]+\))\]\(https?://[^)\s]*51cto[^)\s]*\)')
RE_DEADPAIR = re.compile(r'\[?(https?://s\d\.51cto\.com/[^\]\s]*)\]\(\1\)?', re.S)
RE_TRAILWS = re.compile(r'[ \t]+$', re.M)

stats = {'unwrap': 0, 'deadpair': 0, 'trailws_files': 0}

targets = [os.path.join(POSTS, f) for f in os.listdir(POSTS) if f.endswith('.md')]
targets += [os.path.join(ROOT, x) for x in ('INDEX.md', 'README.md', 'README.en.md')]

for p in targets:
    raw = open(p, encoding='utf-8', newline='').read()
    orig = raw
    m = re.match(r'^---\r?\n[\s\S]*?\r?\n---\r?\n', raw)
    if m:  # front-matter 不动
        head, body = raw[:m.end()], raw[m.end():]
    else:
        head, body = '', raw

    n1 = len(RE_UNWRAP.findall(body))
    if n1:
        body = RE_UNWRAP.sub(r'\1', body)
        stats['unwrap'] += n1

    n2 = len(RE_DEADPAIR.findall(body))
    if n2:
        body = RE_DEADPAIR.sub('', body)
        stats['deadpair'] += n2
        # 清理行内只剩空白/多余空行
        body = re.sub(r'[ \t]{2,}\n', '\n', body)

    if RE_TRAILWS.search(body):
        body = RE_TRAILWS.sub('', body)
        stats['trailws_files'] += 1

    if body != orig[m.end():] if m else body != orig:
        out = head + body
        if APPLY:
            safe_write(p, out)
        print(('APPLY ' if APPLY else 'DRY   ') + os.path.relpath(p, ROOT))

print(stats)
