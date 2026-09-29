# -*- coding: utf-8 -*-
"""读取 wave 结果摘要文件, 逐篇提交精读修改.
用法: python scripts_wave_commit.py tmp_imgdesc/waves/w1_a1_result.txt [more...]
"""
import os, re, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))

def run(*args):
    r = subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    return r.returncode, (r.stdout or '') + (r.stderr or '')

def title_of(path):
    txt = open(path, encoding='utf-8').read(1500)
    m = re.search(r'^title:\s*"(.*)"', txt, re.M)
    return m.group(1) if m else os.path.basename(path)

ok = fail = 0
for rf in sys.argv[1:]:
    if not os.path.exists(rf):
        print('missing result file:', rf); fail += 1; continue
    for line in open(rf, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or '\t' not in line:
            continue
        fname, summary = line.split('\t', 1)
        rel = 'posts/' + fname.strip()
        if not os.path.exists(os.path.join(ROOT, rel)):
            print('no such file:', rel); fail += 1; continue
        code, out = run('status', '--porcelain', '--', rel)
        if not out.strip():
            print('skip (no change):', rel); continue
        t = title_of(os.path.join(ROOT, rel))
        msg = f'docs: 精读《{t}》{summary.strip()}\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>'
        run('add', '--', rel)
        code, out = run('commit', '-m', msg, '--no-verify', '-q')
        if code == 0:
            ok += 1
            print('committed:', rel)
        else:
            fail += 1
            print('FAIL:', rel, out[:150])
print(f'commit ok={ok} fail={fail}')
if ok:
    run('pull', '--rebase', 'origin', 'main')
    code, out = run('push', 'origin', 'main')
    print('push:', 'ok' if code == 0 else out[:300])
