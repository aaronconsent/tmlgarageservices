#!/usr/bin/env python3
"""Extract structured content from the mirrored legacy pages -> content.json

Per page: path, title, meta description, og image, h1, and an ordered list of
content blocks (headings, paragraphs, list items, images) from the main body,
so the redesign re-renders identical copy without hand-transcription.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent / "site"
SKIP_DIRS = {"assets", "new"}

class Extractor(HTMLParser):
    BLOCK_TAGS = {"h1", "h2", "h3", "h4", "h5", "p", "li", "blockquote", "figcaption"}
    SKIP_TAGS = {"script", "style", "nav", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.stack = []
        self.buf = None
        self.cur_tag = None
        self.skip_depth = 0
        self.in_footer = 0
        self.title = ""
        self.in_title = False
        self.meta = {}
        self.images = []

    VOID = {"img", "br", "meta", "link", "input", "hr", "source", "embed", "area", "col", "wbr"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if self.skip_depth:
            if tag not in self.VOID:
                self.skip_depth += 1
            return
        if tag in self.SKIP_TAGS or "w-nav" in cls.split() or "navbar" in cls or "footer" in cls or "cookie" in cls:
            if tag not in self.VOID:
                self.skip_depth = 1
            return
        if tag == "title":
            self.in_title = True
        if tag == "meta" and a.get("name") in ("description",):
            self.meta["description"] = a.get("content", "")
        if tag == "meta" and a.get("property") == "og:image":
            self.meta["og_image"] = a.get("content", "")
        if tag == "img":
            src = a.get("src", "")
            if src.startswith("/assets/") and "icon" not in src.lower() and "logo" not in src.lower():
                self.images.append({"src": src, "alt": a.get("alt", ""), "srcset": a.get("srcset", "")})
                self.blocks.append({"t": "img", "src": src, "alt": a.get("alt", "")})
        if tag == "a" and self.buf is not None:
            href = a.get("href", "")
            if href.startswith("/"):
                self.buf.append(f"[[{href}|")
                self.stack.append("a")
                return
        if tag in self.BLOCK_TAGS and self.buf is None:
            self.cur_tag = tag
            self.buf = []

    def handle_endtag(self, tag):
        a_open = self.stack and self.stack[-1] == "a"
        if tag == "a" and a_open and self.buf is not None:
            self.buf.append("]]")
            self.stack.pop()
            return
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "title":
            self.in_title = False
        if tag == self.cur_tag and self.buf is not None:
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if text:
                self.blocks.append({"t": tag, "x": text})
            self.buf = None
            self.cur_tag = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.skip_depth:
            return
        if self.buf is not None:
            self.buf.append(data)

pages = {}
for f in sorted(ROOT.rglob("index.html")):
    rel = f.parent.relative_to(ROOT)
    if rel.parts and rel.parts[0] in SKIP_DIRS:
        continue
    path = "/" if str(rel) == "." else "/" + str(rel)
    ex = Extractor()
    ex.feed(f.read_text("utf-8", errors="replace"))
    pages[path] = {
        "title": ex.title.strip(),
        "meta": ex.meta,
        "blocks": ex.blocks,
        "images": ex.images,
    }

out = Path(__file__).parent / "content.json"
out.write_text(json.dumps(pages, indent=1), "utf-8")
print(f"{len(pages)} pages -> {out}")
for p, d in pages.items():
    h1 = next((b["x"] for b in d["blocks"] if b["t"] == "h1"), "-")
    print(f"  {p}  h1={h1[:60]!r}  blocks={len(d['blocks'])}")
