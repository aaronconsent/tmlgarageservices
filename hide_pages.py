#!/usr/bin/env python3
"""Keep the placeholder pages hidden after launch.

Right now every page carries a sitewide noindex, which is what has kept the
staging site out of Google. That comes off at cutover — and when it does, two
groups of pages must stay hidden:

  * /teams/ - four biography pages for "Darrell Steward", "Esther Howards",
    "Jerome Bell" and "Kristin Watson". These are Webflow's stock placeholder
    names, presented as TML's Founder, Co-Founder, Managing Director and Sales
    Manager. Publishing invented executives for a real business is the single
    riskiest thing on the site.
  * /projects/ - four kitchen remodel case studies belonging to TML Home
    Improvement, the other company. Accurate work, wrong business.

Neither group is reachable from the real site: they link only to each other,
and none of the four names appears anywhere else. So hiding them is three
things - a page-level noindex, a Disallow in robots.txt, and no sitemap entry.

The noindex here is deliberately marked with a comment, so whoever strips the
sitewide noindex at cutover can tell these apart and leave them alone. Deleting
the pages outright is the cleaner end state; that is the client's call, and
until they make it these stay invisible.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

# imported by build_sitemap.py so the two can never disagree
HIDDEN_PREFIXES = ("teams/", "projects/")

MARKER = "<!-- tml-permanent-noindex: placeholder content, keep hidden at launch -->"
TAG = f'<meta name="robots" content="noindex, nofollow">{MARKER}'


def is_hidden(rel):
    return any(rel.startswith(p) for p in HIDDEN_PREFIXES)


def hidden_pages():
    return sorted(p for p in F.rglob("index.html")
                  if is_hidden(str(p.parent.relative_to(F))))


def main():
    done = 0
    for f in hidden_pages():
        html = orig = f.read_text("utf-8", errors="replace")
        # drop whatever robots tag is there (with or without the marker) and re-add
        html = re.sub(r'<meta\b[^>]*name="robots"[^>]*>(?:\s*' + re.escape(MARKER) + r')?',
                      "", html)
        html = html.replace("</head>", TAG + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            done += 1
        print(f"  {f.parent.relative_to(F)}: permanent noindex")
    print(f"pages held back from launch: {len(hidden_pages())} ({done} rewritten)")


if __name__ == "__main__":
    main()
