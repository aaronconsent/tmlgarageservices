#!/usr/bin/env python3
"""Frame the Workiz booking widget properly.

Hard limit worth stating plainly: the widget is a third-party iframe from
online-booking.workiz.com. Nothing inside it can be styled from here — not its
fonts, colours, spacing or buttons. Browsers forbid reaching into a cross-origin
frame, and Workiz sends no height messages we could listen for. Its own look is
changed in the Workiz dashboard, not in this code.

What this does control is everything around it:

  * Mobile width — the panel and slot each added padding, so the widget got
    309px of a 375px screen. On phones the frame now goes edge to edge.
  * Height — a fixed 760px box left ~500px of empty grey on the first step and
    forced scroll-inside-a-scroll later on. On phones it is now sized to the
    screen, so the widget fills it like an app step instead of floating in a
    half-empty box.
  * Desktop balance — the support panel beside it is only ~260px tall next to a
    760px widget, which left a large dead area. It now sticks as the widget
    scrolls past.
  * The frame itself — one clean white card with a border and rounded corners,
    rather than the widget's own grey butting against the page.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmlwz-css">
/* the widget is a cross-origin iframe: only the frame around it is ours */
.tb-slot{padding:0!important;background:#fff;border:1px solid #dfe3d5;border-radius:14px;
 overflow:hidden;}
.tb-slot iframe{display:block;width:100%;border:0;border-radius:0;}
/* desktop: the support panel is far shorter than the widget, so let it ride along
   instead of leaving a tall empty gap beside it */
@media(min-width:900px){
 .tb-side{position:sticky;top:96px;}
 /* !important: the script writes min-height inline, which a plain rule cannot beat */
 .tb-slot iframe{min-height:820px!important;}
}
/* phones: full width, and sized to the screen so the first step is not a small
   card adrift in 500px of grey, and later steps scroll like a normal app screen */
@media(max-width:899px){
 .tb-panel{padding-left:0!important;padding-right:0!important;background:none!important;
  border:0!important;}
 .tb-panel-head{padding:0 16px;}
 .tb-slot{border-radius:12px;}
 .tb-slot iframe{min-height:0!important;height:calc(100dvh - 190px);min-height:560px;}
}
@supports not (height:100dvh){
 @media(max-width:899px){.tb-slot iframe{height:calc(100vh - 190px);}}
}
</style>"""


def main():
    pages = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "tmlworkiz-account" not in html:      # only pages running the live widget
            continue
        html = re.sub(r'<style id="tmlwz-css">.*?</style>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            print(f"  {f.relative_to(F)}: widget frame styled")
    print(f"pages styled: {pages}")


if __name__ == "__main__":
    main()
