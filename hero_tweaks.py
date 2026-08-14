#!/usr/bin/env python3
"""Home-hero tweaks + emergency button placement (site/fixed/).

- remove the "☎ CALL NOW / 832-887-8747" box from the home hero
- put the hero copy in the same semi-transparent black box used elsewhere,
  at every breakpoint (it was mobile-only before)
- move the floating Emergency Service button to the right side
Idempotent.
"""
import re
from pathlib import Path
from collections import Counter

F = Path(__file__).parent / "site" / "fixed"
n = Counter()

CALL_BOX = re.compile(
    r'<a href="tel:\+18328878747" class="button w-button">\s*<strong class="bold-text">.*?CALL NOW.*?</strong>\s*</a>',
    re.S | re.I)

HERO_CSS = (
    '<style id="tmlhero-css">'
    # hero copy sits in the standard scrim box at all sizes
    '.hero-section .hero-content{background:rgba(0,0,0,.55);border-radius:10px;'
    'padding:26px 26px 24px;max-width:680px;}'
    '.hero-section .hero-title,.hero-section .hero-content p{color:#fff;}'
    # emergency service button -> right side
    '.floating-holder{left:auto!important;right:18px!important;bottom:18px!important;}'
    '.green-button-floating{box-shadow:0 8px 24px -8px rgba(0,0,0,.5);}'
    '@media(max-width:767px){.hero-section .hero-content{padding:18px 16px;}}'
    "</style>")

for f in sorted(F.rglob("index.html")):
    h = orig = f.read_text("utf-8", errors="replace")

    if f.parent == F:                       # home page only for the call box
        h, r = CALL_BOX.subn("", h)
        n["call_box_removed"] += r

    h = re.sub(r'<style id="tmlhero-css">.*?</style>', "", h, flags=re.S)
    h = h.replace("</head>", HERO_CSS + "</head>", 1)

    # the mobile-only scrim rule is now redundant (handled at all sizes)
    h = h.replace(".hero-content{background:rgba(0,0,0,.55);padding:18px 16px;border-radius:10px;}", "")

    if h != orig:
        f.write_text(h, "utf-8")
        n["pages"] += 1

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
