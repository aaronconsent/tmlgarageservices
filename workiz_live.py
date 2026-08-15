#!/usr/bin/env python3
"""Switch pages over to the live Workiz Online Booking widget, one at a time.

The booking script already supports a token, but it lives in the shared script
that every embedded copy carries — setting it there would flip all seven pages
at once. Instead the script now also reads `window.TML_WORKIZ_ACCOUNT`, and this
sets that global on named pages only.

To roll out to another page, add its path to LIVE_PAGES and re-run. To roll back,
remove it and re-run. Nothing else changes: pages without the global keep the
prototype flow.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

# Workiz → Online Booking → Get embed code (the ac=... value). Public by design:
# it travels in the iframe URL, so it is not a secret.
ACCOUNT = "10df6dd8ecbd3be6b547a8f29844054f3c21419b0cb7b7a15eaf1b3c6a331b7d"

# pages running the real Workiz widget. Start with the dedicated booking page;
# add the rest once it has been checked with a real booking.
LIVE_PAGES = [
    "schedule-consult/index.html",
]

TAG = ('<script id="tmlworkiz-account">window.TML_WORKIZ_ACCOUNT='
       f'"{ACCOUNT}";</script>')

# the shared booking script reads cfg.account; teach it to prefer the per-page
# global so one page can go live without dragging the others with it
OLD_READ = "var account = override || cfg.account;"
NEW_READ = ("var account = override || window.TML_WORKIZ_ACCOUNT || cfg.account;"
            "  // per-page opt-in")


def main():
    live = {str(p) for p in LIVE_PAGES}
    patched = enabled = disabled = 0

    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "tmlbook-js" not in html:
            continue

        if OLD_READ in html:
            html = html.replace(OLD_READ, NEW_READ)
            patched += 1

        rel = str(f.relative_to(F))
        html = re.sub(r'<script id="tmlworkiz-account">.*?</script>', "", html, flags=re.S)
        if rel in live:
            html = html.replace("</head>", TAG + "</head>", 1)
            enabled += 1
        elif 'id="tmlworkiz-account"' in orig:
            disabled += 1

        if html != orig:
            f.write_text(html, "utf-8")

    print(f"booking script patched on {patched} page(s)")
    print(f"live Workiz widget: {enabled} page(s) -> {', '.join(LIVE_PAGES)}")
    if disabled:
        print(f"reverted to the prototype flow: {disabled} page(s)")


if __name__ == "__main__":
    main()
