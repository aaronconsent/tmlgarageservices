#!/usr/bin/env python3
"""Remove duplicated injected blocks.

Some generators append a block without first removing the one they added on a
previous run, so re-running them stacked identical sections on the page. The
service pages ended up with three identical "Need this fixed today?" CTA bands.

Keeps the LAST occurrence of each duplicated block (it sits in the intended
position at the end of the page) and drops the earlier copies.

Run after the page generators. Idempotent.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent / "site"

# opening tag of the wrapper that should appear at most once per page
BLOCKS = [
    (r'<div class="sp"><div class="sp-wrap"><div class="sp-final">', 'closing CTA band'),
]


def block_end(html, open_end, depth):
    """End index (exclusive) of a run of `depth` nested divs opened at open_end."""
    for m in re.finditer(r"<div\b|</div>", html[open_end:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return open_end + m.end()
    return None


def dedupe(html):
    removed = 0
    for pattern, _ in BLOCKS:
        while True:
            spans = []
            for m in re.finditer(pattern, html):
                depth = len(re.findall(r"<div\b", m.group(0)))
                end = block_end(html, m.end(), depth)
                if end:
                    spans.append((m.start(), end))
            if len(spans) < 2:
                break
            start, end = spans[0]          # keep the last, drop the earliest
            html = html[:start] + html[end:]
            removed += 1
    return html, removed


def main():
    pages = total = 0
    for page in sorted(SITE.rglob("index.html")):
        html = page.read_text("utf-8", errors="replace")
        new, removed = dedupe(html)
        if removed:
            page.write_text(new, "utf-8")
            pages += 1
            total += removed
            print(f"  removed {removed} duplicate block(s): {page.relative_to(SITE)}")
    print(f"pages cleaned: {pages}, blocks removed: {total}")


if __name__ == "__main__":
    main()
