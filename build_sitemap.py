#!/usr/bin/env python3
"""robots.txt and sitemap.xml.

The site had neither. A sitemap is not required for a 30-page site — Google
will crawl it anyway — but it is the fastest way to tell Search Console what
exists, and it makes an omission obvious: anything not in the file is either
hidden on purpose or was forgotten.

Two rules hold this together:

  * Hidden pages come from hide_pages.py, so the sitemap and the noindex tags
    can never drift apart. If a page is hidden there, it is absent here and
    disallowed in robots.txt.
  * URLs are written on the production domain with clean paths — no /fixed/ —
    matching the canonical tags already on every page. That is the shape of the
    site the day it goes live, which is when this file starts being read.

Priorities are deliberately flat apart from the money pages: search engines
largely ignore the field, and inventing a fine-grained hierarchy implies
knowledge nobody has.

Idempotent.
"""
from pathlib import Path
from datetime import date

from hide_pages import HIDDEN_PREFIXES, is_hidden

ROOT = Path(__file__).parent
SITE = ROOT / "site"
F = SITE / "fixed"
LIVE = "https://www.tmlgarageservices.com"

# the pages that earn money, and the hub pages that feed them
PRIORITY = {
    "": ("1.0", "weekly"),
    "services": ("0.9", "monthly"),
    "schedule-consult": ("0.9", "monthly"),
    "contact": ("0.8", "monthly"),
    "about": ("0.6", "yearly"),
}
LEGAL = ("privacy-policy", "terms-conditions", "cookie-policy")


def url_for(rel):
    return LIVE + "/" if rel == "." else f"{LIVE}/{rel}"


def entries():
    out = []
    for p in sorted(F.rglob("index.html")):
        rel = str(p.parent.relative_to(F))
        if is_hidden(rel):
            continue
        key = "" if rel == "." else rel
        if key in LEGAL:
            pri, freq = "0.2", "yearly"
        elif key.startswith("our-services/") or key.startswith("brands/"):
            pri, freq = "0.8", "monthly"
        elif key.startswith("blogs/") or key.startswith("service-areas/"):
            pri, freq = "0.5", "monthly"
        else:
            pri, freq = PRIORITY.get(key, ("0.5", "monthly"))
        out.append((url_for(rel), pri, freq))
    return out


def main():
    today = date.today().isoformat()
    rows = entries()
    body = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>{f}</changefreq>\n    <priority>{p}</priority>\n  </url>"
        for u, p, f in rows)
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n", "utf-8")

    disallow = "\n".join(f"Disallow: /{p}" for p in HIDDEN_PREFIXES)
    (SITE / "robots.txt").write_text(
        "# TML Garage Door Services\n"
        "User-agent: *\n"
        "Allow: /\n\n"
        "# placeholder content held back from launch — see hide_pages.py\n"
        f"{disallow}\n\n"
        f"Sitemap: {LIVE}/sitemap.xml\n", "utf-8")

    print(f"sitemap.xml: {len(rows)} URLs")
    print(f"robots.txt: {len(HIDDEN_PREFIXES)} disallowed prefixes")


if __name__ == "__main__":
    main()
