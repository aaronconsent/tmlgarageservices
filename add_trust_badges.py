#!/usr/bin/env python3
"""Copy the Angi / HomeAdvisor badges into "Why Choose TML Garage Door Services?".

The three badges sit near the bottom of the page, below the fold, where almost
nobody scrolls. Repeating them inside the reasons-to-choose-us section puts them
next to the argument they support.

The badge images are read from the footer of the same page, so there is one
source: change them there and re-run, and the copies follow.

Two details worth knowing:
  * All three PNGs have transparent backgrounds and dark artwork. The Why Choose
    panel is black, so they would have been close to invisible dropped straight
    in — each sits on a white tile.
  * The Angi badge links to "#" in the footer, which just jumps to the top of the
    page. The copy is rendered without a link rather than repeating that.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

# Set False to take the copies back out of Why Choose (the originals in the footer
# are untouched either way). Turned off: the Angi award is dated 2019 and the
# HomeAdvisor badges have not been checked as current, so repeating them further
# up the page put more weight on claims nobody has verified.
SHOW_BADGES = False

CSS = """<style id="tmlbadge-css">
.tmlwhy-badges{display:flex;flex-wrap:wrap;gap:12px;align-items:stretch;
 margin:0 0 26px;padding:0;list-style:none;}
.tmlwhy-badges li{margin:0;}
.tmlwhy-badges a,.tmlwhy-badges span{display:grid;place-items:center;background:#fff;
 border-radius:12px;padding:12px 16px;min-height:86px;min-width:96px;}
.tmlwhy-badges a{transition:transform .14s ease;}
.tmlwhy-badges a:hover{transform:translateY(-2px);}
.tmlwhy-badges a:focus-visible{outline:2px solid #cfe84d;outline-offset:3px;}
.tmlwhy-badges img{display:block;height:62px;width:auto;max-width:100%;object-fit:contain;}
@media(max-width:520px){
 .tmlwhy-badges a,.tmlwhy-badges span{min-height:74px;padding:10px 12px;}
 .tmlwhy-badges img{height:50px;}
}
@media(prefers-reduced-motion:reduce){.tmlwhy-badges a{transition:none;}}
</style>"""

BADGE_IMG = re.compile(
    r'<a href="(?P<href>[^"]*)"[^>]*class="w-inline-block"[^>]*>\s*'
    r'(?P<img><img[^>]*(?:angies-list-award|soap-solid-border|3year-solid-border)[^>]*>)\s*</a>',
    re.S)


def badges_from(html):
    """Pull the three badge links out of the footer."""
    out, seen = [], set()
    for m in BADGE_IMG.finditer(html):
        src = re.search(r'\ssrc="([^"]+)"', m.group("img"))
        if src:                       # some pages carry the badge strip twice
            if src.group(1) in seen:
                continue
            seen.add(src.group(1))
        href, img = m.group("href"), m.group("img")
        img = re.sub(r'\sclass="[^"]*"', "", img)          # footer-specific sizing
        img = re.sub(r"\s+loading=\"[^\"]*\"", "", img) + ""
        img = img.replace("<img ", '<img loading="lazy" decoding="async" ')
        if href and href != "#":
            out.append(f'<li><a href="{href}" target="_blank" rel="noopener">{img}</a></li>')
        else:
            out.append(f"<li><span>{img}</span></li>")
    return out


def main():
    pages = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if 'class="tmlwhy-grid"' not in html:
            continue
        html = re.sub(r'<ul class="tmlwhy-badges">.*?</ul>', "", html, flags=re.S)
        html = re.sub(r'<style id="tmlbadge-css">.*?</style>', "", html, flags=re.S)

        if not SHOW_BADGES:
            if html != orig:
                f.write_text(html, "utf-8")
                pages += 1
                print(f"  {f.relative_to(F)}: badge copies removed")
            continue

        badges = badges_from(html)
        if len(badges) < 2:
            print(f"  {f.relative_to(F)}: badges not found in footer — skipped")
            continue

        row = '<ul class="tmlwhy-badges">' + "".join(badges) + "</ul>"
        # anchor INSIDE the Why Choose block: "hero-btns" also appears in the page
        # hero, and matching the first one put the badges in the banner
        why = html.find('class="service-content tmlwhy"')
        if why == -1:
            print(f"  {f.relative_to(F)}: Why Choose block not found — skipped")
            continue
        anchor = html.find('<div class="hero-btns">', why)
        if anchor == -1:
            anchor = html.find("</ul>", why)
            anchor = anchor + len("</ul>") if anchor != -1 else -1
        if anchor == -1:
            print(f"  {f.relative_to(F)}: no anchor inside Why Choose — skipped")
            continue
        html = html[:anchor] + row + html[anchor:]

        html = html.replace("</head>", CSS + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            print(f"  {f.relative_to(F)}: {len(badges)} badges copied into Why Choose")
    print(f"pages changed: {pages}")


if __name__ == "__main__":
    main()
