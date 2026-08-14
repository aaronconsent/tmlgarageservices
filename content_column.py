#!/usr/bin/env python3
"""Centre the service-page content instead of pinning it to the left.

These pages were laid out as two columns: an ~854px article and a 340px
sidebar. The sidebar holds three links and is about 150px tall, so past the
first screen the page ran for thousands of pixels with the text jammed against
the left edge and a permanent empty band down the right. That reads as a broken,
off-centre page.

The article column is now centred in the container, and the "Our Services" list
moves to the end of the article as a horizontal row of links -- it keeps its
internal-linking value without costing a third of the page width for its whole
length.

Idempotent.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent / "site"
PAGES = sorted((SITE / "fixed" / "our-services").glob("*/index.html"))

CSS = """<style id="tmlcol-css">
/* one centred column: the old two-column split left a tall empty right band */
.detail-wrap{display:block!important;}
.detail-wrap>.div-block{width:100%!important;max-width:1040px!important;margin:0 auto!important;}
.detail-wrap .sevice-main-image{max-width:none!important;}
.detail-wrap .rich-text{max-width:none!important;}
/* the service list, now a row under the article rather than a column beside it */
.our-services{float:none!important;width:auto!important;max-width:none!important;
 margin:38px 0 8px!important;padding:22px 0 0;border-top:1px solid #e2e5d9;}
.our-services h4{margin:0 0 14px;font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:#5c6553;}
.our-services .service-list{display:grid!important;gap:10px;
 grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));}
.our-services .w-dyn-item{margin:0;}
.our-services .sevice-link{display:block;padding:14px 16px;border:1px solid #e2e5d9;border-radius:12px;
 background:#fff;color:#1f2418;text-decoration:none;font-weight:600;font-size:15px;line-height:1.35;
 transition:border-color .14s ease,color .14s ease;}
.our-services .sevice-link:hover{border-color:#587735;color:#3f5a22;}
</style>"""


def balanced_end(html, open_end, depth=1):
    for m in re.finditer(r"<div\b|</div>", html[open_end:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return open_end + m.end()
    return None


def move_sidebar(html):
    """Take .our-services out of the two-column row and append it to the article."""
    m = re.search(r'<div class="our-services"[^>]*>', html)
    if not m:
        return html, False
    end = balanced_end(html, m.end())
    if end is None:
        return html, False
    block = html[m.start():end]
    rest = html[:m.start()] + html[end:]

    # append inside .div-block, which is the article column
    dm = re.search(r'<div class="div-block"[^>]*>', rest)
    if not dm:
        return html, False
    dend = balanced_end(rest, dm.end())
    if dend is None:
        return html, False
    insert_at = dend - len("</div>")
    return rest[:insert_at] + block + rest[insert_at:], True


def main():
    moved = styled = 0
    for page in PAGES:
        html = page.read_text("utf-8", errors="replace")
        if '<div class="detail-wrap">' not in html:
            continue
        html = re.sub(r'<style id="tmlcol-css">.*?</style>', "", html, flags=re.S)

        # only move it if it is still a direct child of the two-column row
        dw = re.search(r'<div class="detail-wrap"[^>]*>', html)
        sb = html.find('<div class="our-services"')
        already_in_article = False
        if dw and sb != -1:
            depth = 1
            for t in re.finditer(r"<div\b|</div>", html[dw.end():sb]):
                depth += 1 if t.group(0) == "<div" else -1
            already_in_article = depth > 1

        if not already_in_article:
            html, ok = move_sidebar(html)
            moved += int(ok)

        html = html.replace("</head>", CSS + "</head>", 1)
        page.write_text(html, "utf-8")
        styled += 1
    print(f"pages restyled: {styled}, sidebars moved into the article: {moved}")


if __name__ == "__main__":
    main()
