#!/usr/bin/env python3
"""Head-tag hygiene across site/fixed/: correct og:url, add the canonical
each page was missing, and point og/twitter URLs at the production domain.

Companion finding (see CHANGELOG): the client's LIVE Webflow site has a
page-level "noindex, follow" on /services and og:url values on the
misspelled tmlhomeimprovment.com domain — those must be corrected in
Webflow itself; this script fixes our version.
"""
import re
from pathlib import Path
from collections import Counter

F = Path(__file__).parent / "site" / "fixed"
PROD = "https://www.tmlgarageservices.com"
n = Counter()

for p in sorted(F.rglob("index.html")):
    h = orig = p.read_text("utf-8", errors="replace")
    rel = str(p.parent.relative_to(F))
    url = PROD + "/" if rel == "." else f"{PROD}/{rel}"

    # 1. og:url -> this page's production URL (retires tmlhomeimprovment.com)
    def og(m):
        n["og_url"] += 1
        return f'<meta property="og:url" content="{url}"/>'
    h, c = re.subn(r'<meta[^>]*property="og:url"[^>]*>', og, h)
    if not c:
        h = h.replace("</title>", f'</title><meta property="og:url" content="{url}"/>', 1)
        n["og_url_added"] += 1

    # 2. canonical (none of these pages had one)
    if 'rel="canonical"' not in h:
        h = h.replace("</title>", f'</title><link rel="canonical" href="{url}"/>', 1)
        n["canonical"] += 1

    if h != orig:
        p.write_text(h, "utf-8")
        n["pages"] += 1

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
