#!/usr/bin/env python3
"""Create site/fixed/ — a working copy of the classic mirror for repairs.

Byte-identical clone of every classic page with internal PAGE links
rewritten to /fixed/... so navigation stays inside the version (asset
links are untouched; both versions share /assets/). Fixes are then made
directly to site/fixed/ and recorded in CHANGELOG.md.

Refuses to run if site/fixed/ already exists (it would wipe applied
fixes) unless called with --force.
"""
import re
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).parent / "site"
DEST = SITE / "fixed"
SKIP = {"assets", "fixed"}

if DEST.exists() and "--force" not in sys.argv:
    sys.exit("site/fixed/ already exists — it may contain applied fixes. "
             "Use --force to wipe and re-clone from the classic mirror.")
if DEST.exists():
    shutil.rmtree(DEST)

# every internal page route (used to rewrite only page links, not assets)
routes = set()
for p in SITE.rglob("index.html"):
    rel = p.parent.relative_to(SITE)
    if rel.parts and rel.parts[0] in SKIP:
        continue
    routes.add("/" if str(rel) == "." else "/" + str(rel))

def rewrite_links(html: str) -> str:
    def sub(m):
        href = m.group(2)
        route = href.rstrip("/") or "/"
        if route in routes:
            return f'{m.group(1)}"{"/fixed" if route == "/" else "/fixed" + route}"'
        return m.group(0)
    return re.sub(r'(href=)"(/[^"#?]*)"', sub, html)

count = 0
for p in sorted(SITE.rglob("index.html")):
    rel = p.parent.relative_to(SITE)
    if rel.parts and rel.parts[0] in SKIP:
        continue
    dest = DEST / ("index.html" if str(rel) == "." else f"{rel}/index.html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rewrite_links(p.read_text("utf-8", errors="replace")), "utf-8")
    count += 1

print(f"cloned {count} pages -> site/fixed/ (links rewritten to stay in /fixed/)")
