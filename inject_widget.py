#!/usr/bin/env python3
"""Inject the version switcher into every page (original + fixed). Idempotent."""
from pathlib import Path

SITE = Path(__file__).parent / "site"
TAG = '<script src="/switch.js" defer></script>'

count = 0
for f in list(SITE.rglob("index.html")) + [SITE / "404.html"]:
    if "assets" in f.relative_to(SITE).parts or "changes" in f.relative_to(SITE).parts:
        continue
    html = f.read_text("utf-8", errors="replace")
    if TAG in html or "</body>" not in html:
        continue
    f.write_text(html.replace("</body>", TAG + "</body>", 1), "utf-8")
    count += 1
print(f"switcher injected into {count} pages")
