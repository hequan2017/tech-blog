# -*- coding: utf-8 -*-
"""扫描 posts/en/*.md,生成 posts-en-index.json(basename -> 英文标题),并报告缺失/异常。
用法: python scripts/rebuild_en_index.py
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
EN = POSTS / "en"

FM = re.compile(
    r'^---\r?\ntitle: "(.*)"\r?\ndate: "(.*)"\r?\ncategory: "(.*)"\r?\n'
    r'source: "(.*)"\r?\nlang: "en"\r?\n---',
    re.S)


def main():
    zh = {p.name for p in POSTS.glob("*.md")}
    index = {}
    bad = []
    for f in sorted(EN.glob("*.md")):
        m = FM.match(f.read_text(encoding="utf-8"))
        if not m:
            bad.append(f"front-matter 异常(需 title/date/category/source/lang 顺序): {f.name}")
            continue
        title, date, cat, src = m.groups()
        if f.name not in zh:
            bad.append(f"无对应中文原文: {f.name}")
            continue
        zh_text = (POSTS / f.name).read_text(encoding="utf-8")
        zh_cat = re.search(r'^category: "(.*)"$', zh_text, re.M)
        if zh_cat and zh_cat.group(1) != cat:
            bad.append(f"category 与原文不一致: {f.name} ({cat} != {zh_cat.group(1)})")
        index[f.name] = title
    out = ROOT / "posts-en-index.json"
    out.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    missing = sorted(zh - set(index))
    print(f"英文版: {len(index)}/{len(zh)} 篇 -> {out.name}")
    for b in bad:
        print("WARN", b)
    if len(sys.argv) > 1 and sys.argv[1] == "--missing":
        for f in missing:
            print("MISS", f)


if __name__ == "__main__":
    main()
