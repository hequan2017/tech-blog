# -*- coding: utf-8 -*-
"""清洗 posts/*.md 中的模板噪声,组装 repo/ 目录(README + posts)。"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WORK = Path(__file__).parent.resolve()
OUT = WORK / "out"
POSTS = OUT / "posts"
REPO = WORK / "repo"

NOISE_PATTERNS = [
    r"<span>本文包含：</span>\s*",
    r"<a href=\"\" target=\"_blank\"></a>\s*",
    r"<div[^>]*>\s*</div>\s*",
    r"\n{3,}",
]


def clean(text: str) -> str:
    # 去掉正文尾部 "本文包含" 附件块
    text = re.sub(r"<span>本文包含：</span>.*$", "", text, flags=re.S)
    for pat in NOISE_PATTERNS[:-1]:
        text = re.sub(pat, "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main():
    if REPO.exists():
        shutil.rmtree(REPO)
    REPO.mkdir(parents=True)
    dst_posts = REPO / "posts"
    dst_posts.mkdir()

    n = 0
    for f in sorted(POSTS.glob("*.md")):
        (dst_posts / f.name).write_text(clean(f.read_text(encoding="utf-8")),
                                        encoding="utf-8")
        n += 1
    # 图片资产
    shutil.copytree(POSTS / "assets", dst_posts / "assets")
    imgs = sum(1 for _ in (dst_posts / "assets").rglob("*.*"))
    print(f"组装完成: {n} 篇文章, {imgs} 张图片 → {REPO}")


if __name__ == "__main__":
    main()
