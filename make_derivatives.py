#!/usr/bin/env python3
"""Generate WebP derivatives for the photos used on the service pages.

The Webflow originals are 2 MB PNGs displayed at ~430 px wide. Webflow's own
-p-500/-p-800 fallbacks are still 230-450 KB because they stayed PNG. These
WebP versions land around 30-60 KB at the sizes actually rendered.

Idempotent: skips a derivative that already exists and is newer than its source.
"""
import re
import urllib.parse
from pathlib import Path

from PIL import Image

SITE = Path(__file__).parent / "site"
WIDTHS = (500, 800, 1080)
QUALITY = 82


def sources():
    """Every photo referenced by design_sections.py, plus the legacy page banners."""
    src = (Path(__file__).parent / "design_sections.py").read_text()
    ns = {}
    exec("\n".join(l for l in src.splitlines() if re.match(r"^(A1|A2) =", l)), ns)
    urls = set()
    for m in re.finditer(r'f"\{(A1|A2)\}(/[^"]+)"', src):
        urls.add(ns[m.group(1)] + m.group(2))
    for page in sorted((SITE / "fixed" / "our-services").glob("*/index.html")):
        for tag in re.findall(r'<img[^>]*class="service-main-img"[^>]*>', page.read_text()):
            m = re.search(r'\ssrc="([^"]+)"', tag)   # src may precede or follow class=
            if m:
                urls.add(m.group(1))
    return sorted(urls)


def webp_url(url, width):
    """Derivative URL beside the original: foo.PNG -> foo-w800.webp"""
    return url.rsplit(".", 1)[0] + f"-w{width}.webp"


def build():
    made = skipped = 0
    for url in sources():
        src = SITE / urllib.parse.unquote(url).lstrip("/")
        if not src.exists():
            print(f"  MISSING SOURCE {url}")
            continue
        im = Image.open(src)
        im = im.convert("RGB")
        for w in WIDTHS:
            if im.width < w:
                continue
            out = SITE / urllib.parse.unquote(webp_url(url, w)).lstrip("/")
            if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
                skipped += 1
                continue
            im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(
                out, "WEBP", quality=QUALITY, method=6)
            made += 1
    print(f"derivatives written: {made}, already current: {skipped}")


if __name__ == "__main__":
    build()
