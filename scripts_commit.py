# -*- coding: utf-8 -*-
"""逐篇提交修改过的 posts/*.md"""
import os, subprocess, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(REPO, 'posts')

def run(*args):
    r = subprocess.run(['git'] + list(args), cwd=REPO,
                       capture_output=True, text=True, encoding='utf-8')
    return r.returncode, (r.stdout or '') + (r.stderr or '')

def title_of(path):
    txt = open(path, encoding='utf-8').read(1500)
    m = re.search(r'^title:\s*"(.*)"', txt, re.M)
    return m.group(1) if m else os.path.basename(path)

def main():
    files = sorted(f for f in os.listdir(POSTS) if f.endswith('.md'))
    total = len(files)
    ok, skip, fail = 0, 0, 0
    for i, f in enumerate(files, 1):
        rel = 'posts/' + f
        # 只提交有变更的文件
        code, out = run('status', '--porcelain', '--', rel)
        if not out.strip():
            skip += 1
            continue
        t = title_of(os.path.join(POSTS, f))
        run('add', '--', rel)
        msg = f'docs: 补充《{t}》内容介绍与技术备注'
        code, out = run('commit', '-m', msg, '--no-verify')
        if code == 0:
            ok += 1
        else:
            fail += 1
            print(f'[{i}/{total}] FAIL {f}: {out[:200]}')
        if i % 50 == 0:
            print(f'progress {i}/{total} ok={ok} skip={skip} fail={fail}')
    print(f'DONE ok={ok} skip={skip} fail={fail}')

if __name__ == '__main__':
    main()
