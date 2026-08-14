#!/usr/bin/env python3
"""One closing CTA at the end of a service page, not two.

The pages ended with two green bands 28px apart in the same colour, each with
the same "Call (832) 887-8747" button: the service-specific offer block from
the client's own copy, then a generic "Need this fixed today?" band. Two
identical-looking calls to action in a row read as a mistake and dilute both.

Keeps the service-specific block (it names the actual service) and moves the
text-message action into it, so no way to reach TML is lost.

Idempotent.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent / "site"
SMS = "sms:+18328878747"
TEXT_LINK = (f'<a class="tmlcta-call" href="{SMS}" data-book="text" '
             'style="background:#1f2418;color:#fff">&#128172; Send us a text</a>')
BAND_OPEN = '<div class="sp"><div class="sp-wrap"><div class="sp-final">'


def strip_band(html):
    """Remove the generic urgency band, wrapper and all."""
    removed = 0
    while True:
        at = html.find(BAND_OPEN)
        if at == -1:
            return html, removed
        depth, end = len(re.findall(r"<div\b", BAND_OPEN)), None
        for m in re.finditer(r"<div\b|</div>", html[at + len(BAND_OPEN):]):
            depth += 1 if m.group(0) == "<div" else -1
            if depth == 0:
                end = at + len(BAND_OPEN) + m.end()
                break
        if end is None:
            return html, removed
        html = html[:at] + html[end:]
        removed += 1


def add_text_action(html):
    """Give the surviving block a text option if it does not have one."""
    m = re.search(r'<div class="tmlcta-acts">(.*?)</div>', html, re.S)
    if not m or 'data-book="text"' in m.group(1):
        return html, False
    return html[:m.end() - len("</div>")] + TEXT_LINK + html[m.end() - len("</div>"):], True


def main():
    pages = bands = texts = 0
    for page in sorted((SITE / "fixed").rglob("index.html")):
        html = page.read_text("utf-8", errors="replace")
        if '<div class="tmlcta">' not in html:
            continue                      # nothing to merge into; leave the page alone
        new, removed = strip_band(html)
        new, added = add_text_action(new)
        if removed or added:
            page.write_text(new, "utf-8")
            pages += 1
            bands += removed
            texts += int(added)
    print(f"pages updated: {pages}, duplicate bands removed: {bands}, text actions added: {texts}")


if __name__ == "__main__":
    main()
