#!/usr/bin/env python3
"""Audit round 2 — applied to site/fixed/ only. Each lettered fix maps to a
CHANGELOG.md entry. Prints counts for the log."""
import re
import urllib.parse
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
SITE = ROOT / "site"
F = SITE / "fixed"
n = Counter()

REMOVE_DEAD = ["bathroom-renovations", "flooring", "kitchen-remodeling-2",
               "complete-home-renovation"]
REPOINT = {
    "/our-services/residential-driveway-gate-services": "/fixed/our-services/residential-garage-door-services",
    "/our-services/commercial-overhead-door-services": "/fixed/our-services/commercial-garage-door-installation",
    "/our-services/commercial-gate-opener-services": "/fixed/our-services/commercial-garage-door-installation",
}

BRAND_META = {
    "liftmaster": ("LiftMaster Garage Door Opener Repair & Installation | TML Garage Services | Conroe, TX",
                   "LiftMaster garage door opener repair and installation across Conroe, The Woodlands, Spring, and greater Houston. Same-day service from TML Garage Services — call (832) 887-8747."),
    "genie": ("Genie Garage Door Opener Repair & Installation | TML Garage Services | Conroe, TX",
              "Genie garage door opener repair and installation across Conroe, The Woodlands, Spring, and greater Houston. Same-day service from TML Garage Services — call (832) 887-8747."),
    "chamberlain": ("Chamberlain Garage Door Opener Repair & Installation | TML Garage Services | Conroe, TX",
                    "Chamberlain garage door opener repair and installation across Conroe, The Woodlands, Spring, and greater Houston. Same-day service from TML Garage Services — call (832) 887-8747."),
    "craftsman": ("Craftsman Garage Door Opener Repair & Installation | TML Garage Services | Conroe, TX",
                  "Craftsman garage door opener repair and installation across Conroe, The Woodlands, Spring, and greater Houston. Same-day service from TML Garage Services — call (832) 887-8747."),
}
PAGE_DESC = {
    "contact": "Contact TML Garage Door Services in Conroe, TX. Same-day garage door repair, $69 tune-ups, and financing available — call (832) 887-8747 or send a message.",
    "the-woodlands-tx": "Garage door repair, installation, and opener service in The Woodlands, TX from TML Garage Services. Same-day appointments — call (832) 887-8747.",
    "privacy-policy": "Privacy policy for TML Garage Door Services of Conroe, TX.",
    "terms-conditions": "Terms and conditions for TML Garage Door Services of Conroe, TX.",
    "cookie-policy": "Cookie policy for TML Garage Door Services of Conroe, TX.",
}

OG_IMAGE = "https://tmlgarageservices.aironz.workers.dev/assets/66b2dae9e779df43d0d269c9/66b5115cc6a1fdc1f8b546d6_modern-garage-door-services.jpg"

A = "/assets/66b2dae9e779df43d0d269c9"
REVIEWS_BLOCK = (
    '<div class="tmlfix-reviews">'
    f'<img src="{A}/66b2dae9e779df43d0d26a8a_angies-list-award.png" alt="Angi Super Service Award 2019" loading="lazy">'
    f'<img src="{A}/66b2dae9e779df43d0d26a89_soap-solid-border.png" alt="HomeAdvisor Screened and Approved" loading="lazy">'
    f'<img src="{A}/66b2dae9e779df43d0d26a8b_3year-solid-border.png" alt="HomeAdvisor 3 Years Screened and Approved" loading="lazy">'
    '<p><a href="https://www.homeadvisor.com/rated.elioravitan.108891528.html" target="_blank" rel="noopener">Read our reviews on HomeAdvisor</a>'
    ' &middot; <a href="https://www.facebook.com/tmlhomeimprovement" target="_blank" rel="noopener">Facebook</a></p></div>'
)
TRUSTMARY_EMBED = re.compile(r'<div class="code-embed w-embed w-script"><script src="https://widget\.trustmary\.com/[^"]*"></script></div>')
ELFSIGHT_EMBED = re.compile(r'<div class="code-embed w-embed w-script"><!-- Elfsight[^>]*-->\s*<script src="https://elfsightcdn\.com/platform\.js" async></script>\s*<div class="elfsight-app-[^"]*"[^>]*></div></div>', re.S)

STYLE = ('<style id="tmlfix">'
         '.green-button-floating{left:auto!important;right:14px!important;bottom:14px!important;'
         'box-shadow:0 6px 22px rgba(0,0,0,.35);}'
         '.tmlfix-reviews{display:flex;flex-wrap:wrap;align-items:center;gap:18px 28px;justify-content:center;padding:8px 0;}'
         '.tmlfix-reviews img{height:88px;width:auto;}'
         '.tmlfix-reviews p{width:100%;text-align:center;margin:6px 0 0;font-size:15px;}'
         '.tmlfix-reviews a{color:inherit;font-weight:600;}'
         '</style>')

def alt_from_src(src):
    base = urllib.parse.unquote(src.rsplit("/", 1)[-1])
    base = re.sub(r"\.(png|jpe?g|webp|avif)$", "", base, flags=re.I)
    base = re.sub(r"-p-\d+$", "", base)
    while re.match(r"^[0-9a-f]{16,}[_-]", base, re.I):
        base = re.sub(r"^[0-9a-f]{16,}[_-]", "", base, flags=re.I)
    base = re.sub(r"^[0-9a-f]{8}-[0-9a-f-]{27,}[_-]?", "", base, flags=re.I)
    base = re.sub(r"[-_]+", " ", base).strip()
    letters = sum(c.isalpha() for c in base)
    if letters < 5 or re.match(r"^(img|image|photo|screen ?shot|\d)", base, re.I) or re.search(r"[0-9a-f]{8,}", base, re.I):
        return "TML Garage Services garage door work photo"
    return base[:1].upper() + base[1:]

def fix_srcset(m):
    parts, kept = [p.strip() for p in m.group(1).split(",")], []
    for p in parts:
        url = p.split(" ")[0]
        if url.startswith("/assets/"):
            if (SITE / urllib.parse.unquote(url.lstrip("/").split("?")[0])).exists():
                kept.append(p)
            else:
                n["srcset_removed"] += 1
        else:
            kept.append(p)
    return f'srcset="{", ".join(kept)}"' if kept else ""

def remove_anchor(html, href_frag):
    """remove <a ...href*=frag...>...</a> (anchors don't nest)"""
    out, removed = [], 0
    pos = 0
    pat = re.compile(r'<a\b[^>]*href="[^"]*%s[^"]*"[^>]*>' % re.escape(href_frag))
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

for f in sorted(F.rglob("index.html")):
    h = orig = f.read_text("utf-8", errors="replace")
    rel = f.parent.relative_to(F)
    slug = f.parent.name

    # A1 remove phantom home-improvement links
    for d in REMOVE_DEAD:
        h, r = remove_anchor(h, d)
        n["dead_removed"] += r
    # A2 repoint gate/overhead links to the closest real page
    for old, new in REPOINT.items():
        h, r = re.subn('href="%s"' % re.escape(old), 'href="%s"' % new, h)
        n["dead_repointed"] += r

    # B unique titles + descriptions
    for key, (title, desc) in BRAND_META.items():
        if str(rel).startswith(f"brands/{key}"):
            h, r = re.subn(r"<title>.*?</title>", f"<title>{title}</title>", h, count=1, flags=re.S)
            n["titles"] += r
            if 'name="description"' not in h:
                h = h.replace("</title>", f'</title><meta name="description" content="{desc}">', 1)
                n["descs"] += 1
    if slug in PAGE_DESC and 'name="description"' not in h:
        h = h.replace("</title>", f'</title><meta name="description" content="{PAGE_DESC[slug]}">', 1)
        n["descs"] += 1

    # C og:image -> real absolute image
    h, r = re.subn(r'content="[^"]*avtar[^"]*"(\s*property="og:image")', f'content="{OG_IMAGE}"\\1', h)
    h, r2 = re.subn(r'(property="og:image"\s*content=")[^"]*avtar[^"]*(")', f"\\g<1>{OG_IMAGE}\\2", h)
    n["og"] += r + r2

    # D heading structure: blogs get a real h1; extra h1s demoted to h2
    if str(rel).startswith("blogs/"):
        h, r = re.subn(r'<div class="blog-name">', '<h1 class="blog-name">', h, count=1)
        if r:
            i = h.find('<h1 class="blog-name">')
            j = h.find("</div>", i)
            h = h[:j] + "</h1>" + h[j + 6:]
            n["blog_h1"] += 1
    parts = re.split(r"(<h1\b)", h)
    if h.count("<h1") > 1:
        seen = 0
        rebuilt = []
        idx = 0
        while idx < len(parts):
            if parts[idx] == "<h1":
                seen += 1
                if seen > 1:
                    seg = parts[idx + 1]
                    seg = seg.replace("</h1>", "</h2>", 1)
                    rebuilt.append("<h2" + seg)
                    n["h1_demoted"] += 1
                    idx += 2
                    continue
            rebuilt.append(parts[idx])
            idx += 1
        h = "".join(rebuilt)

    # E contact hero: end the truncated h1 at its first complete sentence
    if slug == "contact":
        h, r = re.subn(
            r'(<h1[^>]*>)<strong>TML Garage Door Services</strong> is here to help\..*?</h1>',
            r'\1<strong>TML Garage Door Services</strong> is here to help.</h1>'
            r'<p style="color:#fff;max-width:62ch;">We proudly provide fast, reliable, and affordable '
            r'garage door services throughout the Houston area.</p>',
            h, flags=re.S)
        n["contact_h1"] += r

    # F financing subtitle contrast
    h, r = re.subn(r'<p class="page-subtitle">Renovate Now\. Pay Later\.</p>',
                   '<p class="page-subtitle" style="color:#fff;opacity:1;">Renovate Now. Pay Later.</p>', h)
    n["contrast"] += r

    # J reviews embeds -> static proof block
    h, r = TRUSTMARY_EMBED.subn(REVIEWS_BLOCK, h)
    n["trustmary"] += r
    h, r = ELFSIGHT_EMBED.subn(REVIEWS_BLOCK, h)
    n["elfsight"] += r

    # I srcset entries pointing at files that don't exist
    h = re.sub(r'srcset="([^"]*)"', fix_srcset, h)

    # H alt text for content images missing/empty alt
    def add_alt(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]*)"', tag)
        if not src or not re.search(r"\.(png|jpe?g|webp|avif)(\?|$|\")", src.group(1), re.I):
            return tag
        if re.search(r'alt="[^"]+"', tag):
            return tag
        alt = alt_from_src(src.group(1))
        n["alts"] += 1
        if 'alt=""' in tag:
            return tag.replace('alt=""', f'alt="{alt}"', 1)
        return tag[:-1] + f' alt="{alt}">'
    h = re.sub(r"<img\b[^>]*>", add_alt, h)

    # K style overrides (emergency button reposition + reviews block styles)
    if "tmlfix" not in h:
        h = h.replace("</head>", STYLE + "</head>", 1)
        n["styled"] += 1

    if h != orig:
        f.write_text(h, "utf-8")
        n["pages_changed"] += 1

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
