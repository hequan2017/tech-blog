# -*- coding: utf-8 -*-
"""抓取 51CTO 博客(hequan)全部文章 → Markdown + 本地图片。

布局:out/posts/*.md,out/posts/assets/<文章id>/NN_图片名
图片链接为目录内向下的相对路径(assets/...),无父目录引用。
约束:仅允许 http/https;发请求前校验 host,拒绝解析到私有/保留地址的主机;
所有写盘路径 resolve 后校验在输出根目录内。
"""
import ipaddress
import json
import re
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

BLOG_USER = "hequan"
BASE = f"https://blog.51cto.com/{BLOG_USER}"
OUT = (Path(__file__).parent / "out").resolve()
POSTS_DIR = OUT / "posts"
ASSETS_DIR = POSTS_DIR / "assets"   # 图片根:posts/assets/<aid>/
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CURL = r"C:\Windows\System32\curl.exe"
sys.stdout.reconfigure(encoding="utf-8")

# ---------- host 校验(Mimosa 约束) ----------
_validated_hosts = set()


def validate_url(url: str) -> str:
    p = parse_url(url)
    if p.scheme not in ("http", "https"):
        raise ValueError(f"scheme not allowed: {p.scheme!r} in {url}")
    host = p.hostname
    if not host:
        raise ValueError(f"no host: {url}")
    if host in _validated_hosts:
        return url
    for info in socket.getaddrinfo(host, None):
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            raise ValueError(f"host {host} resolves to reserved addr {ip}")
    _validated_hosts.add(host)
    return url


def parse_url(url: str):
    from urllib.parse import urlparse
    return urlparse(url)


def curl_get(url: str, binary: bool = False, retries: int = 3):
    """经系统 curl 抓取(绕过 WAF 对 python TLS 指纹的拦截)。URL 已先过 validate_url。"""
    last = None
    for i in range(retries):
        try:
            proc = subprocess.run(
                [CURL, "-sL", "--compressed", "--max-time", "60",
                 "-A", UA, url],
                capture_output=True, timeout=90)
            data = proc.stdout
            if proc.returncode == 0 and data:
                if b"Security Verification" in data[:600]:
                    raise RuntimeError("WAF challenge page")
                return data if binary else data.decode("utf-8", errors="replace")
            last = RuntimeError(f"curl rc={proc.returncode} len={len(data)}")
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(1.0 + 0.5 * i)
    raise last


def fetch_text(url: str) -> str:
    validate_url(url)
    return curl_get(url)


def fetch_bytes(url: str) -> bytes:
    validate_url(url)
    return curl_get(url, binary=True)


def ensure_inside(root: Path, *parts: str) -> Path:
    """在 root 内拼接子路径,resolve 后校验未越界,防 URL 派生名逃逸。"""
    resolved = root.joinpath(*parts).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes output root: {parts}")
    return resolved


# ---------- 第一步:列表页收集文章 ID ----------
def collect_ids() -> list[int]:
    ids: list[int] = []
    no_new_rounds = 0
    page = 1
    while page <= 40 and no_new_rounds < 3:
        try:
            html = fetch_text(f"{BASE}?page={page}")
        except Exception as e:  # noqa: BLE001
            print(f"  page {page} 失败: {e}")
            no_new_rounds += 1
            page += 1
            continue
        found = [int(m) for m in re.findall(
            rf"blog\.51cto\.com/{BLOG_USER}/(\d{{5,}})", html)]
        new = [i for i in found if i not in ids]
        print(f"  page {page}: {len(found)} 链接, 新 {len(new)}")
        if not new:
            no_new_rounds += 1
        else:
            no_new_rounds = 0
            ids.extend(new)
        page += 1
        time.sleep(0.4)
    return sorted(set(ids), reverse=True)


# ---------- HTML → Markdown ----------
class Converter:
    def __init__(self, article_id: int):
        self.aid = article_id
        self.img_map: dict[str, str] = {}               # src -> markdown 链接
        self.img_tasks: list[tuple[str, Path, str]] = []  # (url, 写盘路径, 链接)

    def _register_img(self, el: Tag) -> str:
        src = (el.get("src") or el.get("data-src") or el.get("data-original")
               or "").strip()
        if not src or src.startswith("data:"):
            return ""
        if src.startswith("//"):
            src = "https:" + src
        if src not in self.img_map:
            p = parse_url(src)
            name = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(p.path).name) or "img"
            if "." not in name:
                name += ".png"
            fname = f"{len(self.img_map) + 1:02d}_{name[:60]}"
            target = ensure_inside(ASSETS_DIR, str(self.aid), fname)
            link = f"assets/{self.aid}/{fname}"   # 目录内向下的相对链接
            self.img_map[src] = link
            self.img_tasks.append((src, target, link))
        alt = (el.get("alt") or "").strip()
        return f"![{alt}]({self.img_map[src]})"

    def inline(self, node) -> str:
        if isinstance(node, NavigableString):
            return str(node)
        if not isinstance(node, Tag):
            return ""
        name = node.name
        if name in ("script", "style"):
            return ""
        if name == "br":
            return "\n"
        if name == "img":
            return self._register_img(node)
        inner = "".join(self.inline(c) for c in node.children)
        if name in ("strong", "b"):
            s = inner.strip()
            return f"**{s}**" if s else ""
        if name in ("em", "i"):
            s = inner.strip()
            return f"*{s}*" if s else ""
        if name == "code":
            t = node.get_text()
            return f"`{t}`" if t.strip() else ""
        if name == "a":
            href = (node.get("href") or "").strip()
            if href.startswith(("javascript:", "#")) or not href:
                return inner
            if href.startswith("//"):
                href = "https:" + href
            txt = inner.strip() or href
            return f"[{txt}]({href})"
        return inner

    def _pre_text(self, el: Tag) -> str:
        for br in el.find_all("br"):
            br.replace_with("\n")
        for p in el.find_all("p"):
            p.replace_with(NavigableString("\n" + p.get_text() + "\n"))
        return el.get_text().strip("\n")

    def _pre_lang(self, el: Tag) -> str:
        for node in [el] + el.find_all(True):
            for c in (node.get("class") or []):
                for pat in (r"language-([A-Za-z0-9+#]+)", r"brush:\s*([A-Za-z0-9+#]+)"):
                    m = re.search(pat, c)
                    if m:
                        return m.group(1).lower()
        return ""

    def blocks(self, node: Tag, depth: int = 0) -> list[str]:
        out: list[str] = []
        for child in node.children:
            if isinstance(child, NavigableString):
                t = str(child).strip()
                if t:
                    out.append(t)
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name
            if name in ("script", "style"):
                continue
            if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = min(int(name[1]) + 1, 6)  # 文章标题是 h1,正文从 ## 起
                out.append(f"{'#' * level} {self.inline(child).strip()}")
            elif name == "p":
                t = self.inline(child).strip()
                if t:
                    out.append(t)
            elif name in ("ul", "ol"):
                out.append(self._list(child, depth, name == "ol"))
            elif name == "pre":
                out.append(f"```{self._pre_lang(child)}\n{self._pre_text(child)}\n```")
            elif name == "blockquote":
                inner = "\n\n".join(self.blocks(child, depth))
                out.append("\n".join("> " + l for l in inner.splitlines()))
            elif name == "table":
                out.append(self._table(child))
            elif name == "hr":
                out.append("---")
            elif name == "figure":
                out.extend(self.blocks(child, depth))
            elif name in ("div", "section", "article", "main", "span"):
                out.extend(self.blocks(child, depth))
            else:
                t = self.inline(child).strip()
                if t:
                    out.append(t)
        return [b for b in out if b.strip()]

    def _list(self, el: Tag, depth: int, ordered: bool) -> str:
        lines = []
        idx = 0
        for li in el.find_all("li", recursive=False):
            idx += 1
            marker = f"{idx}. " if ordered else "- "
            texts, sublists = [], []
            for c in li.children:
                if isinstance(c, Tag) and c.name in ("ul", "ol"):
                    sublists.append(self._list(c, depth + 1, c.name == "ol"))
                else:
                    t = self.inline(c).strip()
                    if t:
                        texts.append(t)
            lines.append("  " * depth + marker + " ".join(texts))
            lines.extend(sublists)
        return "\n".join(lines)

    def _table(self, el: Tag) -> str:
        rows: list[list[str]] = []
        for tr in el.find_all("tr"):
            cells = [self.inline(c).strip().replace("|", "\\|").replace("\n", " ")
                     for c in tr.find_all(("td", "th"))]
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(r) for r in rows)
        for r in rows:
            r += [""] * (width - len(r))
        header, body = (rows[0], rows[1:]) if el.find("th") else ([""] * width, rows)
        md = ["| " + " | ".join(header) + " |",
              "|" + "|".join([" --- "] * width) + "|"]
        md += ["| " + " | ".join(r) + " |" for r in body]
        return "\n".join(md)


# ---------- 第二步:抓取单篇文章 ----------
def parse_article(aid: int) -> dict | None:
    r = fetch_text(f"{BASE}/{aid}")
    soup = BeautifulSoup(r, "html.parser")
    h1 = soup.find("h1")
    content = soup.select_one(".article-content-wrap")
    if not h1 or content is None:
        return None
    title = h1.get_text(strip=True)
    time_el = soup.find("time")
    pubdate = (time_el.get("pubdate") or time_el.get_text(strip=True)
               if time_el else "")
    category = ""
    for sp in soup.select(".messbox span"):
        if "博主文章分类" in sp.get_text():
            a = sp.find("a")
            category = a.get_text(strip=True) if a else ""
            break
    conv = Converter(aid)
    body = "\n\n".join(conv.blocks(content))
    body = re.sub(r"\n{3,}", "\n\n", body)
    return {
        "id": aid, "title": title, "date": pubdate.strip(),
        "category": category, "body": body,
        "images": conv.img_tasks, "url": f"{BASE}/{aid}",
    }


def dl_image(url: str, target: Path) -> bool:
    try:
        data = fetch_bytes(url)
        if not data:
            return False
        if "." not in target.name:
            target = target.with_suffix(".jpg")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return True
    except Exception:  # noqa: BLE001
        return False


def safe_title(title: str) -> str:
    t = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", title)
    t = re.sub(r"\s+", " ", t).strip().rstrip(".")
    return t[:70] or "untitled"


def main():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print("[1/3] 收集文章列表 ...")
    ids = collect_ids()
    print(f"共发现 {len(ids)} 篇文章")
    (OUT / "ids.json").write_text(json.dumps(ids), encoding="utf-8")
    index, skipped = [], []

    print("[2/3] 抓取文章 ...")
    done = 0

    def work(aid):
        try:
            return aid, parse_article(aid), None
        except Exception as e:  # noqa: BLE001
            return aid, None, str(e)

    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(work, aid) for aid in ids]
        for fut in as_completed(futs):
            aid, art, err = fut.result()
            done += 1
            if err or art is None:
                skipped.append({"id": aid, "reason": err or "无正文"})
                print(f"  [{done}/{len(ids)}] {aid} 跳过: {err or '无正文'}")
                continue
            fname = f"{art['date'][:10] or 'nodate'}-{safe_title(art['title'])}-{aid}.md"
            ok_imgs = 0
            for url, target, link in art["images"]:
                if dl_image(url, target):
                    ok_imgs += 1
                else:
                    # 下载失败 → Markdown 链接回退为原始外链
                    remote = url if url.startswith("http") else "https:" + url
                    art["body"] = art["body"].replace(f"]({link})", f"]({remote})")
            fm = (f'---\ntitle: "{art["title"].replace(chr(34), chr(39))}"\n'
                  f'date: "{art["date"]}"\n'
                  f'category: "{art["category"]}"\n'
                  f'source: "{art["url"]}"\n---\n\n')
            (POSTS_DIR / fname).write_text(fm + art["body"] + "\n",
                                           encoding="utf-8")
            index.append({**{k: art[k] for k in ("id", "title", "date", "category", "url")},
                          "file": f"posts/{fname}"})
            print(f"  [{done}/{len(ids)}] {art['date'][:10]} {art['title'][:40]} "
                  f"(图 {ok_imgs}/{len(art['images'])})")

    print(f"完成 {len(index)} 篇, 跳过 {len(skipped)} 篇")
    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "skipped.json").write_text(
        json.dumps(skipped, ensure_ascii=False), encoding="utf-8")
    print("[3/3] 输出目录:", OUT)


if __name__ == "__main__":
    main()
