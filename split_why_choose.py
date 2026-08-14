#!/usr/bin/env python3
"""Give "Why Choose TML Garage Door Services" its own section above the FAQ.

It was the left-hand column of a two-column block, sharing the row with the FAQ
accordion. That squeezed seven reasons-to-buy into a 460px column of small text
running down the side of the page, where it read as a caption to the FAQ rather
than as its own argument.

It is now a full-width section stacked above the FAQ, with the seven reasons as
a grid: bold claim, supporting line underneath, a check against each. Same words,
same black section, same buttons.

Idempotent.
"""
import html as H
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmlwhy-css">
.tmlwhy{margin:0 0 clamp(34px,5vw,60px);}
.tmlwhy h2{color:#fff;margin:0 0 14px;}
.tmlwhy-lede{color:#c9d0bd;font-size:17px;line-height:1.6;margin:0 0 26px;max-width:70ch;}
.tmlwhy-grid{display:grid;gap:22px 30px;grid-template-columns:1fr;margin:0 0 26px;padding:0;list-style:none;}
.tmlwhy-grid li{display:flex;gap:12px;align-items:flex-start;border-top:1px solid rgba(255,255,255,.15);
 padding-top:16px;margin:0;}
.tmlwhy-grid li::before{content:"\\2713";flex:0 0 auto;width:22px;height:22px;border-radius:50%;
 background:#cfe84d;color:#1f2418;font-size:12px;font-weight:800;display:grid;place-items:center;
 margin-top:2px;}
.tmlwhy-grid b{display:block;color:#fff;font-size:16px;line-height:1.25;margin:0 0 5px;}
.tmlwhy-grid span{display:block;color:#c2caB4;font-size:15px;line-height:1.55;}
.tmlwhy-close{color:#c9d0bd;font-size:16.5px;line-height:1.6;margin:0 0 22px;max-width:70ch;}
.tmlwhy-faq{margin:0;}
@media(min-width:760px){.tmlwhy-grid{grid-template-columns:1fr 1fr;}}
@media(min-width:1120px){.tmlwhy-grid{grid-template-columns:repeat(3,1fr);}}
/* the row that used to hold both columns now simply stacks them */
.services .services-wrap{display:block!important;}
.services .service-content,.services .service-faq{width:100%!important;max-width:none!important;}
</style>"""

ITEM = re.compile(r"<li[^>]*>\s*<p[^>]*>\s*<strong>(?P<label>.*?)</strong>(?P<rest>.*?)</p>\s*</li>", re.S)


def strip(x):
    """Unescape before the caller re-escapes, or '&' becomes '&amp;amp;' and an
    apostrophe becomes '&amp;#x27;' on screen."""
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x))).strip()


def balanced(html, start, tag="div"):
    m = re.match(r"<%s[^>]*>" % tag, html[start:])
    if not m:
        return None
    depth, pos = 1, start + m.end()
    for t in re.finditer(r"<%s\b|</%s>" % (tag, tag), html[pos:]):
        depth += 1 if not t.group(0).startswith("</") else -1
        if depth == 0:
            return pos + t.end()
    return None


def convert(html):
    i = html.find('class="service-content"')
    if i == -1 or "tmlwhy-grid" in html:
        return html, 0
    wrap_i = html.rfind('<div class="services-wrap">', 0, i)
    if wrap_i == -1:
        return html, 0
    wrap_end = balanced(html, wrap_i)
    if wrap_end is None:
        return html, 0
    wrap = html[wrap_i:wrap_end]

    head = re.search(r"<h2[^>]*>(.*?)</h2>", wrap, re.S)
    lede = re.search(r"<p class=\"body-small\">(.*?)</p>", wrap, re.S)
    items = [(strip(m.group("label")).rstrip(": "), strip(m.group("rest")).lstrip(": "))
             for m in ITEM.finditer(wrap)]
    btns = re.search(r'<div class="hero-btns">.*?</div>', wrap, re.S)
    faq_i = wrap.find('<div class="service-faq">')
    faq = wrap[faq_i:balanced(wrap, faq_i)] if faq_i != -1 else ""
    closing = re.findall(r"<p class=\"body-small\">(.*?)</p>", wrap, re.S)
    closing = strip(closing[-1]) if len(closing) > 1 else ""

    if not head or len(items) < 3 or not faq:
        return html, 0

    grid = "".join(
        f"<li><div><b>{H.escape(lab)}</b><span>{H.escape(txt)}</span></div></li>"
        for lab, txt in items)
    new = (
        '<div class="services-wrap">'
        '<div class="service-content tmlwhy">'
        f"<h2>{strip(head.group(1))}</h2>"
        + (f'<p class="tmlwhy-lede">{H.escape(strip(lede.group(1)))}</p>' if lede else "")
        + f'<ul class="tmlwhy-grid">{grid}</ul>'
        + (f'<p class="tmlwhy-close">{H.escape(closing)}</p>' if closing else "")
        + (btns.group(0) if btns else "")
        + "</div>"
        f'<div class="tmlwhy-faq">{faq}</div>'
        "</div>")
    return html[:wrap_i] + new + html[wrap_end:], len(items)


def main():
    pages = total = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "Expert Technicians" not in html:
            continue
        html, n = convert(html)
        if not n:
            continue
        html = re.sub(r'<style id="tmlwhy-css">.*?</style>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            total += n
            print(f"  {f.relative_to(F)}: {n} reasons, now above the FAQ")
    print(f"pages changed: {pages}")


if __name__ == "__main__":
    main()
