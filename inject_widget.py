#!/usr/bin/env python3
"""Inject the design-preview switcher into every legacy page (idempotent).
The new-design pages include it from their template; this covers the mirror."""
from pathlib import Path

SITE = Path(__file__).parent / "site"
TAG = '<script src="/switch.js" defer></script>'

count = 0
for f in list(SITE.rglob("index.html")) + [SITE / "404.html"]:
    if "new" in f.relative_to(SITE).parts:
        continue
    html = f.read_text("utf-8", errors="replace")
    if TAG in html:
        continue
    if "</body>" in html:
        f.write_text(html.replace("</body>", TAG + "</body>", 1), "utf-8")
        count += 1
print(f"injected switcher into {count} legacy pages")
