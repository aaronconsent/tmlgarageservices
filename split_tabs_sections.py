#!/usr/bin/env python3
"""Unpack the Webflow tabs widget into plain, fully-visible sections.

On the homepage this widget hid half the section behind a tab: "Why Choose TML
Garage Door Services?" was shown and "What You Can Expect From TML" — the eight
promises, the strongest trust content on the page — was invisible until clicked.
Both tab labels were <p> elements, so they read as paragraphs rather than
controls, and nothing suggested there was more behind them.

Each tab becomes its own headed section with its content on the page. Nothing is
added or reworded; content that was hidden is simply shown.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmltabs-css">
.tmltab-sec{margin:0 0 clamp(26px,3.6vw,40px);}
.tmltab-sec:last-child{margin-bottom:0;}
.tmltab-h{font-size:clamp(19px,2.3vw,24px);line-height:1.15;margin:0 0 12px;color:#1f2418;}
.tmltab-sec p{font-size:16.5px;line-height:1.62;color:#535c48;margin:0 0 14px;max-width:68ch;}
.tmltab-sec p:last-child{margin-bottom:0;}
.tmltab-list{list-style:none;margin:0;padding:0;display:grid;gap:11px;grid-template-columns:1fr;}
.tmltab-list li{display:flex;gap:11px;align-items:flex-start;margin:0;}
.tmltab-list li p{margin:0;font-size:15.5px;line-height:1.5;color:#535c48;max-width:none;}
.tmltab-list li::before{content:"\\2713";flex:0 0 auto;width:21px;height:21px;border-radius:50%;
 background:#587735;color:#fff;font-size:12px;font-weight:800;display:grid;place-items:center;}
@media(min-width:700px){.tmltab-list{grid-template-columns:1fr 1fr;column-gap:32px;}}
</style>"""

TABS = re.compile(r'<div[^>]*class="tabs w-tabs"[^>]*>.*?</div>\s*</div>\s*</div>', re.S)


def balanced(html, start, open_tag="<div", close_tag="</div>"):
    """End index of the element opened at `start`."""
    m = re.match(r"<div[^>]*>", html[start:])
    if not m:
        return None
    depth, pos = 1, start + m.end()
    for t in re.finditer(r"<div\b|</div>", html[pos:]):
        depth += 1 if t.group(0) == "<div" else -1
        if depth == 0:
            return pos + t.end()
    return None


def convert(html):
    i = html.find('class="tabs w-tabs"')
    if i == -1:
        return html, 0
    start = html.rfind("<div", 0, i)
    end = balanced(html, start)
    if end is None:
        return html, 0
    widget = html[start:end]

    labels = [re.sub(r"<[^>]+>", "", m.group(1)).strip()
              for m in re.finditer(r'<a data-w-tab="[^"]*" class="tab-link[^"]*"[^>]*>(.*?)</a>',
                                   widget, re.S)]
    panes = re.findall(r'<div data-w-tab="[^"]*" class="tab-pane[^"]*"[^>]*>\s*'
                       r'<div class="tab-content">(.*?)</div>\s*</div>', widget, re.S)
    if not labels or len(panes) != len(labels):
        return html, 0

    out = []
    for label, body in zip(labels, panes):
        body = body.replace('<ul role="list">', '<ul role="list" class="tmltab-list">')
        body = body.replace('class="list-item-2"', "")
        out.append(f'<div class="tmltab-sec"><h3 class="tmltab-h">{label}</h3>{body}</div>')
    return html[:start] + "".join(out) + html[end:], len(out)


def main():
    pages = made = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if 'class="tabs w-tabs"' not in html:
            continue
        html, n = convert(html)
        if not n:
            continue
        html = re.sub(r'<style id="tmltabs-css">.*?</style>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            made += n
            print(f"  {f.relative_to(F)}: {n} tabs opened into sections")
    print(f"pages changed: {pages}, sections created: {made}")


if __name__ == "__main__":
    main()
