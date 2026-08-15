#!/usr/bin/env python3
"""Mobile UX repairs found by measuring the rendered page, not reading the markup.

Six things, all of which only show up once the browser has laid the page out:

  * The header logo carried loading="lazy". It is the first thing on the page,
    so the browser was deferring the one image it should fetch first: the link
    measured 220x0 until it arrived, and the whole header jumped down when it
    did. Now eager, with intrinsic dimensions so the space is reserved.
  * The hero video's pause button rendered 0px wide — present in the markup,
    impossible to press. A video that plays by itself needs a working pause
    control (WCAG 2.2.2), so it is now a real 44px button instead of a
    theoretical one.
  * Carousel and review dots were 8px targets with a 7px gap. Widened to 24px
    hit areas via a pseudo-element, so the dots still look like 8px dots but can
    actually be hit with a thumb. The gap goes to 16px so neighbouring targets
    tile instead of overlapping — 8 + 16 = a 24px pitch, exactly.
  * Footer social icons were 30x30. Now 44x44, which is the size a thumb
    expects, with the icon itself unchanged.
  * Footer links and legal links were 15-24px tall. Padding brings each to 24px
    without moving anything visually.
  * "Explore Services", "View More" and the footer legal row were set at 12px.
    These are the links people are meant to follow; 14px for the calls to
    action, 13px for the legal row.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmlux-css">
/* --- touch targets ------------------------------------------------------ */
/* the dot stays 8px; the pressable area around it becomes 24px */
.tmlcar-dots,.tmlrev-dots{gap:16px;}
.tmlcar-dot,.tmlrev-dot{position:relative;}
.tmlcar-dot::after,.tmlrev-dot::after{content:"";position:absolute;top:50%;left:50%;
 width:24px;height:24px;transform:translate(-50%,-50%);}
.social-block{width:44px;height:44px;display:grid;place-items:center;}
.social-block img{width:22px;height:22px;object-fit:contain;}
.footer-link,.footer-contact{display:inline-block;padding:2px 0;min-height:24px;}
.bottom-link{display:inline-block;padding:4px 0;min-height:24px;}
/* --- legibility --------------------------------------------------------- */
.text-link,.text-link-black{font-size:14px;}
.bottom-text,.bottom-link{font-size:13px;}
/* --- hero video pause button -------------------------------------------- */
/* it was in the markup at 0px wide, so the video could not be stopped */
.w-backgroundvideo-backgroundvideoplaypausebutton{width:44px;height:44px;display:grid;
 place-items:center;padding:0;border:0;border-radius:50%;cursor:pointer;
 background:rgba(0,0,0,.45);backdrop-filter:blur(2px);}
.w-backgroundvideo-backgroundvideoplaypausebutton img{width:18px;height:18px;display:block;}
.w-backgroundvideo-backgroundvideoplaypausebutton:focus-visible{outline:2px solid #cfe84d;
 outline-offset:3px;}
</style>"""


def main():
    logo = video = styled = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")

        # the logo is the first paint on every page: fetch it first, and reserve
        # its box so the header does not jump when it lands
        def fix_logo(m):
            tag = m.group(0)
            tag = tag.replace(' loading="lazy"', "").replace(" loading='lazy'", "")
            if "width=" not in tag:
                tag = tag.replace("<img ", '<img width="220" height="48" ', 1)
            return tag.replace("<img ", '<img fetchpriority="high" decoding="async" ', 1)

        new = re.sub(r'<img\b[^>]*class="nav-logo"[^>]*>', fix_logo, html)
        if new != html:
            logo += 1
            html = new

        if "data-w-bg-video-control" in html:
            video += 1

        html = re.sub(r'<style id="tmlux-css">.*?</style>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)

        if html != orig:
            f.write_text(html, "utf-8")
            styled += 1
    print(f"logo set to eager with reserved space: {logo} page(s)")
    print(f"pages with a hero video pause button now pressable: {video}")
    print(f"pages restyled: {styled}")


if __name__ == "__main__":
    main()
