#!/usr/bin/env python3
"""Give the three image-less cards on the services hub their photos.

Four of the seven service cards had a photo and three did not, so the grid read
as half-finished. TML's own library already contained purpose-named photographs
for all three (they ship with the Webflow export and were simply never wired up).

Idempotent: a card that already has a picture is left alone.
"""
import re
import urllib.parse
from pathlib import Path

SITE = Path(__file__).parent / "site"
HUB = SITE / "fixed" / "services" / "index.html"
A1 = "/assets/66b2dae9e779df43d0d269c9"

CARDS = {
    "commercial-overhead-door-services": (
        f"{A1}/66b511bf3289a9426e0f95bb_Commercial%20Overhead%20Door%20Services.jpg",
        "Commercial overhead door at a Houston-area facility"),
    "residential-driveway-gate-services": (
        f"{A1}/66b5119db797c43daeb33012_Residential%20Driveway%20Gate%20Services.jpg",
        "Residential driveway entry gate serviced by TML"),
    "commercial-gate-opener-services": (
        f"{A1}/66b51301eaa11f55da847a3d_commercial%20gate%20and%20opener%20services.jpg",
        "Commercial gate and gate operator serviced by TML"),
}

WIDTHS = (500, 800, 1080)
SIZES = "(max-width: 991px) 100vw, 380px"


def picture(url, alt):
    cands = []
    for w in WIDTHS:
        d = url.rsplit(".", 1)[0] + f"-w{w}.webp"
        if (SITE / urllib.parse.unquote(d).lstrip("/")).exists():
            cands.append(f"{d} {w}w")
    img = f'<img src="{url}" alt="{alt}" loading="lazy" decoding="async">'
    if not cands:
        return img
    return ('<picture><source type="image/webp" srcset="' + ", ".join(cands)
            + f'" sizes="{SIZES}">' + img + "</picture>")


def main():
    html = HUB.read_text("utf-8", errors="replace")
    added = 0
    for slug, (url, alt) in CARDS.items():
        m = re.search(r'(<a class="sv-card" href="/fixed/our-services/%s">)' % re.escape(slug), html)
        if not m:
            print(f"  card not found: {slug}")
            continue
        if html[m.end():m.end() + 40].startswith('<div class="sv-shot">'):
            continue                                   # already has its photo
        shot = f'<div class="sv-shot">{picture(url, alt)}</div>'
        html = html[:m.end()] + shot + html[m.end():]
        added += 1
    HUB.write_text(html, "utf-8")
    print(f"cards given a photo: {added}")


if __name__ == "__main__":
    main()
