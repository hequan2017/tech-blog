# -*- coding: utf-8 -*-
"""围栏规范化(状态机版, 正确处理嵌套配对):
1. 删除空代码块 (``` ``` 之间无内容)
2. 解开误包进代码块的标题/说明文字 -> 恢复为正文
3. 给无语言标注的真代码块补语言标注 (保守: 拿不准不标)
用法: python scripts_fence.py [--apply] [文件名...]
"""
import os, re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(ROOT, 'posts')
APPLY = '--apply' in sys.argv

SHELL_HINT = re.compile(r'^\s*(\$ |yum |apt(-get)? |systemctl |kubectl |service |cd |mkdir |tar |wget |curl |rpm |ls\b|cat\b|grep |sed |awk |chmod |chown |useradd |echo |export |source |if \[ |for \[|while \[|fi\b|esac|then\b|#!/bin/(ba)?sh|->|^-)', re.M)
PY = re.compile(r'^\s*(def |class \w|import \w+|from \w+ import|print\(|if __name__)', re.M)
GO = re.compile(r'^\s*(package main|import \(|func \w|fmt\.)', re.M)
JS = re.compile(r'^\s*(const |let |var \w+ =|function |module\.exports|require\()', re.M)
SQL = re.compile(r'^\s*(SELECT |INSERT |UPDATE |DELETE |CREATE (TABLE|DATABASE|USER)|GRANT |SHOW |DROP |ALTER )', re.I | re.M)
DIFF = re.compile(r'^\s*(@@|diff --git|index \w+)', re.M)
DOCKER = re.compile(r'^\s*FROM ', re.M)
NGINX = re.compile(r'^\s*(server \{|location |proxy_pass|upstream \w+ \{)', re.M)

def classify(code):
    s = code.strip()
    if not s: return None
    if s[0] in '{[':
        try:
            json.loads(s); return 'json'
        except Exception: pass
    if DOCKER.search(code): return 'dockerfile'
    if PY.search(code) and not SHELL_HINT.search(code): return 'python'
    if GO.search(code): return 'go'
    if DIFF.search(code): return 'diff'
    if SQL.search(code): return 'sql'
    lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith('#')]
    if len(lines) >= 2:
        kv = sum(1 for l in lines if re.match(r'^\s*[\w./-]+\s*:\s', l) or re.match(r'^\s*-\s+\S', l))
        if kv / len(lines) > 0.7 and '<' not in code: return 'yaml'
    if re.match(r'^\s*\[[\w.-]+\]\s*$', s, re.M) and ini_ratio(code) > 0.5: return 'ini'
    if s.startswith('<') and re.search(r'<(\?xml|!DOCTYPE|html|config|beans|template|server)', code):
        return 'html' if re.search(r'<(div|span|p\b|table|h\d|script|body)', code) else 'xml'
    if NGINX.search(code): return 'nginx'
    if JS.search(code): return 'javascript'
    if SHELL_HINT.search(code): return 'shell'
    return None

def ini_ratio(code):
    lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith(('#', ';'))]
    if not lines: return 0
    return sum(1 for l in lines if re.match(r'^\s*[\w.-]+\s*=\s*\S', l)) / len(lines)

def prose_kind(block_lines):
    """标题/说明文字判定; 返回 'empty'|'heading'|'prose'|'code'"""
    content = [l for l in block_lines if l.strip()]
    if not content: return 'empty'
    if all(re.match(r'^#{1,6}\s+\S', l) for l in content): return 'heading'
    cn = 0
    for l in content:
        if re.search(r'[一-鿿]{4,}', l) and not re.search(r'[=;{}]|^\s*(\$|yum|apt|cd |ls|cat|echo|make|wget|curl|tar|pip|go |python|npm|docker|\./|>)', l):
            cn += 1
    if cn / len(content) >= 0.6 and len(content) <= 4:
        return 'prose'
    return 'code'

stats = {'empty': 0, 'unwrap': 0, 'tag': 0}
ONLY = [a for a in sys.argv[1:] if not a.startswith('--')]
for f in (ONLY if ONLY else sorted(os.listdir(POSTS))):
    if not f.endswith('.md'): continue
    p = os.path.join(POSTS, f)
    raw = open(p, encoding='utf-8', newline='').read()
    m = re.match(r'^---\r?\n[\s\S]*?\r?\n---\r?\n', raw)
    head, body = (raw[:m.end()], raw[m.end():]) if m else ('', raw)
    lines = body.split('\n')
    res = []
    changed = False
    i, n = 0, len(lines)
    in_fence = False       # 是否处于围栏内
    fence_lang = ''
    while i < n:
        line = lines[i].rstrip('\r')
        mm = re.match(r'^```(\S*)\s*$', line)
        if not in_fence:
            if mm:                     # 围栏开启
                in_fence, fence_lang = True, mm.group(1)
                fence_start = i
                i += 1
                continue
            res.append(lines[i]); i += 1
        else:
            if mm:                     # 围栏闭合
                block = [l.rstrip('\r') for l in lines[fence_start+1:i]]
                if fence_lang == '':
                    kind = prose_kind(block)
                    if kind == 'empty':
                        stats['empty'] += 1; changed = True
                    elif kind in ('heading', 'prose'):
                        stats['unwrap'] += 1; changed = True
                        res.append('')
                        res.extend(block)
                        res.append('')
                    else:
                        lang = classify('\n'.join(block))
                        if lang:
                            stats['tag'] += 1; changed = True
                            res.append('```' + lang)
                            res.extend(block)
                            res.append('```')
                        else:
                            res.append('```')
                            res.extend(block)
                            res.append('```')
                else:                  # 已有语言, 原样保留
                    res.append('```' + fence_lang)
                    res.extend(block)
                    res.append('```')
                in_fence = False
                i += 1
                continue
            i += 1                     # 围栏内容, 暂存
    if in_fence:                        # 未闭合围栏: 兜底原样输出
        res.extend(lines[fence_start:])
    if changed:
        new_body = re.sub(r'\n{3,}', '\n\n', '\n'.join(res))
        if APPLY:
            open(p, 'w', encoding='utf-8', newline='\n').write(head + new_body)
        else:
            print('DRY', f)
print(stats)
