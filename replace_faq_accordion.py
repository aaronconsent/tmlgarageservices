#!/usr/bin/env python3
"""Make the black FAQ accordions actually open.

These four items on the home page and About page are Webflow dropdowns whose
open/close is driven by a Webflow interaction. That interaction does not survive
the static export: clicking a question does nothing, and the panel is pinned at
height:0. So four answers have been sitting on the page unreadable — this is true
of the untouched mirror too, not something the rebuild introduced.

They become native <details>/<summary>, which open with no JavaScript at all,
work from the keyboard, and are searchable by the browser's find-on-page.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmlacc-css">
.tmlacc{border-top:1px solid rgba(255,255,255,.2);}
.tmlacc summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:16px;
 padding:18px 0;min-height:56px;}
.tmlacc summary::-webkit-details-marker{display:none;}
.tmlacc summary h4{margin:0;color:#fff;flex:1 1 auto;}
.tmlacc summary::after{content:"";flex:0 0 auto;width:14px;height:14px;
 border-right:2px solid #cfe84d;border-bottom:2px solid #cfe84d;
 transform:rotate(45deg);margin-top:-6px;transition:transform .18s ease;}
.tmlacc[open] summary::after{transform:rotate(225deg);margin-top:4px;}
.tmlacc summary:focus-visible{outline:2px solid #cfe84d;outline-offset:2px;}
.tmlacc .faq-ans{padding:0 0 20px;}
.tmlacc .faq-ans p{margin:0;color:#c9d0bd;line-height:1.6;}
@media(prefers-reduced-motion:reduce){.tmlacc summary::after{transition:none;}}
</style>"""

BLOCK = re.compile(
    r'<div[^>]*class="faq-black w-dropdown"[^>]*>\s*'
    r'<div class="que-block w-dropdown-toggle">\s*(?P<q><h4[^>]*>.*?</h4>).*?</div>\s*'
    r'<nav[^>]*class="ans-block w-dropdown-list">(?P<a>.*?)</nav>\s*</div>', re.S)


def convert(html):
    made = 0

    def one(m):
        nonlocal made
        made += 1
        return (f'<details class="tmlacc"><summary>{m.group("q")}</summary>'
                f'{m.group("a")}</details>')

    return BLOCK.sub(one, html), made


def main():
    pages = total = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "faq-black w-dropdown" not in html:
            continue
        html, n = convert(html)
        if not n:
            continue
        html = re.sub(r'<style id="tmlacc-css">.*?</style>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            total += n
            print(f"  {f.relative_to(F)}: {n} answers now openable")
    print(f"pages changed: {pages}, accordions converted: {total}")


if __name__ == "__main__":
    main()
