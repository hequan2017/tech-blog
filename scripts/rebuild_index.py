# -*- coding: utf-8 -*-
"""从 out/posts/*.md 的 front-matter 重建 index.json,并对照 ids.json 找出缺失文章。"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = (Path(__file__).parent / "out").resolve()
POSTS = OUT / "posts"

FM = re.compile(
    r'^---\ntitle: "(.*)"\ndate: "(.*)"\ncategory: "(.*)"\nsource: "https://blog\.51cto\.com/hequan/(\d+)"\n---',
    re.S)


def main():
    index = []
    for f in sorted(POSTS.glob("*.md")):
        m = FM.match(f.read_text(encoding="utf-8"))
        if not m:
            print("front-matter 异常:", f.name)
            continue
        title, date, cat, aid = m.groups()
        index.append({"id": int(aid), "title": title, "date": date,
                      "category": cat,
                      "url": f"https://blog.51cto.com/hequan/{aid}",
                      "file": f"posts/{f.name}"})
    index.sort(key=lambda a: a["id"], reverse=True)
    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

    ids = set(json.loads((OUT / "ids.json").read_text()))
    have = {a["id"] for a in index}
    missing = sorted(ids - have, reverse=True)
    (OUT / "missing.json").write_text(json.dumps(missing), encoding="utf-8")
    print(f"索引重建: {len(index)} 篇; 列表页发现 {len(ids)} 篇; 缺失 {len(missing)} 篇")
    print("缺失样例:", missing[:15])


if __name__ == "__main__":
    main()
