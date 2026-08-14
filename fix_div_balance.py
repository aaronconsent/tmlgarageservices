#!/usr/bin/env python3
"""Repair pages left with an unclosed <div>, and guard against new ones.

Several generators splice new markup over a region of the Webflow export. When
that region ended inside a wrapper, its closing </div> went with it and the page
was left one short. Browsers silently auto-close at </body>, which pushed the
sidebar column inside the content column: the content ended up locked to 900px
with a dead gutter beside it, reading as "the whole page is shifted left".

Run last in the chain. Idempotent: a balanced page is left untouched.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent / "site"

OPEN_DIV = re.compile(r"<div\b")
CLOSE_DIV = re.compile(r"</div>")
SIDEBAR = '<div class="our-services"'
FOOTER = re.compile(r'<div class="footer[^"]*"')


def balance(html):
    return len(OPEN_DIV.findall(html)) - len(CLOSE_DIV.findall(html))


def insertion_point(html):
    """Where the missing </div> belongs: before the sidebar column if the page
    has one (it must be a sibling of the content column, not a child), else
    just before the footer."""
    i = html.find(SIDEBAR)
    if i != -1:
        return i
    m = FOOTER.search(html)
    return m.start() if m else None


def main():
    fixed = skipped = unresolved = 0
    for page in sorted(SITE.rglob("index.html")):
        html = page.read_text("utf-8", errors="replace")
        short = balance(html)
        if short <= 0:
            skipped += 1
            continue
        at = insertion_point(html)
        if at is None:
            print(f"  no safe insertion point: {page.relative_to(SITE)}")
            unresolved += 1
            continue
        page.write_text(html[:at] + "</div>" * short + html[at:], "utf-8")
        fixed += 1
        print(f"  closed {short} div(s): {page.relative_to(SITE)}")
    print(f"repaired: {fixed}, already balanced: {skipped}, unresolved: {unresolved}")


if __name__ == "__main__":
    main()
