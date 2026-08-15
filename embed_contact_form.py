#!/usr/bin/env python3
"""Put the Workiz service-request form on the pages that are not the booking page.

The booking page runs the full Workiz online-booking widget (pick a service, a
day and a time). Everywhere else a shorter form suits better: name, phone,
email, message. This is Workiz's own Send A Job service-request form, so those
submissions land in the same Workiz account as the bookings — one inbox, no
separate CRM to wire up.

It replaces the prototype booking form embedded on those pages, and takes the
now-unused prototype styles and script out with it.

Checked before shipping: the SEND button sits 347px down at both 620px and 340px
wide, so the 407px frame height clears it at either size with no inner scrollbar.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

FORM_SRC = ("https://st.sendajob.com/MY/servicerequest/"
            "2d84b4cf24c7da337cffe1ceb1f4d4129519b227_f.html")
FRAME_H = 407
PHONE, PHONE_HREF, SMS_HREF = "(832) 887-8747", "tel:+18328878747", "sms:+18328878747"
BOOK = "/fixed/schedule-consult"

CSS = """<style id="tmlsaj-css">
.tmlsaj{background:#f5f7ef;border:1px solid #dfe3d5;border-radius:16px;
 padding:clamp(18px,3vw,26px);max-width:640px;}
.tmlsaj h3{margin:0 0 6px;font-size:clamp(20px,2.6vw,25px);line-height:1.15;color:#1f2418;}
.tmlsaj>p{margin:0 0 16px;font-size:15.5px;line-height:1.55;color:#535c48;max-width:52ch;}
.tmlsaj-frame{background:#fff;border:1px solid #dfe3d5;border-radius:12px;overflow:hidden;}
.tmlsaj-frame iframe{display:block;width:100%;border:0;}
.tmlsaj-alt{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0 0;
 font-size:15px;color:#535c48;}
.tmlsaj-alt a{display:inline-flex;align-items:center;gap:7px;min-height:44px;padding:0 16px;
 border-radius:10px;border:2px solid #1f2418;background:#fff;color:#1f2418;text-decoration:none;
 font-weight:700;font-size:15px;white-space:nowrap;transition:background .14s ease,color .14s ease;}
.tmlsaj-alt a:hover{background:#1f2418;color:#fff;}
.tmlsaj-alt a:focus-visible{outline:2px solid #587735;outline-offset:2px;}
/* the legacy two-column rows on these pages never stacked on a phone, which left
   the form about 239px of a 375px screen. Same fix the booking panel needed. */
@media(max-width:860px){
 .section-inner:has(.tmlsaj),.contact:has(.tmlsaj),
 .discuss-wrap:has(.tmlsaj),.services-wrap:has(.tmlsaj){display:block!important;}
 .tmlsaj{max-width:none;}
}
@media(max-width:600px){.tmlsaj{padding:16px;max-width:none;}}
@media(prefers-reduced-motion:reduce){.tmlsaj-alt a{transition:none;}}
</style>"""

BLOCK = (
    '<div class="tmlsaj">'
    "<h3>Request service</h3>"
    "<p>Tell us what the door is doing and we'll get straight back to you. "
    "Same-day and weekend appointments are available at no extra charge.</p>"
    f'<div class="tmlsaj-frame"><iframe src="{FORM_SRC}" title="Request service from TML '
    f'Garage Door Services" height="{FRAME_H}" scrolling="no" loading="lazy"'
    f' style="height:{FRAME_H}px"></iframe></div>'
    '<p class="tmlsaj-alt">In a hurry?'
    f'<a href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
    f'<a href="{SMS_HREF}" data-book="text">&#128172; Text us</a>'
    f'<a href="{BOOK}" data-book="book">Pick a time</a>'
    "</p></div>")


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


def main():
    pages = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "tmlworkiz-account" in html:
            continue                      # the booking page keeps the full widget
        target = "tmlbookfit" if 'class="tmlbookfit"' in html else (
            "tmlsaj" if 'class="tmlsaj"' in html else None)
        if not target:
            continue

        i = html.find(f'<div class="{target}">')
        end = balanced(html, i)
        if end is None:
            continue
        html = html[:i] + BLOCK + html[end:]

        # the prototype booking form is gone from this page; its styles and script go too
        for pat in (r'<style id="tmlbook-css">.*?</style>',
                    r'<style id="tmlbookfit-css">.*?</style>',
                    r'<script id="tmlbook-js">.*?</script>',
                    r'<style id="tmlsaj-css">.*?</style>'):
            html = re.sub(pat, "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)

        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            print(f"  {f.relative_to(F)}: service-request form embedded")
    print(f"pages changed: {pages}")


if __name__ == "__main__":
    main()
