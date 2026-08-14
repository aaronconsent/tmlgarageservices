#!/usr/bin/env python3
"""Issue 1 (dead links), per Aaron's decision: build real stub pages for the
three gate/overhead services at their linked URLs, remove the four
home-improvement phantom links, repoint the three gate links into /fixed/.
Stub copy is assembled from TML's own published claims (flagged in the
changelog for client review)."""
import re
from pathlib import Path
from collections import Counter

F = Path(__file__).parent / "site" / "fixed"
n = Counter()

SHELL = (F / "contact" / "index.html").read_text("utf-8", errors="replace")
first_section = SHELL.find('<section class="title-section">')
footer_at = SHELL.find('<section class="footer">')
PREFIX = SHELL[:first_section]
SUFFIX = SHELL[footer_at:]

CALL = ('<a href="tel:+18328878747" class="button w-button" '
        'style="margin-top:18px;">☎ CALL NOW — (832) 887-8747</a>')
CHECKS = ("<ul><li>Same day on-time service</li><li>Emergency Services</li>"
          "<li>No extra charges for weekend appointments</li>"
          "<li>Well-trained and insured technicians</li>"
          "<li>100% satisfaction guaranteed</li></ul>")

PAGES = {
    "residential-driveway-gate-services": {
        "title": "Residential Driveway Gate Services | TML Garage Services | Conroe, TX",
        "desc": "Driveway entry gate repair, opener service, and installation for homeowners in Conroe, The Woodlands, Spring, and greater Houston. Call (832) 887-8747.",
        "h1": "Residential Driveway Gate Services",
        "body": (
            "<p>We are a trustworthy, affordable, and always accessible garage door and "
            "driveway entry gate service company. Our residential technicians repair and "
            "install driveway entry gates and gate openers for homeowners throughout "
            "Conroe, The Woodlands, Spring, and the greater Houston area.</p>"
            "<p>What you can expect from TML:</p>" + CHECKS),
    },
    "commercial-overhead-door-services": {
        "title": "Commercial Overhead Door Services | TML Garage Services | Conroe, TX",
        "desc": "Overhead door repair, replacement, and installation for businesses across the greater Houston area. Call TML Garage Services at (832) 887-8747.",
        "h1": "Commercial Overhead Door Services",
        "body": (
            "<p>TML Garage Door Services&rsquo; residential and commercial technicians are "
            "highly proficient at repairing all garage door and opener brands. Our "
            "commercial team services overhead doors for businesses throughout the "
            "greater Houston area &mdash; repair, replacement, and new installation.</p>"
            "<p>What you can expect from TML:</p>" + CHECKS),
    },
    "commercial-gate-opener-services": {
        "title": "Commercial Gate & Opener Services | TML Garage Services | Conroe, TX",
        "desc": "Commercial gate and gate-opener repair, service, and installation across the greater Houston area. Call TML Garage Services at (832) 887-8747.",
        "h1": "Commercial Gate & Opener Services",
        "body": (
            "<p>We are a trustworthy, affordable, and always accessible garage door and "
            "driveway entry gate service company. Our commercial technicians repair, "
            "service, and install gates and gate openers for businesses throughout the "
            "greater Houston area.</p>"
            "<p>What you can expect from TML:</p>" + CHECKS),
    },
}

def build_page(slug, cfg):
    mid = (
        '<div class="page-wrap remove-the-padding-bottom">'
        '<section class="title-section"><div class="w-layout-blockcontainer container w-container">'
        '<div class="title-wrapper"><p class="page-subtitle white">our Garage &amp; Gate Services</p>'
        f'<h1 class="white-heading">{cfg["h1"]}</h1></div></div></section>'
        '<section class="section-3"><div class="w-layout-blockcontainer container w-container">'
        f'<div class="section-inner" style="max-width:760px;">{cfg["body"]}{CALL}'
        '<p style="margin-top:22px;"><a href="/fixed/services" class="text-link">&larr; See all of our services</a></p>'
        "</div></div></section></div>"
    )
    html = PREFIX + mid + SUFFIX
    html = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", html, count=1, flags=re.S)
    html = re.sub(r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")',
                  f"\\g<1>{cfg['desc']}\\2", html, count=1)
    if 'name="description"' not in html:
        html = html.replace("</title>", f'</title><meta name="description" content="{cfg["desc"]}">', 1)
    dest = F / "our-services" / slug / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, "utf-8")
    n["pages_built"] += 1

for slug, cfg in PAGES.items():
    build_page(slug, cfg)

# remove home-improvement phantom links; repoint gate links into /fixed/
REMOVE = ["bathroom-renovations", "flooring", "kitchen-remodeling-2", "complete-home-renovation"]

def remove_anchor(html, frag):
    out, pos, removed = [], 0, 0
    pat = re.compile(r'<a\b[^>]*href="[^"]*%s[^"]*"[^>]*>' % re.escape(frag))
    while True:
        m = pat.search(html, pos)
        if not m:
            out.append(html[pos:])
            break
        end = html.find("</a>", m.end())
        if end == -1:
            out.append(html[pos:])
            break
        out.append(html[pos:m.start()])
        pos = end + 4
        removed += 1
    return "".join(out), removed

for f in F.rglob("index.html"):
    h = orig = f.read_text("utf-8", errors="replace")
    for d in REMOVE:
        h, r = remove_anchor(h, d)
        n["links_removed"] += r
    for slug in PAGES:
        h, r = re.subn(f'href="/our-services/{slug}"', f'href="/fixed/our-services/{slug}"', h)
        n["links_repointed"] += r
    if h != orig:
        f.write_text(h, "utf-8")

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
