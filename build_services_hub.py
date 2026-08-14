#!/usr/bin/env python3
"""Rebuild site/fixed/services/ as a garage-door services hub per the
SEO/AEO/CRO spec: phone-first hero, verifiable trust strip, service cards,
scam-proofing, reviews, brands, service areas, question-first FAQ, and
Service + FAQPage + BreadcrumbList schema.

Every claim here comes from TML's own published copy or from the verified
Google rating (5.0 / 213). No invented pricing, warranty terms, or awards.
"""
import html as H
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"
SHELL = F / "contact" / "index.html"
DEST = F / "services" / "index.html"

PHONE_HREF = "tel:+18328878747"
SMS_HREF = "sms:+18328878747"
PHONE = "(832) 887-8747"
BOOK = "/fixed/schedule-consult"
PROD = "https://www.tmlgarageservices.com/services"
A = "/assets/66b2dae9e779df43d0d269c9"

TITLE = "Garage Door Services in Conroe & The Woodlands, TX | Same-Day | TML Garage Door Services"
DESC = ("Garage door repair, spring replacement, opener service, and new installation across Conroe, "
        "The Woodlands, Spring and greater Houston. Same-day appointments, upfront pricing. "
        "Call (832) 887-8747.")

SERVICES = [
    ("/fixed/our-services/garage-door-spring-replacement", "Garage Door Spring Replacement",
     "Snapped or worn spring? Same-day replacement with a full safety check.",
     f"/assets/66b2dae9e779df43d0d269e7/6a54260670dbe02d7e8ec87f_68DF2D4A-C38C-4154-B26F-3D2148B574F7.PNG", "Same-day"),
    ("/fixed/our-services/garage-door-opener-installation", "Garage Door Opener Services",
     "Repair or replace LiftMaster, Genie, Chamberlain and Craftsman openers.",
     f"{A}/6a542e2ec6b8791b21582f07_Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png", "All brands"),
    ("/fixed/our-services/residential-garage-door-services", "Residential Garage Door Services",
     "Repairs, tune-ups, and new door installation for your home.",
     f"{A}/6a542a3cc1d76f4028c06fb8_2C6A44D6-3090-4449-81C8-D96132FB7ED7.PNG", "Residential"),
    ("/fixed/our-services/commercial-garage-door-installation", "Commercial Garage Door Installation",
     "Overhead doors for warehouses, shops, and loading docks.",
     f"{A}/6a543355c034cb7d551b686f_E796B398-C84E-4B4B-8948-E05CBCB1864E.PNG", "Commercial"),
    ("/fixed/our-services/commercial-overhead-door-services", "Commercial Overhead Door Services",
     "Repair, replacement, and service for business overhead doors.", "", "Commercial"),
    ("/fixed/our-services/residential-driveway-gate-services", "Residential Driveway Gate Services",
     "Driveway gate and gate-opener repair and installation.", "", "Gates"),
    ("/fixed/our-services/commercial-gate-opener-services", "Commercial Gate & Opener Services",
     "Gate and operator service for commercial properties.", "", "Gates"),
]

BRANDS = [("LiftMaster", "/fixed/brands/liftmaster-garage-door-opener-repair-and-installation"),
          ("Genie", "/fixed/brands/genie-garage-door-opener-repair-and-installation"),
          ("Chamberlain", "/fixed/brands/chamberlain-garage-door-opener-repair-and-installation"),
          ("Craftsman", "/fixed/brands/craftsman-garage-door-opener-repair-and-installation")]

AREAS = ["Conroe", "The Woodlands", "Spring", "Magnolia", "Montgomery", "Willis", "Tomball", "Houston"]

# question-first, ~40-60 word answers (AEO "answer capsule"), all from TML's own claims
FAQ = [
    ("Can you come out the same day?",
     "Yes. TML offers same-day and emergency garage door service across Conroe, The Woodlands, Spring and "
     "the greater Houston area, including weekends at no extra charge. If your door is stuck or a spring "
     "has broken, call (832) 887-8747 — the owner or a live in-house rep answers every call."),
    ("What garage door problems do you fix?",
     "Broken and worn torsion or extension springs, garage doors that won't open or close, doors off track, "
     "cable and roller problems, noisy or unbalanced doors, and opener faults on LiftMaster, Genie, "
     "Chamberlain and Craftsman systems. TML also installs new residential and commercial doors, gates "
     "and openers."),
    ("Do you charge extra for weekend appointments?",
     "No. There are no extra charges for weekend appointments at TML. Weekend and evening availability is "
     "the same as weekdays, which matters when a garage door fails on a Saturday and your car is stuck "
     "inside."),
    ("How do I know what the job will cost?",
     "Your technician diagnoses the problem on site and gives you the full price before any work begins. "
     "TML's stated policy is fair, upfront pricing with no hidden fees, so you approve the cost before a "
     "single part is replaced."),
    ("Are your technicians employees or subcontractors?",
     "TML's technicians are well-trained and insured members of the team, not a dispatch service. Calls are "
     "answered by the company owner or a live in-house customer service rep, and the same company that "
     "quotes your job performs the work."),
    ("Which areas do you serve?",
     "TML serves Conroe, The Woodlands, Spring, Magnolia, Montgomery, Willis, Tomball and the greater "
     "Houston area from its base in Conroe, TX. If you are nearby but do not see your town listed, call "
     "(832) 887-8747 to check availability."),
]

shell = SHELL.read_text("utf-8", errors="replace")
head_end = shell.find("</head>")
body_start = shell.find(">", shell.find("<body")) + 1
first_section = shell.find('<section class="title-section">')
footer_at = shell.find('<section class="footer">')
HEAD, PRE, POST = shell[:head_end], shell[body_start:first_section], shell[footer_at:]

# ---- head: entity + indexing hygiene ---------------------------------------
HEAD = re.sub(r"<title>.*?</title>", f"<title>{H.escape(TITLE)}</title>", HEAD, count=1, flags=re.S)
HEAD = re.sub(r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")', f"\\g<1>{H.escape(DESC)}\\2", HEAD, count=1)
HEAD = re.sub(r'(<meta[^>]*property="og:description"[^>]*content=")[^"]*(")', f"\\g<1>{H.escape(DESC)}\\2", HEAD, count=1)
HEAD = re.sub(r'(<meta[^>]*content=")[^"]*("[^>]*name="twitter:description")', f"\\g<1>{H.escape(DESC)}\\2", HEAD, count=1)
# retire the misspelled legacy-domain og:url; add the canonical the page never had
HEAD = re.sub(r'<meta[^>]*property="og:url"[^>]*>', f'<meta property="og:url" content="{PROD}"/>', HEAD)
if "rel=\"canonical\"" not in HEAD:
    HEAD = HEAD.replace("</title>", f'</title><link rel="canonical" href="{PROD}"/>', 1)
# NOTE: demo stays noindex until cutover; the page-specific Webflow
# "noindex, follow" is replaced so cutover only has to flip our sitewide tag.
HEAD = re.sub(r'<meta name="robots" content="noindex, follow"\s*/?>', "", HEAD)

SCHEMA = [
    {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.tmlgarageservices.com/"},
        {"@type": "ListItem", "position": 2, "name": "Services", "item": PROD}]},
    {"@context": "https://schema.org", "@type": "Service",
     "serviceType": "Garage door repair, installation and gate services",
     "provider": {"@type": "HomeAndConstructionBusiness", "name": "TML Garage Door Services",
                  "telephone": "+18328878747",
                  "address": {"@type": "PostalAddress", "streetAddress": "2330 FM 1488 #400",
                              "addressLocality": "Conroe", "addressRegion": "TX", "postalCode": "77384"}},
     "areaServed": [f"{a} TX" for a in AREAS],
     "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Garage door services",
                         "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t}}
                                             for _, t, _, _, _ in SERVICES]}},
    {"@context": "https://schema.org", "@type": "FAQPage",
     "mainEntity": [{"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
]
SCHEMA_HTML = "".join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + "</script>"
                      for s in SCHEMA)

CSS = """<style id="tmlsvc-css">
.sv{--g:#587735;--gd:#3f5a22;--ink:#1f2418;--mut:#5c6553;--line:#e2e5d9;}
.sv *{box-sizing:border-box;}
.sv-wrap{width:min(100% - 36px,1180px);margin:0 auto;}
.sv-hero{position:relative;color:#fff;padding:56px 0 52px;background:#3f5a22 url('/assets/66b2dae9e779df43d0d269c9/66b5115cc6a1fdc1f8b546d6_modern-garage-door-services.jpg') center/cover no-repeat;}
.sv-hero::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.28) 55%,rgba(0,0,0,.1) 100%);}
.sv-hero .sv-wrap{position:relative;}
.sv-box{background:rgba(0,0,0,.55);border-radius:10px;padding:24px 24px 22px;max-width:680px;}
.sv-hero h1{font-size:clamp(28px,4.6vw,46px);line-height:1.06;margin:0 0 12px;color:#fff!important;max-width:22ch;}
.sv-hero p{font-size:clamp(15.5px,2vw,18px);line-height:1.5;color:#eef3e6;margin:0 0 18px;max-width:58ch;}
.sv-strip{display:flex;flex-wrap:wrap;gap:8px 22px;padding:0;margin:0 0 20px;list-style:none;}
.sv-strip li{display:flex;align-items:center;gap:7px;font-weight:600;font-size:14.5px;color:#fff;}
.sv-strip li::before{content:"✓";display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#587735;color:#fff;font-size:12px;font-weight:800;}
.sv-stars{color:#ffd35c;letter-spacing:1px;}
.sv-acts{display:flex;flex-wrap:wrap;gap:10px;}
.sv-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;padding:0 24px;
 border-radius:10px;font-weight:800;font-size:16.5px;text-decoration:none;white-space:nowrap;transition:transform .14s ease;}
.sv-btn:active{transform:scale(.98);}
.sv-btn.p{background:#fff;color:var(--ink);}
.sv-btn.p:hover{background:var(--ink);color:#fff;}
.sv-btn.s{background:var(--g);color:#fff;border:2px solid rgba(255,255,255,.5);}
.sv-btn.s:hover{background:var(--gd);color:#fff;}
.sv-sec{padding:40px 0 10px;}
.sv-sec h2{font-size:clamp(21px,3.2vw,30px);margin:0 0 8px;color:var(--ink);}
.sv-sec .lede{color:var(--mut);font-size:16px;margin:0 0 22px;max-width:62ch;line-height:1.6;}
.sv-trust{display:grid;gap:12px;grid-template-columns:1fr;margin:0 0 6px;}
.sv-trust div{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;}
.sv-trust b{display:block;font-size:16px;color:var(--ink);margin-bottom:4px;}
.sv-trust span{color:var(--mut);font-size:14.5px;line-height:1.5;}
.sv-cards{display:grid;gap:16px;grid-template-columns:1fr;}
.sv-card{display:flex;flex-direction:column;background:#fff;border:1px solid var(--line);border-radius:14px;
 overflow:hidden;text-decoration:none;color:var(--ink);transition:transform .18s ease,box-shadow .18s ease;}
.sv-card:hover{transform:translateY(-3px);box-shadow:0 16px 34px -22px rgba(20,27,13,.55);color:var(--ink);}
.sv-shot{position:relative;aspect-ratio:16/10;overflow:hidden;background:#eef0e7;}
.sv-shot img{width:100%;height:100%;object-fit:cover;}
.sv-tag{position:absolute;top:10px;left:10px;background:var(--g);color:#fff;border-radius:6px;
 font-size:11.5px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;padding:4px 8px;}
.sv-card-b{padding:16px 18px 18px;display:flex;flex-direction:column;gap:6px;flex:1;}
.sv-card-b h3{margin:0;font-size:18.5px;}
.sv-card-b p{margin:0;color:var(--mut);font-size:14.5px;line-height:1.5;}
.sv-go{margin-top:auto;padding-top:10px;font-weight:700;color:var(--gd);}
.sv-diff{background:#1f2418;color:#fff;border-radius:16px;padding:clamp(22px,4vw,34px);margin:30px 0 6px;}
.sv-diff h2{color:#fff;margin:0 0 12px;}
.sv-diff ul{list-style:none;margin:0;padding:0;display:grid;gap:12px;}
.sv-diff li{display:flex;gap:11px;align-items:flex-start;color:#cfd6c4;font-size:15.5px;line-height:1.55;}
.sv-diff li::before{content:"✓";color:#cfe84d;font-weight:800;}
.sv-diff b{color:#fff;}
.sv-chips{display:flex;flex-wrap:wrap;gap:8px;padding:0;margin:14px 0 0;list-style:none;}
.sv-chips a,.sv-chips span{display:inline-block;padding:9px 15px;border-radius:999px;border:1px solid var(--line);
 background:#fff;color:var(--ink);text-decoration:none;font-weight:600;font-size:14.5px;}
.sv-chips a:hover{border-color:var(--g);color:var(--gd);}
.sv-faq{margin:10px 0 0;}
.sv-faq details{background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:10px;}
.sv-faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:14px;align-items:center;
 padding:15px 18px;font-weight:700;font-size:16.5px;color:var(--ink);}
.sv-faq summary::-webkit-details-marker{display:none;}
.sv-faq summary::after{content:"+";font-size:22px;line-height:1;color:var(--g);transition:transform .2s ease;}
.sv-faq details[open] summary::after{transform:rotate(45deg);}
.sv-faq p{margin:0;padding:0 18px 16px;color:var(--mut);font-size:15.5px;line-height:1.6;}
.sv-final{background:var(--g);border-radius:16px;color:#fff;padding:clamp(22px,4vw,34px);margin:30px 0 40px;}
.sv-final h2{color:#fff;margin:0 0 8px;}
.sv-final p{color:#eef3e6;margin:0 0 16px;font-size:16px;}
@media(min-width:760px){
 .sv-trust{grid-template-columns:repeat(4,1fr);}
 .sv-cards{grid-template-columns:repeat(3,1fr);}
 .sv-diff ul{grid-template-columns:1fr 1fr;}
}
@media(max-width:600px){.sv-hero{padding:34px 0 32px;}.sv-box{padding:18px 16px;}}
</style>"""

def cards():
    out = []
    for href, name, blurb, img, tag in SERVICES:
        shot = (f'<div class="sv-shot"><img src="{img}" alt="{H.escape(name)}" loading="lazy" decoding="async">'
                f'<span class="sv-tag">{tag}</span></div>') if img else ""
        out.append(f'<a class="sv-card" href="{href}">{shot}<div class="sv-card-b"><h3>{H.escape(name)}</h3>'
                   f'<p>{H.escape(blurb)}</p><span class="sv-go">See details →</span></div></a>')
    return "".join(out)

BODY = f"""
<div class="sv">
<section class="sv-hero">
  <div class="sv-wrap"><div class="sv-box">
    <h1>Garage door repair &amp; installation in Conroe and The Woodlands</h1>
    <p>Same-day service, upfront pricing, and technicians who work for TML — not a dispatch service.
    Tell us what the door is doing and we'll get it working today.</p>
    <ul class="sv-strip">
      <li><span class="sv-stars">★★★★★</span>&nbsp;5.0 from 213 Google reviews</li>
      <li>Same-day &amp; emergency service</li>
      <li>No weekend surcharge</li>
      <li>Insured technicians</li>
    </ul>
    <div class="sv-acts">
      <a class="sv-btn p" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>
      <a class="sv-btn s" href="{BOOK}" data-book="services-hero">Book online</a>
    </div>
  </div></div>
</section>

<section class="sv-sec"><div class="sv-wrap">
  <h2>What we fix</h2>
  <p class="lede">Residential and commercial technicians proficient in repairing all garage door and opener
  brands — and installing new ones.</p>
  <div class="sv-cards">{cards()}</div>
</div></section>

<section class="sv-sec"><div class="sv-wrap">
  <div class="sv-diff">
    <h2>What you can expect from TML</h2>
    <ul>
      <li><span><b>The price before the work.</b> Your technician diagnoses the problem and gives you the full
      price before anything is replaced — fair, upfront pricing with no hidden fees.</span></li>
      <li><span><b>A real person answers.</b> The company owner or a live in-house customer service rep is on
      the line for every call — no phone tree, no dispatch service.</span></li>
      <li><span><b>Our own technicians.</b> Well-trained and insured technicians who do the job right the
      first time, with quality workmanship on every job.</span></li>
      <li><span><b>Weekends cost the same.</b> Same-day, on-time service with no extra charges for weekend
      appointments, and 100% satisfaction guaranteed.</span></li>
    </ul>
  </div>
</div></section>

<section class="sv-sec"><div class="sv-wrap">
  <h2>Opener brands we service</h2>
  <ul class="sv-chips">{"".join(f'<li><a href="{h}">{b}</a></li>' for b, h in BRANDS)}</ul>
  <h2 style="margin-top:28px;">Where we work</h2>
  <p class="lede">Based in Conroe, TX and on the road across the metro every day.</p>
  <ul class="sv-chips">
    <li><a href="/fixed/service-areas/the-woodlands-tx">The Woodlands, TX</a></li>
    {"".join(f"<li><span>{a}, TX</span></li>" for a in AREAS if a != "The Woodlands")}
  </ul>
</div></section>

<section class="sv-sec"><div class="sv-wrap">
  <!--tmlrev--><!--/tmlrev-->
</div></section>

<section class="sv-sec"><div class="sv-wrap">
  <h2>Questions people ask before they book</h2>
  <div class="sv-faq">
    {"".join(f"<details><summary>{H.escape(q)}</summary><p>{H.escape(a)}</p></details>" for q, a in FAQ)}
  </div>
</div></section>

<section class="sv-sec" style="padding-top:6px;"><div class="sv-wrap">
  <div class="sv-final">
    <h2>Garage door won't open?</h2>
    <p>Call now for same-day service in Conroe, The Woodlands, Spring and greater Houston.</p>
    <div class="sv-acts">
      <a class="sv-btn p" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>
      <a class="sv-btn s" href="{SMS_HREF}" data-book="text">&#128172; Send us a text</a>
    </div>
  </div>
</div></section>
</div>
"""

DEST.write_text(HEAD + SCHEMA_HTML + CSS + "</head><body>" + PRE + BODY + POST, "utf-8")
print(f"rebuilt {DEST.relative_to(ROOT)}")
