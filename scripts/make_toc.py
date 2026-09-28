# -*- coding: utf-8 -*-
"""生成 repo/INDEX.md 完整目录:总览 + 分类导航 + 分类×年份文章列表 + 按年总表。"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8")
WORK = Path(__file__).parent.resolve()
OUT = WORK / "out"
REPO = WORK / "repo"


def link(path: str) -> str:
    """URL 编码路径,防标题中的空格/括号截断 Markdown 链接。"""
    return quote(path, safe="/-.")


def anchor(text: str) -> str:
    a = re.sub(r"[^\w\u4e00-\u9fff -]", "", text).strip().lower()
    return a.replace(" ", "-")


def main():
    index = json.loads((OUT / "index.json").read_text(encoding="utf-8"))
    total = len(index)

    years = defaultdict(int)
    for a in index:
        years[a["date"][:4]] += 1

    cats = defaultdict(lambda: defaultdict(list))
    for a in index:
        cats[a["category"] or "未分类"][a["date"][:4]].append(a)
    cat_counts = {c: sum(len(v) for v in ys.values()) for c, ys in cats.items()}

    parts = []
    parts.append(f"# 目录\n")
    parts.append(f"> 共 **{total}** 篇文章(2016–2025)· 抓取整理于 {datetime.now():%Y-%m-%d} "
                 f"· [← 返回首页](README.md)\n")

    # ---- 总览 ----
    parts.append("## 总览\n")
    parts.append("| 年份 | " + " | ".join(sorted(years)) + " | 合计 |")
    parts.append("| --- | " + " | ".join(["--- "] * len(years)) + "| --- |")
    parts.append("| 篇数 | " + " | ".join(str(years[y]) for y in sorted(years)) + f" | {total} |")
    parts.append("")
    parts.append("**分类导航:** " + " · ".join(
        f"[{c}](#{anchor(c)})({n})" for c, n in sorted(cat_counts.items(), key=lambda kv: -kv[1])))
    parts.append("")

    # ---- 分类目录 ----
    parts.append("## 分类目录\n")
    for cat in sorted(cat_counts, key=lambda c: (-cat_counts[c], c)):
        ymap = cats[cat]
        parts.append(f"### {cat}({cat_counts[cat]} 篇)\n")
        for y in sorted(ymap, reverse=True):
            parts.append(f"**{y} 年**\n")
            for a in sorted(ymap[y], key=lambda x: x["date"], reverse=True):
                parts.append(f"- {a['date'][5:10]} · [{a['title']}]({link(a['file'])})")
            parts.append("")
        parts.append("---\n")

    # ---- 按年份总表 ----
    parts.append("## 按年份总表\n")
    by_year = defaultdict(list)
    for a in index:
        by_year[a["date"][:4]].append(a)
    for y in sorted(by_year, reverse=True):
        parts.append(f"### {y} 年({len(by_year[y])} 篇)\n")
        parts.append("| 日期 | 标题 | 分类 |")
        parts.append("| --- | --- | --- |")
        for a in sorted(by_year[y], key=lambda x: x["date"], reverse=True):
            parts.append(f"| {a['date'][:10]} | [{a['title']}]({link(a['file'])}) | {a['category'] or '未分类'} |")
        parts.append("")

    (REPO / "INDEX.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"目录已生成: {REPO/'INDEX.md'} ({total} 篇, {len(cat_counts)} 分类)")


if __name__ == "__main__":
    main()
