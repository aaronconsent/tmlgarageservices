#!/usr/bin/env python3
"""Remove Webflow leftovers from the Fixed site, one approved step at a time.

Each step is a named, self-contained transform. Only the steps listed in
APPROVED run, so nothing goes in without a decision. Every step must be
visually inert — it removes something dead, not something the page uses.

Idempotent: a page already clean is left untouched.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

# steps the owner has signed off on, in the order they were approved
APPROVED = [
    "dead-script",
    "self-host-fonts",
]


def dead_script(html):
    """A Webflow tracking stub that was never exported: the path 404s on every
    page load. Nothing reads it, nothing depends on it."""
    return re.subn(r'<script[^>]+src="/g0lnomhfn3mg[^"]*"[^>]*>\s*</script>', "", html)


FONT_LINK = ('<link rel="preload" href="/assets/fonts/Inter-400-latin.woff2" as="font" '
             'type="font/woff2" crossorigin>'
             '<link rel="preload" href="/assets/fonts/BebasNeue-400-latin.woff2" as="font" '
             'type="font/woff2" crossorigin>'
             '<link rel="stylesheet" href="/assets/fonts/fonts.css">')


def self_host_fonts(html):
    """Drop the Google WebFont loader for a local stylesheet.

    The loader pulled a script from ajax.googleapis.com which then requested six
    families at every weight — about 36 font files' worth — for the four faces
    the site renders. It is render-blocking, so text waited on a third-party
    round-trip. The replacement serves the same faces from this site."""
    n = 0
    html, a = re.subn(r'<script[^>]+src="https://ajax\.googleapis\.com/ajax/libs/webfont/[^"]*"[^>]*>\s*</script>', "", html)
    html, b = re.subn(r'<script[^>]*>\s*WebFont\.load\(.*?\);?\s*</script>', "", html, flags=re.S)
    n += a + b
    if n and "/assets/fonts/fonts.css" not in html:
        html = html.replace("</head>", FONT_LINK + "</head>", 1)
    return html, n


def last_published(html):
    """The '<!-- Last Published: ... -->' banner Webflow stamps on every export."""
    return re.subn(r"<!--\s*Last Published:.*?-->", "", html, flags=re.S)


def wf_identifiers(html):
    """data-wf-domain / -page / -site / -collection / -item on <html>. Webflow's
    own runtime reads these, so this step must run only after the Webflow JS is
    gone. Not approved yet."""
    return re.subn(r'\sdata-wf-(?:domain|page|site|collection|item)="[^"]*"', "", html)


STEPS = {
    "dead-script": ("dead 404 script tag", dead_script),
    "last-published": ("Last Published comment", last_published),
    "wf-identifiers": ("data-wf-* identifiers", wf_identifiers),
    "self-host-fonts": ("Google WebFont loader -> self-hosted", self_host_fonts),
}


def main():
    steps = sys.argv[1:] or APPROVED
    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        sys.exit(f"unknown step(s): {', '.join(unknown)}\nknown: {', '.join(STEPS)}")

    for name in steps:
        label, fn = STEPS[name]
        pages = hits = 0
        for f in sorted(F.rglob("index.html")):
            html = f.read_text("utf-8", errors="replace")
            new, n = fn(html)
            if n:
                f.write_text(new, "utf-8")
                pages += 1
                hits += n
        print(f"  {label}: removed {hits} on {pages} pages")


if __name__ == "__main__":
    main()
