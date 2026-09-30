# -*- coding: utf-8 -*-
"""全量体检: 检查 posts/*.md 的结构性问题"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

POSTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'posts')

issues = {
    'no_frontmatter': [],      # 缺 front-matter
    'no_intro': [],            # 缺 内容介绍 头
    'unclosed_fence': [],      # 未闭合代码块
    'broken_img': [],          # 引用不存在的本地图片
    'dead_img_link': [],       # 图片外层包着 51cto 死链
    'filename_alt': [],        # alt 是无意义文件名哈希
    'empty_alt': [],           # alt 为空
    'html_junk': [],           # 残留脏 HTML (&nbsp; <br> 等)
    'raw_url_junk': [],        # 成对的裸 URL 残留
    'no_title': [],            # front-matter 缺 title
    'no_source': [],           # 缺原文链接
    'trailing_ws': [],         # 行尾空白
}

IMG_RE = re.compile(r'(!\[(.*?)\]\(([^)]+)\))')
LINK_IMG_RE = re.compile(r'\[!\[(.*?)\]\([^)]+\)\]\((https?://[^)]*51cto[^)]*)\)')


def strip_fences(text):
    """去掉代码围栏内容: 围栏内的 &nbsp;/&#12288; 等是教学示例, 不算脏 HTML"""
    out, in_fence = [], False
    for ln in text.split('\n'):
        if ln.startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(ln)
    return '\n'.join(out)

for f in sorted(os.listdir(POSTS)):
    if not f.endswith('.md'):
        continue
    p = os.path.join(POSTS, f)
    raw = open(p, encoding='utf-8').read()
    m = re.match(r'^---\r?\n([\s\S]*?)\r?\n---\r?\n', raw)
    if not m:
        issues['no_frontmatter'].append(f)
        continue
    fm, body = m.group(1), raw[m.end():]

    if not re.search(r'^title:', fm, re.M):
        issues['no_title'].append(f)
    if not re.search(r'^source:', fm, re.M):
        issues['no_source'].append(f)
    if '**内容介绍**' not in body:
        issues['no_intro'].append(f)

    # 代码块闭合
    fence_count = len(re.findall(r'^```', body, re.M))
    if fence_count % 2 != 0:
        issues['unclosed_fence'].append(f)

    # 图片
    for mm in IMG_RE.finditer(body):
        alt, src = mm.group(2), mm.group(3)
        if src.startswith('assets/'):
            if not os.path.exists(os.path.join(POSTS, src)):
                issues['broken_img'].append(f'{f} -> {src}')
        if alt == '':
            issues['empty_alt'].append(f'{f} -> {src}')
        elif re.match(r'^wKio', alt) or re.match(r'^[0-9A-F]{32}', alt):
            issues['filename_alt'].append(f'{f} -> {src}')

    if LINK_IMG_RE.search(body):
        issues['dead_img_link'].append(f)

    # 脏 HTML (仅查围栏外正文)
    body_nofence = strip_fences(body)
    if re.search(r'&nbsp;|<br\s*/?>\s*$|&#\d+;', body_nofence):
        issues['html_junk'].append(f)
    # 裸 URL 成对残留 (51cto 抓取常见)
    if re.search(r'\[https?://s\d\.51cto[^\]]*\]\(https?://', body_nofence):
        issues['raw_url_junk'].append(f)

    if re.search(r'[ \t]+$', body, re.M):
        issues['trailing_ws'].append(f)

for k, v in issues.items():
    print(f'== {k}: {len(v)}')
    for x in v[:8]:
        print(f'   {x}')
    if len(v) > 8:
        print(f'   ... 共 {len(v)}')
