#!/usr/bin/env python3
"""Serve every content image on the Fixed site as WebP.

The Webflow export ships 2 MB PNGs and uses them everywhere, including as
gallery thumbnails. Even Webflow's own -p-500/-p-800 fallbacks stayed PNG, so
a single service page pulled ~19 MB of images.

This generates WebP derivatives beside each original and wraps the <img> in a
<picture> with a WebP <source>. The original <img> is untouched, so anything
that cannot read WebP still gets the PNG.

Idempotent: an <img> already inside a <picture> is skipped.
"""
import re
import urllib.parse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
SITE = ROOT / "site"
FIXED = SITE / "fixed"
WIDTHS = (500, 800, 1080, 1600)
QUALITY = 82
MIN_BYTES = 120_000          # leave small images alone; the rewrite would not pay for itself
DEFAULT_SIZES = "(max-width: 991px) 100vw, 900px"

RASTER = re.compile(r"\.(png|jpe?g)$", re.I)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)


def local_path(url):
    return SITE / urllib.parse.unquote(url).lstrip("/")


def webp_url(url, width):
    return url.rsplit(".", 1)[0] + f"-w{width}.webp"


def derivatives(url, made):
    """Ensure WebP derivatives exist; return srcset candidates."""
    src = local_path(url)
    if not src.exists() or src.stat().st_size < MIN_BYTES or not RASTER.search(url):
        return []
    im = None
    cands = []
    for w in WIDTHS:
        out = local_path(webp_url(url, w))
        if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            if im is None:
                im = Image.open(src).convert("RGB")
            if im.width < w:
                continue
            im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(
                out, "WEBP", quality=QUALITY, method=6)
            made.append(out.name)
        if out.exists():
            cands.append(f"{webp_url(url, w)} {w}w")
    return cands


def rewrite(html, made):
    # anything already inside a <picture> was wrapped on a previous run
    wrapped = [(w.start(), w.end()) for w in re.finditer(r"<picture\b.*?</picture>", html, re.S)]

    out, pos, count = [], 0, 0
    for m in IMG_TAG.finditer(html):
        tag = m.group(0)
        src = re.search(r'\ssrc="([^"]+)"', tag)
        if not src or any(a <= m.start() < b for a, b in wrapped):
            continue
        url = src.group(1)
        if not url.startswith("/assets/") or not RASTER.search(url):
            continue
        cands = derivatives(url, made)
        if not cands:
            continue
        sizes = re.search(r'\ssizes="([^"]*)"', tag)
        source = (f'<picture><source type="image/webp" srcset="{", ".join(cands)}" '
                  f'sizes="{sizes.group(1) if sizes else DEFAULT_SIZES}">')
        out.append(html[pos:m.start()])
        out.append(source + tag + "</picture>")
        pos = m.end()
        count += 1
    out.append(html[pos:])
    return "".join(out), count


def main():
    made, pages, imgs = [], 0, 0
    for page in sorted(FIXED.rglob("index.html")):
        html = page.read_text("utf-8")
        new, count = rewrite(html, made)
        if count:
            page.write_text(new, "utf-8")
            pages += 1
            imgs += count
    print(f"pages rewritten: {pages}, images wrapped: {imgs}, derivatives made: {len(made)}")


if __name__ == "__main__":
    main()
