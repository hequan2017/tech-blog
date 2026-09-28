# -*- coding: utf-8 -*-
"""统一优化 repo/posts/*.md 排版:

- 删除正文开头与 front-matter title 重复的加粗标题
- 清除残留空 HTML 标签、行尾空白、3+ 连续空行
- 标题/表格/代码块/列表前保证空行(GitHub 渲染需要)
- 连续多余的分隔线合并
front-matter 与代码块内部内容不动。
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WORK = Path(__file__).parent.resolve()
POSTS = WORK / "repo" / "posts"

FM_SPLIT = re.compile(r"\A---\n(.*?)\n---\n\n?", re.S)
TITLE_RE = re.compile(r'^title: "(.*)"$', re.M)

RE_EMPTY_TAG = re.compile(
    r"<(span|div|a|p)[^>]*>(\s|&nbsp;)*</\1>", re.I)
RE_TRAIL_WS = re.compile(r"[ \t]+$", re.M)
RE_BLANKS = re.compile(r"\n{3,}")

RE_HEADING = re.compile(r"#{1,6} ")
RE_LIST = re.compile(r"(?:[-*+] |\d+\. )")
RE_FENCE = re.compile(r"```")


def split_fm(text: str):
    m = FM_SPLIT.match(text)
    if not m:
        return "", text
    return m.group(0), text[m.end():]


def needs_blank_before(line: str, prev: str) -> bool:
    """块级行前一行非空且不属于同一块时需要补空行。"""
    if not prev or not prev.strip():
        return False
    if RE_FENCE.match(line):
        return True
    if RE_HEADING.match(line):
        return True
    if line.lstrip().startswith("|"):
        return not prev.lstrip().startswith("|")
    if RE_LIST.match(line):
        return not RE_LIST.match(prev)
    if line.startswith(">"):
        return not prev.startswith(">")
    return False


def optimize(body: str, title: str) -> str:
    # 去正文开头与 title 重复的标题块(**标题** / # 标题)
    body = body.lstrip("\n")
    first = body.split("\n", 1)
    head = first[0].strip()
    if head in (f"**{title}**", f"# {title}", title):
        body = first[1].lstrip("\n") if len(first) > 1 else ""

    # 按 ``` 代码围栏分段,只优化代码外文本
    segs = body.split("```")
    for i in range(0, len(segs), 2):  # 偶数段 = 代码外
        s = segs[i]
        s = RE_EMPTY_TAG.sub("", s)
        s = RE_TRAIL_WS.sub("", s)
        # 连续分隔线合并
        s = re.sub(r"(?:^---\s*\n){2,}", "---\n", s, flags=re.M)
        # 块级元素前补空行
        lines = s.split("\n")
        out = []
        for ln in lines:
            if out and needs_blank_before(ln, out[-1]):
                out.append("")
            out.append(ln)
        segs[i] = "\n".join(out)

    body = "```".join(segs)
    body = RE_BLANKS.sub("\n\n", body)
    return body.strip() + "\n"


def main():
    changed = same = 0
    for f in sorted(POSTS.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        fm, body = split_fm(raw)
        tm = TITLE_RE.search(fm)
        title = tm.group(1) if tm else ""
        new = optimize(body, title)
        if fm:
            new = fm + new
        if new != raw:
            f.write_text(new, encoding="utf-8")
            changed += 1
        else:
            same += 1
    print(f"排版优化: 变更 {changed} 篇, 无需变更 {same} 篇")


if __name__ == "__main__":
    main()
