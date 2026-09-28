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


def stats(index):
    cats = defaultdict(int)
    for a in index:
        cats[a["category"] or "未分类"] += 1
    y_min = min(year(a) for a in index)
    y_max = max(year(a) for a in index)
    return cats, y_min, y_max


def gh_anchor(text: str) -> str:
    """按 GitHub 标题锚点规则生成锚点:小写、去标点、空格转连字符。"""
    a = re.sub(r"[^\w\u4e00-\u9fff -]", "", text).strip().lower()
    return a.replace(" ", "-")


def cat_links(index):
    """生成可点击分类目录:点击直达 INDEX.md 对应分类段落。"""
    cats = defaultdict(int)
    for a in index:
        cats[a["category"] or "未分类"] += 1
    return [(c, n, f"[{c}({n})](INDEX.md#{gh_anchor(c + f'({n} 篇)')})")
            for c, n in sorted(cats.items(), key=lambda kv: -kv[1])]


def main():
    REPO.mkdir(exist_ok=True)
    index = load()
    cats, y_min, y_max = stats(index)
    cat_line = " · ".join(f"{c}({n})" for c, n in
                          sorted(cats.items(), key=lambda kv: -kv[1]))
    links = cat_links(index)
    toc_zh = " · ".join(l for _, _, l in links)
    toc_en = toc_zh  # 分类名源自博客本身,保持中文

    zh = f"""# 技术博客

> [hequan](https://blog.51cto.com/hequan) 的 51CTO 博客文章全集备份 · 共 **{TOTAL}** 篇({y_min}–{y_max})

本仓库将博主在 [51CTO 博客](https://blog.51cto.com/hequan) 发布的全部技术文章抓取并转换为 Markdown,
图片已本地化至 `posts/assets/`,可离线阅读、全文检索。每篇文章的 front-matter 保留原标题、发布时间、
分类与原文链接(`source`)。

## 目录(点击直达)

{toc_zh}

📖 完整目录:[INDEX.md](INDEX.md) — 分类×年份双视图 + 按年总表

所有文章位于 [`posts/`](posts/) 目录,文件名格式:`YYYY-MM-DD-标题-文章ID.md`

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

## Contents (clickable)

{toc_en}

📖 Full index: [INDEX.md](INDEX.md) — categories × years + yearly tables

All posts live in [`posts/`](posts/), named `YYYY-MM-DD-title-postID.md`

## Notes

- Scraped on {datetime.now().strftime('%Y-%m-%d')}
- Copyright belongs to the author; cite the [original blog](https://blog.51cto.com/hequan) when reproducing
- Toolchain: Python + BeautifulSoup
"""
    (REPO / "README.en.md").write_text(en, encoding="utf-8")

    print(f"README.md / README.en.md 生成完毕,共 {TOTAL} 篇")
    print("分类:", dict(sorted(cats.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main()
