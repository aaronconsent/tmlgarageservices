#!/usr/bin/env python3
"""Put the real booking form on the pages, instead of a link to it.

The six pages that used to carry the dead Webflow contact form were given a
panel that linked through to /fixed/schedule-consult. This replaces that panel
with the booking form itself — pick the problem, pick a day, pick a time window,
leave your details — so a visitor never has to leave the page they landed on.

The component (markup, styles and script) is lifted from the booking page at
build time, so there is one source of truth: change the booking page and re-run
this, and all six pages follow.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"
SOURCE = F / "schedule-consult" / "index.html"

# the form is built for a full-width page; these few rules let it sit inside the
# narrower column the old contact form occupied
FIT_CSS = """<style id="tmlbookfit-css">
.tmlbookfit{background:#f5f7ef;border:1px solid #dfe3d5;border-radius:16px;
 padding:clamp(20px,3vw,28px);max-width:640px;}
.tmlbookfit .tmlbookfit-head h3{margin:0 0 6px;font-size:clamp(20px,2.6vw,25px);
 line-height:1.15;color:#1f2418;}
.tmlbookfit .tmlbookfit-head p{margin:0 0 18px;font-size:15.5px;line-height:1.55;color:#535c48;}
/* .bk-days is a horizontal swipe strip (flex + overflow-x), not a grid — leave it be */
.tmlbookfit .bk-fields{grid-template-columns:1fr;}
@media(min-width:560px){.tmlbookfit .bk-fields{grid-template-columns:1fr 1fr;}}
/* the legacy two-column rows on these pages never stacked on a phone, which
   squeezed the form into ~205px of a 375px screen. Scoped with :has() so only
   the rows that actually contain the form are affected. */
@media(max-width:860px){
 .section-inner:has(.tmlbookfit),.contact:has(.tmlbookfit),
 .discuss-wrap:has(.tmlbookfit),.services-wrap:has(.tmlbookfit){
  display:block!important;}
 .tmlbookfit{max-width:none;}
}
/* the page container, this panel and the form's own slot each add padding; on a
   phone that stacked up to 63px a side and left the form only ~205px of 375 */
@media(max-width:600px){
 .tmlbookfit{padding:16px;}
 .tmlbookfit #tmlbook-slot{padding:0;border:0;background:none;}
 /* the three arrival windows squeezed to 72px each and wrapped their times;
    stacked, each is a full-width tap target */
 .tmlbookfit .bk-windows{grid-template-columns:1fr;}
}
</style>"""

HEAD = ('<div class="tmlbookfit-head"><h3>Schedule your appointment</h3>'
        "<p>Takes about a minute. You'll get a confirmation right away.</p></div>")


def balanced(html, start):
    m = re.match(r"<div[^>]*>", html[start:])
    if not m:
        return None
    depth, pos = 1, start + m.end()
    for t in re.finditer(r"<div\b|</div>", html[pos:]):
        depth += 1 if t.group(0) == "<div" else -1
        if depth == 0:
            return pos + t.end()
    return None


def component():
    """Pull the form, its stylesheet and its script off the booking page."""
    src = SOURCE.read_text("utf-8", errors="replace")
    i = src.find('<div class="tb-slot" id="tmlbook-slot">')
    end = balanced(src, i) if i != -1 else None
    if end is None:
        raise SystemExit("could not find the booking form on the booking page")
    slot = src[i:end]
    css = re.search(r'<style id="tmlbook-css">.*?</style>', src, re.S)
    js = re.search(r'<script id="tmlbook-js">.*?</script>', src, re.S)
    if not css or not js:
        raise SystemExit("booking styles or script missing from the booking page")
    return slot, css.group(0), js.group(0)


def main():
    slot, css, js = component()
    pages = 0
    for f in sorted(F.rglob("index.html")):
        if f == SOURCE:
            continue
        html = orig = f.read_text("utf-8", errors="replace")
        if 'class="tmlbook"' not in html and "tmlbookfit" not in html:
            continue

        # drop any previous embed so a re-run refreshes rather than stacks
        for pat in (r'<style id="tmlbook-css">.*?</style>',
                    r'<style id="tmlbookfit-css">.*?</style>',
                    r'<style id="tmlbook-panel-css">.*?</style>',
                    r'<script id="tmlbook-js">.*?</script>'):
            html = re.sub(pat, "", html, flags=re.S)

        block = f'<div class="tmlbookfit">{HEAD}{slot}</div>'
        i = html.find('<div class="tmlbook">')
        if i != -1:
            end = balanced(html, i)
            html = html[:i] + block + html[end:]
        else:
            i = html.find('<div class="tmlbookfit">')
            end = balanced(html, i)
            html = html[:i] + block + html[end:]

        html = html.replace("</head>", css + FIT_CSS + "</head>", 1)
        html = html.replace("</body>", js + "</body>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            print(f"  {f.relative_to(F)}: booking form embedded")
    print(f"pages with the live form: {pages}")


if __name__ == "__main__":
    main()
