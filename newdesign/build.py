#!/usr/bin/env python3
"""Render the TML redesign: content.json + templates -> site/new/

Every legacy route gets a counterpart at /new/<path> so the version toggle
always has somewhere to land. Content is ported verbatim from the legacy
site (content.json); only structure, hierarchy, and dead links change.
"""
import html as htmllib
import json
import re
import shutil
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = SITE / "new"
CONTENT = json.loads((ROOT / "content.json").read_text("utf-8"))

PHONE_DISPLAY = "(832) 887-8747"
PHONE_HREF = "tel:+18328878747"
BOOK = "https://calendar.app.google/juqN1UNcknf4KZ9v9"
EMAIL = "info@tmlgarageservices.com"
ADDRESS = "15232 Saddlewood Dr, Conroe, TX 77384"
FB = "https://www.facebook.com/tmlhomeimprovement"
IG = "https://www.instagram.com/tml_homeimprovement_llc/?hl=en"
YT = "https://www.youtube.com/@TMLHomeImprovement"
HA = "https://www.homeadvisor.com/rated.elioravitan.108891528.html"

A = "/assets/66b2dae9e779df43d0d269c9"
LOGO = f"{A}/66b2f5077df3a3b06a15a1bd_TMLGarageServices-Logo-web.svg"
LOGO_W = f"{A}/66b513d8d31e80c12f51920d_TMLGarageServices-Logo-web-wh.svg"
FAVICON = f"{A}/66b51dc4282e5ee4d47ceef1_TML-garage-services-favicon-32.png"
HERO_POSTER = f"{A}/6a6638dbf310548aa6535691_copy_AE586C56-1DE3-4700-978C-82BBC75C202F_poster.0000000.jpg"
HERO_MP4 = f"{A}/6a6638dbf310548aa6535691_copy_AE586C56-1DE3-4700-978C-82BBC75C202F_mp4.mp4"
BADGES = [
    (f"{A}/66b2dae9e779df43d0d26a8a_angies-list-award.png", "Angi Super Service Award 2019"),
    (f"{A}/66b2dae9e779df43d0d26a89_soap-solid-border.png", "HomeAdvisor Screened & Approved"),
    (f"{A}/66b2dae9e779df43d0d26a8b_3year-solid-border.png", "HomeAdvisor 3 Years Screened & Approved"),
]

SERVICES = [
    ("/our-services/residential-garage-door-services", "Residential Garage Door Services",
     f"{A}/6a542a3cc1d76f4028c06fb8_2C6A44D6-3090-4449-81C8-D96132FB7ED7.PNG",
     "New doors, repairs, and tune-ups for your home."),
    ("/our-services/garage-door-spring-replacement", "Garage Door Spring Replacement",
     f"{A}/6a543368b89f6b6fe88b1284_1F1EB104-997F-40F2-AAC8-9630A0DF66CC.PNG",
     "Snapped spring? Same-day replacement, done safely."),
    ("/our-services/garage-door-opener-installation", "Garage Door Opener Services",
     f"{A}/6a542e2ec6b8791b21582f07_Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png",
     "LiftMaster, Genie, Chamberlain & Craftsman openers."),
    ("/our-services/commercial-garage-door-installation", "Commercial Garage Door Installation",
     f"{A}/6a543355c034cb7d551b686f_E796B398-C84E-4B4B-8948-E05CBCB1864E.PNG",
     "Overhead doors and gates for Houston businesses."),
]
BRANDS = [
    ("/brands/liftmaster-garage-door-opener-repair-and-installation", "LiftMaster"),
    ("/brands/genie-garage-door-opener-repair-and-installation", "Genie"),
    ("/brands/chamberlain-garage-door-opener-repair-and-installation", "Chamberlain"),
    ("/brands/craftsman-garage-door-opener-repair-and-installation", "Craftsman"),
]
AREAS = ["The Woodlands", "Conroe", "Spring", "Magnolia", "Tomball", "Montgomery", "Willis", "Houston"]

esc = htmllib.escape

def nw(path: str) -> str:
    """Map a legacy path to its /new counterpart."""
    path = path.strip()
    return "/new" if path == "/" else "/new" + path

def srcset(src: str) -> str:
    """Build a srcset from the -p-500/-p-800/-p-1080 variants Webflow shipped."""
    m = re.match(r"^(.*)(\.(?:png|jpg|jpeg|webp|PNG|JPG|JPEG))$", src)
    if not m:
        return ""
    base, ext = m.groups()
    parts = []
    for w in (500, 800, 1080, 1600):
        cand = f"{base}-p-{w}{ext}"
        disk = SITE / urllib.parse.unquote(cand.lstrip("/"))
        if disk.exists():
            parts.append(f"{cand} {w}w")
    full = SITE / urllib.parse.unquote(src.lstrip("/"))
    if parts and full.exists():
        parts.append(f"{src} 1920w")
    return ", ".join(parts)

def img_tag(src, alt="", cls="", lazy=True, sizes="(max-width: 860px) 100vw, 50vw"):
    ss = srcset(src)
    return (f'<img src="{src}" alt="{esc(alt)}"'
            + (f' class="{cls}"' if cls else "")
            + (f' srcset="{ss}" sizes="{sizes}"' if ss else "")
            + (' loading="lazy" decoding="async"' if lazy else "") + ">")

def links(text: str) -> str:
    """Convert extractor [[href|label]] markers into anchors, mapped to /new."""
    out = esc(text)
    def sub(m):
        href = m.group(1).replace(" ", "")
        return f'<a href="{nw(href)}">{m.group(2)}</a>'
    return re.sub(r"\[\[([^|\]]+)\|(.*?)\]\]", sub, out)

ARROW = '<svg width="18" height="14" viewBox="0 0 18 14" fill="none" aria-hidden="true"><path d="M11 1l6 6-6 6M17 7H1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
GTM = """<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-M5ZMMSJX');</script>"""
GTM_NS = """<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-M5ZMMSJX" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>"""

def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/new/style.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"LocalBusiness","name":"TML Garage Door Services","telephone":"+18328878747","email":"{EMAIL}","address":{{"@type":"PostalAddress","streetAddress":"15232 Saddlewood Dr","addressLocality":"Conroe","addressRegion":"TX","postalCode":"77384"}},"areaServed":["The Woodlands TX","Conroe TX","Spring TX","Houston TX"],"url":"https://www.tmlgarageservices.com/"}}</script>
{GTM}
</head>
<body>
{GTM_NS}
"""

def nav_dropdown(label, items):
    lis = "".join(f'<a href="{href}">{esc(t)}</a>' for href, t in items)
    return f"<details><summary>{label}</summary><div>{lis}</div></details>"

def header():
    svc_items = [(nw(h), t) for h, t, _, _ in SERVICES] + [("/new/services", "All services →")]
    brand_items = [(nw(h), f"{t} repair & installation") for h, t in BRANDS]
    return f"""
<header class="top">
  <div class="wrap top-in">
    <a class="top-logo" href="/new" aria-label="TML Garage Services home"><img src="{LOGO}" alt="TML Garage Services" width="220" height="50"></a>
    <nav class="top-nav" aria-label="Main">
      {nav_dropdown("Services", svc_items)}
      {nav_dropdown("Brands", brand_items)}
      <a href="/new/service-areas/the-woodlands-tx">Service areas</a>
      <a href="/new/about">About</a>
      <a href="/new/contact">Contact</a>
    </nav>
    <div class="top-cta">
      <a class="btn btn-ghost" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Book online</a>
      <a class="btn btn-vis" href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a>
      <button class="menu-btn" id="menu-open" aria-expanded="false" aria-controls="menu" aria-label="Open menu">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>
      </button>
    </div>
  </div>
</header>
<div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="menu-head">
    <img src="{LOGO_W}" alt="TML Garage Services">
    <button class="menu-close" id="menu-close" aria-label="Close menu">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>
    </button>
  </div>
  <ul class="menu-links">
    <li><a href="/new">Home</a></li>
    <li><a href="/new/services">Services</a>
      <ul class="menu-sub">{"".join(f'<li><a href="{nw(h)}">{esc(t)}</a></li>' for h, t, _, _ in SERVICES)}</ul></li>
    <li><a href="{nw(BRANDS[0][0])}">Brands</a>
      <ul class="menu-sub">{"".join(f'<li><a href="{nw(h)}">{esc(t)}</a></li>' for h, t in BRANDS)}</ul></li>
    <li><a href="/new/service-areas/the-woodlands-tx">Service areas</a></li>
    <li><a href="/new/about">About</a></li>
    <li><a href="/new/contact">Contact</a></li>
  </ul>
  <div class="menu-foot">
    <a class="btn btn-vis" href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a>
    <a class="btn btn-ghost-light" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Book online</a>
  </div>
</div>
"""

CALLBAR = f"""
<div class="callbar" role="region" aria-label="Quick contact">
  <a class="btn btn-vis" href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a>
  <a class="btn btn-ghost-light" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Book online</a>
</div>
"""

def cta_band(heading="Broken door? We're local and we answer."):
    return f"""
<section class="cta-band">
  <div class="wrap">
    <div class="rev">
      <h2>{esc(heading)}</h2>
      <a class="hero-phone" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
    </div>
    <div class="cta-actions rev rev-d1">
      <a class="btn btn-vis" href="{PHONE_HREF}">Call now</a>
      <a class="btn btn-ghost-light" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Book online</a>
    </div>
  </div>
</section>
"""

SOCIAL_SVG = {
    "Facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 21v-7h2.4l.4-3h-2.8V9.1c0-.9.3-1.5 1.6-1.5h1.3V4.9c-.3 0-1.1-.1-2-.1-2 0-3.4 1.2-3.4 3.5V11H8.5v3h2.5v7z"/></svg>',
    "Instagram": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8.4A3.6 3.6 0 1 0 12 15.6 3.6 3.6 0 0 0 12 8.4zm0 5.9a2.3 2.3 0 1 1 0-4.6 2.3 2.3 0 0 1 0 4.6zM17 6.2a.9.9 0 1 0 0 1.8.9.9 0 0 0 0-1.8zM21 12c0-1.2 0-2.5-.1-3.7a5 5 0 0 0-1.3-3.4A5 5 0 0 0 16.2 3.6C15 3.5 13.2 3.5 12 3.5s-3 0-4.2.1a5 5 0 0 0-3.4 1.3A5 5 0 0 0 3.1 8.3C3 9.5 3 10.8 3 12s0 2.5.1 3.7a5 5 0 0 0 1.3 3.4 5 5 0 0 0 3.4 1.3c1.2.1 3 .1 4.2.1s3 0 4.2-.1a5 5 0 0 0 3.4-1.3 5 5 0 0 0 1.3-3.4c.1-1.2.1-2.5.1-3.7zm-1.7 4.4a3.3 3.3 0 0 1-1.9 1.9c-1.3.5-4.4.4-5.4.4s-4.1.1-5.4-.4a3.3 3.3 0 0 1-1.9-1.9C4.2 15.1 4.3 12 4.3 12s-.1-3.1.4-4.4a3.3 3.3 0 0 1 1.9-1.9C7.9 5.2 11 5.3 12 5.3s4.1-.1 5.4.4a3.3 3.3 0 0 1 1.9 1.9c.5 1.3.4 4.4.4 4.4s.1 3.1-.4 4.4z"/></svg>',
    "YouTube": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15.2V8.8L15.5 12z"/></svg>',
}

def footer():
    return f"""
<div class="slats slats--dark" style="background-color: var(--pit);"></div>
<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <p class="foot-logo"><img src="{LOGO_W}" alt="TML Garage Services"></p>
        <p>Family-owned garage door repair &amp; installation serving The Woodlands, Conroe, Spring, and the greater Houston area.</p>
        <div class="foot-social">
          <a href="{FB}" aria-label="Facebook" rel="noopener" target="_blank">{SOCIAL_SVG["Facebook"]}</a>
          <a href="{IG}" aria-label="Instagram" rel="noopener" target="_blank">{SOCIAL_SVG["Instagram"]}</a>
          <a href="{YT}" aria-label="YouTube" rel="noopener" target="_blank">{SOCIAL_SVG["YouTube"]}</a>
        </div>
      </div>
      <div>
        <h4>Services</h4>
        <ul>{"".join(f'<li><a href="{nw(h)}">{esc(t)}</a></li>' for h, t, _, _ in SERVICES)}
        <li><a href="/new/services">All services</a></li></ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="/new/about">About us</a></li>
          <li><a href="/new/service-areas/the-woodlands-tx">Service areas</a></li>
          {"".join(f'<li><a href="{nw(h)}">{esc(t)} openers</a></li>' for h, t in BRANDS[:2])}
          <li><a href="/new/schedule-consult">Schedule service</a></li>
          <li><a href="/new/contact">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Get in touch</h4>
        <a class="contact-phone" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p>{ADDRESS}</p>
      </div>
    </div>
    <div class="foot-base">
      <span>© 2026 TML Garage Door Services. All rights reserved.</span>
      <a href="/new/privacy-policy">Privacy policy</a>
      <a href="/new/terms-conditions">Terms &amp; conditions</a>
      <a href="/new/cookie-policy">Cookie policy</a>
    </div>
  </div>
</footer>
{CALLBAR}
<script src="/new/app.js" defer></script>
<script src="/switch.js" defer></script>
</body>
</html>
"""

def write(path, body):
    dest = OUT / "index.html" if path == "/" else OUT / path.strip("/") / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, "utf-8")

# ---------------------------------------------------------------- home ----
def build_home():
    body = head("TML Garage Door Services | The Woodlands, Conroe, Spring, Houston TX | Garage Door Repair, Installation, and Service",
                CONTENT["/"]["meta"].get("description", "Garage door repair, installation, and service across the greater Houston area."))
    body += header()
    body += f"""
<main id="main">
<section class="hero">
  <div class="hero-media">
    <video autoplay muted loop playsinline preload="metadata" poster="{HERO_POSTER}">
      <source src="{HERO_MP4}" type="video/mp4">
    </video>
  </div>
  <div class="wrap hero-in">
    <p class="hero-kicker">The Woodlands · Conroe · Spring · Greater Houston</p>
    <h1>Garage door repair &amp; installation</h1>
    <p class="hero-sub">Broken spring, dead opener, or a brand-new door — TML Garage Door Services is your local, family-owned crew. Same-day service, honest pricing.</p>
    <a class="hero-phone" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
    <div class="hero-ctas">
      <a class="btn btn-vis" href="{PHONE_HREF}">Call now — we answer</a>
      <a class="btn btn-ghost-light" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Book online</a>
    </div>
    <ul class="hero-note">
      <li>Same-day &amp; emergency service</li>
      <li>No weekend surcharge</li>
      <li>Insured technicians</li>
    </ul>
  </div>
</section>
<div class="slats"></div>

<section class="sec" id="services">
  <div class="wrap">
    <div class="sec-head rev">
      <h2>Our garage door services</h2>
      <p>Residential and commercial technicians proficient in repairing all garage door and opener brands — and installing new ones.</p>
    </div>
    <div class="svc-grid">
      {"".join(f'''<a class="svc rev rev-d{i}" href="{nw(h)}">
        {img_tag(img, t, sizes="(max-width: 640px) 100vw, (max-width: 1100px) 50vw, 25vw")}
        <div class="svc-body"><h3>{esc(t)}</h3><p style="margin:.3rem 0 0;color:oklch(88% .03 128)">{esc(blurb)}</p>
        <span class="svc-go">See details {ARROW}</span></div>
      </a>''' for i, (h, t, img, blurb) in enumerate(SERVICES))}
    </div>
  </div>
</section>

<section class="sec sec-forest">
  <div class="wrap promise">
    <div class="rev">
      <h2>What you can expect from TML</h2>
      <p style="color: var(--on-dark-muted); font-size: var(--step-1); margin: 1rem 0 0;">We are a trustworthy, affordable, and always accessible garage door and driveway entry gate service company.</p>
      <div style="margin-top: 1.6rem;"><a class="btn btn-vis" href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a></div>
    </div>
    <ul class="checks rev rev-d1">
      <li>Same-day, on-time service</li>
      <li>Emergency services</li>
      <li>No extra charge for weekend appointments</li>
      <li>The owner or a live rep answers every call</li>
      <li>Friendly, professional service from first call to job done</li>
      <li>Quality workmanship on every job</li>
      <li>Well-trained and insured technicians</li>
      <li>100% satisfaction guaranteed</li>
    </ul>
  </div>
</section>

<section class="sec">
  <div class="wrap split">
    <div class="rev">{img_tag(f"{A}/6a6f95756ecb7a47b54e82e8_IMG_3555.jpg", "TML technician installing a garage door opener")}</div>
    <div class="split-copy rev rev-d1">
      <h2>A local family company, not a call center</h2>
      <p class="lead" style="font-size: var(--step-1); color: var(--ink); margin: 1rem 0;">At TML Garage Door Services, we are committed to delivering exceptional service and quality workmanship for all your garage door and gate needs.</p>
      <p>Expert technicians trained to handle any garage door or gate issue. Transparent, upfront pricing with no hidden fees. Same-day service, because a stuck door can't wait. When you choose TML, you're choosing a company that values excellence, professionalism, and integrity.</p>
      <p style="margin-top: 1.4rem;"><a class="btn btn-olive" href="/new/about">More about us</a></p>
    </div>
  </div>
</section>

<section class="sec sec-steel">
  <div class="wrap">
    <div class="sec-head rev">
      <h2>Every major opener brand</h2>
      <p>Factory-trusted parts and technicians who know each system inside out.</p>
    </div>
    <div class="brand-row">
      {"".join(f'''<a class="brand-card rev rev-d{i}" href="{nw(h)}"><b>{esc(t)}</b><span>Opener repair &amp; installation</span><span class="svc-go">Details {ARROW}</span></a>''' for i, (h, t) in enumerate(BRANDS))}
    </div>
  </div>
</section>

<section class="sec sec-forest">
  <div class="wrap">
    <div class="sec-head rev">
      <h2>Serving the greater Houston area</h2>
      <p>Local to The Woodlands, Conroe, and Spring — and on the road across the metro every day.</p>
    </div>
    <ul class="areas rev rev-d1">
      <li><a class="is-page" href="/new/service-areas/the-woodlands-tx">The Woodlands, TX</a></li>
      {"".join(f"<li><span>{a}, TX</span></li>" for a in AREAS[1:])}
    </ul>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head rev">
      <h2>Rated where it counts</h2>
      <p>Real awards from real customers — see for yourself.</p>
    </div>
    <div class="badges rev rev-d1">
      {"".join(f'<figure>{img_tag(b, alt)}</figure>' for b, alt in BADGES)}
      <figure><p class="badge-txt">Read our reviews<small><a href="{HA}" rel="noopener" target="_blank">HomeAdvisor</a> · <a href="{FB}" rel="noopener" target="_blank">Facebook</a></small></p></figure>
    </div>
  </div>
</section>
{cta_band()}
</main>
"""
    body += footer()
    write("/", body)

# ------------------------------------------------------------ articles ----
ICON_PAT = re.compile(r"(ic-|Play-|Pause|right-white|chevron|arrow)", re.I)
CUT_PAT = re.compile(r"(LET.S WORK TOGETHER|Clients Review|^Testimonials$|QUALITY MEETS EFFICIENCY|^Our Services$|^Similar Project|^Related$)", re.I)
CTA_PAT = re.compile(r"(CALL FOR FAST SERVICE|CLICK HERE TO BOOK|SCHEDULE ONLINE|BOOK ONLINE NOW|GET A QUOTE)", re.I)

def clean_blocks(page):
    """De-dupe, drop icons/shared-tail sections, stop at the contact tail."""
    seen_prev = None
    out = []
    for b in page["blocks"]:
        if b["t"] == "img":
            if ICON_PAT.search(b["src"]) or b["src"].endswith(".svg"):
                continue
            key = ("img", b["src"])
        else:
            txt = b["x"].strip()
            if not txt:
                continue
            if CUT_PAT.search(txt):
                break
            if CTA_PAT.search(txt):
                continue
            key = (b["t"], txt.lower())
        if key == seen_prev:
            continue
        seen_prev = key
        out.append(b)
    return out

def render_blocks(blocks, gallery=False, midcall_at=None):
    out, i, li_open = [], 0, False
    n = 0
    for idx, b in enumerate(blocks):
        if b["t"] == "li":
            if not li_open:
                out.append("<ul>")
                li_open = True
            out.append(f"<li>{links(b['x'])}</li>")
            continue
        if li_open:
            out.append("</ul>")
            li_open = False
        if b["t"] == "img":
            # group runs of images into a gallery grid
            if gallery:
                run = [b]
                j = idx + 1
                while j < len(blocks) and blocks[j]["t"] == "img":
                    run.append(blocks[j])
                    j += 1
                if len(run) >= 2 and not getattr(render_blocks, "_in_run", False):
                    pass  # handled below via simple approach
            out.append(img_tag(b["src"], b.get("alt", "")))
        elif b["t"] == "h1":
            out.append(f"<h2>{links(b['x'])}</h2>")
        elif b["t"] in ("h2", "h3", "h4", "h5"):
            tag = "h2" if b["t"] == "h2" else "h3"
            out.append(f"<{tag}>{links(b['x'])}</{tag}>")
        elif b["t"] == "blockquote":
            out.append(f"<blockquote>{links(b['x'])}</blockquote>")
        else:
            out.append(f"<p>{links(b['x'])}</p>")
        n = idx + 1
        if midcall_at and n == midcall_at:
            out.append(f"""<div class="midcall"><strong>Need it fixed today?</strong>
<div class="cta-actions"><a class="btn btn-vis" href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a>
<a class="btn btn-ghost" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Book online</a></div></div>""")
    if li_open:
        out.append("</ul>")
    return "\n".join(out)

def group_galleries(html_str):
    """Collapse 2+ consecutive top-level <img> tags into a .shots grid."""
    pat = re.compile(r"(?:<img [^>]*>\s*){2,}", re.S)
    def sub(m):
        return f'<div class="shots">{m.group(0)}</div>'
    return pat.sub(sub, html_str)

def title_of(path, page):
    for b in page["blocks"]:
        if b["t"] == "h1" and b["x"].strip():
            return b["x"].strip()
    t = page["title"].split("|")[0].strip()
    return t or path.rsplit("/", 1)[-1].replace("-", " ").title()

def build_article(path, crumb_label, crumb_href=None, narrow=False, gallery=False, midcall=False, lede_from_blocks=True):
    page = CONTENT[path]
    blocks = clean_blocks(page)
    h1 = title_of(path, page)
    lede = ""
    body_blocks = []
    took_lede = False
    for b in blocks:
        if b["t"] == "h1" and b["x"].strip().lower() == h1.strip().lower():
            continue
        if b["t"] == "p" and len(b["x"].strip()) <= 2:
            continue
        if lede_from_blocks and not took_lede and b["t"] == "p" and 90 < len(b.get("x", "")) < 240:
            lede = b["x"]
            took_lede = True
            continue
        body_blocks.append(b)
    # drop legacy eyebrow labels: short un-punctuated p right before a heading
    pruned = []
    for i, b in enumerate(body_blocks):
        if (b["t"] == "p" and len(b["x"]) <= 42 and not re.search(r"[.!?]", b["x"])
                and (i == 0 or (i + 1 < len(body_blocks) and body_blocks[i + 1]["t"] in ("h2", "h3", "h4")))):
            continue
        pruned.append(b)
    body_blocks = pruned
    mid = max(6, len(body_blocks) // 2) if midcall else None
    art = render_blocks(body_blocks, midcall_at=mid)
    if gallery:
        art = group_galleries(art)
    wrap_cls = "wrap-narrow" if narrow else "wrap-narrow"
    crumb = f'<a href="{crumb_href}">{esc(crumb_label)}</a>' if crumb_href else esc(crumb_label)
    body = head(page["title"] or h1, page["meta"].get("description", lede[:150]))
    body += header()
    body += f"""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumb"><a href="/new">Home</a> / {crumb}</p>
    <h1>{esc(h1)}</h1>
    {f'<p class="lede">{links(lede)}</p>' if lede else ''}
  </div>
</section>
<div class="slats"></div>
<article class="article">
  <div class="{wrap_cls}">
    {art}
  </div>
</article>
{cta_band()}
</main>
"""
    body += footer()
    write(path, body)

# ------------------------------------------------------- services hub ----
def build_services_hub():
    page = CONTENT["/services"]
    body = head(page["title"], page["meta"].get("description", "Garage door services in Conroe, TX and the greater Houston area."))
    body += header()
    body += f"""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumb"><a href="/new">Home</a> / What we do</p>
    <h1>Our services</h1>
    <p class="lede">Repair, replacement, new installation, and maintenance — residential and commercial, all brands.</p>
  </div>
</section>
<div class="slats"></div>
<section class="sec">
  <div class="wrap">
    <div class="svc-grid">
      {"".join(f'''<a class="svc rev rev-d{i}" href="{nw(h)}">
        {img_tag(img, t, sizes="(max-width: 640px) 100vw, 50vw")}
        <div class="svc-body"><h3>{esc(t)}</h3><p style="margin:.3rem 0 0;color:oklch(88% .03 128)">{esc(blurb)}</p>
        <span class="svc-go">See details {ARROW}</span></div>
      </a>''' for i, (h, t, img, blurb) in enumerate(SERVICES))}
    </div>
    <div class="sec-head rev" style="margin-top: var(--space-sm);">
      <h2 style="font-size: var(--step-3);">Opener brands we service</h2>
    </div>
    <div class="brand-row">
      {"".join(f'''<a class="brand-card rev" href="{nw(h)}"><b>{esc(t)}</b><span>Opener repair &amp; installation</span><span class="svc-go">Details {ARROW}</span></a>''' for h, t in BRANDS)}
    </div>
  </div>
</section>
{cta_band()}
</main>
"""
    body += footer()
    write("/services", body)

# ---------------------------------------------------- contact/schedule ----
FORM = f"""
<form class="form" id="lead-form">
  <div class="form-row">
    <label>First name<input name="first" autocomplete="given-name" required></label>
    <label>Last name<input name="last" autocomplete="family-name" required></label>
  </div>
  <div class="form-row">
    <label>Phone<input name="phone" type="tel" autocomplete="tel" required></label>
    <label>Email<input name="email" type="email" autocomplete="email"></label>
  </div>
  <label>What's going on with your door?<textarea name="msg" rows="4"></textarea></label>
  <button class="btn btn-olive" type="submit">Send message</button>
  <p class="form-note">Sends via your email app to {EMAIL}. In a hurry? <a href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a>.</p>
</form>
<script>
document.getElementById('lead-form').addEventListener('submit', function (e) {{
  e.preventDefault();
  var f = new FormData(this);
  var body = 'Name: ' + f.get('first') + ' ' + f.get('last') + '%0APhone: ' + f.get('phone') +
             '%0AEmail: ' + (f.get('email') || '-') + '%0A%0A' + encodeURIComponent(f.get('msg') || '');
  location.href = 'mailto:{EMAIL}?subject=' + encodeURIComponent('Service request from the website') + '&body=' + body;
}});
</script>
"""

def build_contact():
    page = CONTENT["/contact"]
    body = head(page["title"], page["meta"].get("description", "Contact TML Garage Door Services."))
    body += header()
    body += f"""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumb"><a href="/new">Home</a> / Contact</p>
    <h1>Talk to a real person</h1>
    <p class="lede">Need fast, reliable garage door service? Whether it's a repair, a new installation, or a question — the owner or a live rep answers every call.</p>
  </div>
</section>
<div class="slats"></div>
<section class="sec">
  <div class="wrap contact-grid">
    <div class="rev">
      <div class="contact-card">
        <h3>Fastest: call us</h3>
        <a class="contact-phone" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
        <p>Same-day service · Houston &amp; surrounding areas · Safety inspection included</p>
        <p style="margin-top:1rem;"><strong>Garage door tune-up — just $69.</strong> Financing available.</p>
      </div>
      <div class="contact-card" style="margin-top: var(--gutter);">
        <h3>Prefer to book online?</h3>
        <p><a class="btn btn-olive" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Pick a time on our calendar</a></p>
        <p style="margin-top:1rem;">{ADDRESS}<br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
    </div>
    <div class="rev rev-d1">
      <h2 style="font-size: var(--step-3); margin-bottom: 1.2rem;">Send us a message</h2>
      {FORM}
    </div>
  </div>
</section>
{cta_band("Same-day service. Honest pricing.")}
</main>
"""
    body += footer()
    write("/contact", body)

def build_schedule():
    page = CONTENT["/schedule-consult"]
    body = head(page["title"], page["meta"].get("description", "Schedule garage door service with TML."))
    body += header()
    body += f"""
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <p class="crumb"><a href="/new">Home</a> / Schedule service</p>
    <h1>Schedule your service</h1>
    <p class="lede">Broken spring replacement, garage door repair, opener service, a new installation, or a $69 tune-up — pick a time and our team will confirm your appointment.</p>
  </div>
</section>
<div class="slats"></div>
<section class="sec">
  <div class="wrap contact-grid">
    <div class="rev">
      <div class="contact-card">
        <h3>Book online now</h3>
        <p>Choose a slot that works for you — takes under a minute.</p>
        <p style="margin-top:0.9rem;"><a class="btn btn-vis" href="{BOOK}" data-track="book_click" target="_blank" rel="noopener">Open the booking calendar</a></p>
      </div>
      <div class="contact-card" style="margin-top: var(--gutter);">
        <h3>Financing available</h3>
        <p>Renovate now, pay later. Contact us for a soft-pull pre-approval — it only takes a few minutes.</p>
        <p style="margin-top:0.9rem;"><strong>Fast service. Honest pricing. Guaranteed satisfaction.</strong></p>
      </div>
    </div>
    <div class="rev rev-d1">
      <div class="contact-card" style="background: var(--forest); color: #fff;">
        <h3 style="color:#fff;">Rather just call?</h3>
        <a class="contact-phone" href="{PHONE_HREF}" style="color:#fff;">{PHONE_DISPLAY}</a>
        <p style="color: var(--on-dark-muted);">Same-day service, upfront pricing, and quality workmanship you can trust. Complete the booking or give us a call, and our team will contact you shortly to confirm your appointment.</p>
      </div>
    </div>
  </div>
</section>
{cta_band("Fast service. Honest pricing.")}
</main>
"""
    body += footer()
    write("/schedule-consult", body)

# --------------------------------------------------------------- 404 ----
def build_404():
    body = head("Page not found | TML Garage Door Services", "That page rolled away.")
    body += header()
    body += f"""
<main id="main">
<section class="lost">
  <div class="wrap">
    <p class="big">404</p>
    <h1 style="font-size: var(--step-3); margin-top: 1rem;">That page rolled away</h1>
    <p style="color: var(--ink-2); max-width: 50ch;">The page you're looking for doesn't exist — but a real person is one tap away.</p>
    <div class="cta-actions" style="margin-top: 1.4rem;">
      <a class="btn btn-vis" href="{PHONE_HREF}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn-ghost" href="/new">Back to home</a>
    </div>
  </div>
</section>
</main>
"""
    body += footer()
    (OUT / "404").mkdir(parents=True, exist_ok=True)
    (OUT / "404" / "index.html").write_text(body, "utf-8")

# -------------------------------------------------------------- main ----
def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copy(ROOT / "newdesign" / "style.css", OUT / "style.css")
    shutil.copy(ROOT / "newdesign" / "app.js", OUT / "app.js")

    build_home()
    build_services_hub()
    build_contact()
    build_schedule()
    build_404()

    for path in CONTENT:
        if path in ("/", "/services", "/contact", "/schedule-consult"):
            continue
        if path.startswith("/our-services/"):
            build_article(path, "Services", "/new/services", midcall=True)
        elif path.startswith("/brands/"):
            build_article(path, "Brands", midcall=True)
        elif path.startswith("/blogs/"):
            build_article(path, "From the blog", narrow=True)
        elif path.startswith("/projects/"):
            build_article(path, "Projects", gallery=True)
        elif path.startswith("/teams/"):
            build_article(path, "Our team", lede_from_blocks=False)
        elif path.startswith("/service-areas/"):
            build_article(path, "Service areas", midcall=True)
        else:  # about + legal
            build_article(path, "TML Garage Services", narrow=(path != "/about"))

    n = len(list(OUT.rglob("index.html")))
    print(f"built {n} pages -> {OUT}")

if __name__ == "__main__":
    main()
