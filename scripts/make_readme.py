# -*- coding: utf-8 -*-
"""根据 out/index.json 生成双语 README.md / README.en.md 及文章索引。"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = (Path(__file__).parent / "out").resolve()
REPO = OUT.parent / "repo"

TOTAL = 0


def load():
    global TOTAL
    index = json.loads((OUT / "index.json").read_text(encoding="utf-8"))
    TOTAL = len(index)
    return index


def year(art):
    d = art["date"][:10]
    return d[:4] if re.match(r"\d{4}-\d\d-\d\d", d) else "未知"


def title_zh(art):
    return f"[{art['title']}](posts/)"


def group(index):
    cats = defaultdict(lambda: defaultdict(list))
    for a in index:
        cats[a["category"] or "未分类"][year(a)].append(a)
    return cats


def index_table(index):
    lines = ["| 日期 | 标题 | 分类 |", "| --- | --- | --- |"]
    for a in sorted(index, key=lambda x: x["date"], reverse=True):
        lines.append(f"| {a['date'][:10]} | [{a['title']}]({a['file']}) "
                     f"| {a['category'] or '未分类'} |")
    return "\n".join(lines)


def write_index_md(index):
    per_year = defaultdict(list)
    for a in index:
        per_year[year(a)].append(a)
    parts = ["# 文章总索引(按年份)\n"]
    for y in sorted(per_year, reverse=True):
        parts.append(f"## {y} 年({len(per_year[y])} 篇)\n")
        parts.append("| 日期 | 标题 | 分类 |")
        parts.append("| --- | --- | --- |")
        for a in sorted(per_year[y], key=lambda x: x["date"], reverse=True):
            parts.append(f"| {a['date'][:10]} | [{a['title']}]({a['file']}) "
                         f"| {a['category'] or '未分类'} |")
        parts.append("")
    (REPO / "INDEX.md").write_text("\n".join(parts), encoding="utf-8")


def stats(index):
    cats = defaultdict(int)
    for a in index:
        cats[a["category"] or "未分类"] += 1
    y_min = min(year(a) for a in index)
    y_max = max(year(a) for a in index)
    return cats, y_min, y_max


def main():
    REPO.mkdir(exist_ok=True)
    index = load()
    cats, y_min, y_max = stats(index)
    cat_line = " · ".join(f"{c}({n})" for c, n in
                          sorted(cats.items(), key=lambda kv: -kv[1]))

    zh = f"""# 技术博客

> [hequan](https://blog.51cto.com/hequan) 的 51CTO 博客文章全集备份 · 共 **{TOTAL}** 篇({y_min}–{y_max})

本仓库将博主在 [51CTO 博客](https://blog.51cto.com/hequan) 发布的全部技术文章抓取并转换为 Markdown,
图片已本地化至 `posts/assets/`,可离线阅读、全文检索。每篇文章的 front-matter 保留原标题、发布时间、
分类与原文链接(`source`)。

## 分类概览

{cat_line}

## 目录

- [文章总索引(按年份)](INDEX.md)
- 所有文章位于 [`posts/`](posts/) 目录,文件名格式:`YYYY-MM-DD-标题-文章ID.md`

## 说明

- 抓取时间:{datetime.now().strftime('%Y-%m-%d')}
- 原文版权归博主所有,转载请注明 [原文出处](https://blog.51cto.com/hequan)
- 抓取工具:Python + BeautifulSoup,脚本见仓库历史
"""
    (REPO / "README.md").write_text(zh, encoding="utf-8")

    cat_line_en = " · ".join(f"{c}({n})" for c, n in
                             sorted(cats.items(), key=lambda kv: -kv[1]))
    en = f"""# Tech Blog

> Complete archive of [hequan](https://blog.51cto.com/hequan)'s blog posts on 51CTO · **{TOTAL}** articles ({y_min}–{y_max})

All articles were scraped from the author's [51CTO blog](https://blog.51cto.com/hequan) and converted to Markdown.
Images are localized under `posts/assets/` for offline reading and full-text search.
Each article keeps its original title, publish date, category and source URL in the front-matter.

## Categories

{cat_line_en}

## Contents

- [Full article index by year](INDEX.md)
- All posts live in [`posts/`](posts/), named `YYYY-MM-DD-title-postID.md`

## Notes

- Scraped on {datetime.now().strftime('%Y-%m-%d')}
- Copyright belongs to the author; cite the [original blog](https://blog.51cto.com/hequan) when reproducing
- Toolchain: Python + BeautifulSoup
"""
    (REPO / "README.en.md").write_text(en, encoding="utf-8")

    write_index_md(index)
    print(f"README.md / README.en.md / INDEX.md 生成完毕,共 {TOTAL} 篇")
    print("分类:", dict(sorted(cats.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main()
