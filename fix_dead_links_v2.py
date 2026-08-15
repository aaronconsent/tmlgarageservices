#!/usr/bin/env python3
"""Retire the 44 links that go nowhere.

Every one of them was an href="#", which scrolls the page to the top and looks,
to a visitor, like the site is broken. Five distinct causes:

  * 37 - the Angi award badge in the footer. TML has no verified Angi profile
    URL on file, so the badge becomes a plain image rather than a link to an
    invented address. Give me the profile URL and it becomes a link again.
  * 3 - "info@tml-homeimprovement.com" on the kitchen project pages: the old
    company's address, and not even wired as a mailto. Now the real address.
  * 2 - "Explore Portfolio" on the home and about pages. It pointed at the
    kitchen remodel gallery, which belongs to the other business. It sits
    directly beside "VIEW ALL SERVICES", so removing it loses nothing.
  * 1 - "Contact us" button on the Woodlands service-area page.
  * 1 - "here" in the terms page, in the sentence referring to the privacy
    policy.

Idempotent.
"""
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

EMAIL = "info@tmlgarageservices.com"
n = Counter()


def unlink_badge(html):
    """Angi badge: keep the image, drop the link that goes nowhere."""
    def repl(m):
        n["angi badge unlinked"] += 1
        return f'<span class="w-inline-block">{m.group("img")}</span>'
    return re.sub(
        r'<a href="#"[^>]*>\s*(?P<img><img[^>]*angies-list-award[^>]*>)\s*</a>',
        repl, html, flags=re.S)


def fix_old_email(html):
    def repl(m):
        n["old company e-mail corrected"] += 1
        return f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
    return re.sub(r'<a href="#">\s*info@tml-homeimprovement\.com\s*</a>', repl, html)


def drop_portfolio(html):
    def repl(m):
        n["dead Explore Portfolio removed"] += 1
        return ""
    return re.sub(r'<a href="#" class="text-link">[^<]*Explore Portfolio[^<]*</a>', repl,
                  html, flags=re.I)


def fix_contact_btn(html):
    def repl(m):
        n["Contact us button pointed at /contact"] += 1
        return m.group(0).replace('href="#"', 'href="/fixed/contact"', 1)
    return re.sub(r'<a href="#" class="primary-btn-3 w-button"[^>]*>.*?</a>', repl,
                  html, flags=re.S)


def fix_here(html):
    def repl(m):
        n["privacy-policy reference linked"] += 1
        return '<a href="/fixed/privacy-policy">here</a>'
    # the export left a target="_new" on it, so the attributes are not in one order
    return re.sub(r'<a\b[^>]*href="#"[^>]*>\s*here\s*</a>', repl, html)


def main():
    pages = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        for fn in (unlink_badge, fix_old_email, drop_portfolio, fix_contact_btn, fix_here):
            html = fn(html)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
    for k, v in n.most_common():
        print(f"  {v:>3}  {k}")
    left = sum('href="#"' in p.read_text(errors="replace") for p in F.rglob("index.html"))
    print(f"pages changed: {pages}; pages still holding a dead link: {left}")


if __name__ == "__main__":
    main()
