#!/usr/bin/env python3
"""Build out the two stub service pages.

These pages shipped as ~970 bytes: two sentences, the standard expectations
list, and a phone link. No hero, no reviews, no FAQ, no schema. This gives them
the same hero and the same body architecture as the four rebuilt service pages.

IMPORTANT — unlike the other service pages, most of the copy here is NEW. The
originals had almost nothing to preserve. Everything TML actually states about
these services is used verbatim (marked `# TML's words` below); the rest is
written from standard trade practice and describes either the customer's
symptom or what a service visit involves. It deliberately makes NO claim about
gate brands serviced, gate types installed, materials, fabrication, access
control, pricing, or warranty, because none of that is evidenced anywhere on
the site. The owner should read this before it goes public.

Run before bake_reviews.py, which fills the <!--tmlrev--> placeholder.
"""
import html as H
import re
from pathlib import Path

from build_service_body import (A1, BOOK, PHONE, PHONE_HREF, SMS_HREF, SITE,
                                band, build, emit, picture)

HERO_CSS = """<style id="tmlsp-css">
.sp-hero{--ink:#1f2418;position:relative;color:#fff;padding:52px 0 48px;background:#3f5a22 center/cover no-repeat;}
.sp-hero::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.6) 0%,rgba(0,0,0,.3) 55%,rgba(0,0,0,.12) 100%);}
.sp-hero .sp-wrap{position:relative;width:min(100% - 36px,1180px);margin:0 auto;}
.sp-box{background:rgba(0,0,0,.55);border-radius:10px;padding:24px 24px 22px;max-width:700px;}
.sp-hero h1{font-size:clamp(26px,4.2vw,42px);line-height:1.08;margin:0 0 12px;color:#fff!important;max-width:24ch;}
.sp-hero p{font-size:clamp(15.5px,1.9vw,17.5px);line-height:1.55;color:#eef3e6;margin:0 0 18px;max-width:60ch;}
.sp-strip{display:flex;flex-wrap:wrap;gap:8px 20px;padding:0;margin:0 0 18px;list-style:none;}
.sp-strip li{display:flex;align-items:center;gap:7px;font-weight:600;font-size:14.5px;color:#fff;}
.sp-strip li::before{content:"✓";display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#587735;color:#fff;font-size:12px;font-weight:800;}
.sp-stars{color:#ffd35c;letter-spacing:1px;}
.sp-acts{display:flex;flex-wrap:wrap;gap:10px;}
.sp-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;padding:0 24px;border-radius:10px;
 font-weight:800;font-size:16.5px;text-decoration:none;white-space:nowrap;transition:background .14s ease,color .14s ease;}
.sp-btn.p{background:#fff!important;color:#1f2418!important;} .sp-btn.p:hover{background:#1f2418!important;color:#fff!important;}
.sp-btn.s{background:#587735!important;color:#fff!important;border:2px solid rgba(255,255,255,.5);} .sp-btn.s:hover{background:#3f5a22!important;color:#fff!important;}
@media(max-width:600px){.sp-hero{padding:32px 0 30px;} .sp-box{padding:18px 16px;}}
</style>"""

FAQ_CSS = """<style id="tmlsv2faq-css">
.sv2 .sv2-faq{display:grid;gap:10px;margin-top:22px;}
.sv2 .sv2-faq details{background:#fff;border:1px solid var(--line);border-radius:12px;padding:0;}
.sv2 .sv2-faq summary{cursor:pointer;list-style:none;padding:16px 18px;font-weight:700;font-size:16px;
 color:var(--ink);display:flex;justify-content:space-between;gap:14px;align-items:center;min-height:54px;}
.sv2 .sv2-faq summary::-webkit-details-marker{display:none;}
.sv2 .sv2-faq summary::after{content:"+";font-size:20px;font-weight:700;color:var(--g);flex:0 0 auto;}
.sv2 .sv2-faq details[open] summary::after{content:"\\2013";}
.sv2 .sv2-faq p{margin:0;padding:0 18px 17px;font-size:15.5px;line-height:1.6;color:var(--mut);max-width:74ch;}
</style>"""

GATE = {
    "slug": "residential-driveway-gate-services",
    "h1": "Driveway Gate Repair &amp; Installation in Conroe, TX",
    "title": "Driveway Gate Repair &amp; Installation in Conroe &amp; The Woodlands, TX | TML Garage Door Services",
    "desc": ("Driveway entry gate and gate opener repair, service and installation for homeowners in "
             "Conroe, The Woodlands, Spring and greater Houston. Same-day service. Call (832) 887-8747."),
    "service": "Residential driveway gate repair and installation",
    "hero_img": f"{A1}/66b5119db797c43daeb33012_Residential%20Driveway%20Gate%20Services.jpg",
    "hero_sub": ("Gate stuck open, stuck shut, or the opener not responding? We diagnose the actual "
                 "cause — operator, control board, sensors, or the gate hardware itself — and tell "
                 "you the price before we start."),
    "intro_h": "Residential Driveway Gate Services",
    "intro_p": [
        # TML's words, verbatim from the original page
        "We are a trustworthy, affordable, and always accessible garage door and driveway entry gate "
        "service company.",
        "Our residential technicians repair and install driveway entry gates and gate openers for "
        "homeowners throughout Conroe, The Woodlands, Spring, and the greater Houston area.",
    ],
    "triage_h": "Signs your driveway gate needs service",
    "triage_lede": "If your gate is doing any of these, it is worth having a technician look at it "
                   "before it fails completely:",
    "triage": ["Gate won't open or won't close", "Gate opens partway and stops",
               "Motor runs but the gate doesn't move", "Remote or keypad has stopped working",
               "Gate moves slowly, jerkily, or unevenly", "Grinding, scraping or unusually loud operation",
               "Gate sags, drags, or catches on the driveway", "Gate reverses on its own",
               "Safety sensors blocked or out of alignment", "No power reaching the gate operator",
               "Gate stuck open, leaving the property unsecured", "Worn hinges, rollers, or track"],
    "triage_close": "Whether your gate swings or slides, tell us what it is doing and we will "
                    "diagnose the actual cause before any work starts.",
    "price_tail": "for your gate",
    "jobs": [],
    "jobs_close": "",
    "blocks": [
        {"kind": "steps", "tint": True, "h": "What a gate service visit includes",
         "items": ["Full inspection of the gate and the operator",
                   "Check the power supply, wiring and control board",
                   "Test the safety sensors and reversing behaviour",
                   "Inspect hinges, rollers, track and posts",
                   "Check gate alignment and balance",
                   "Adjust travel limits and force settings",
                   "Program remotes and keypads",
                   "Lubricate the moving parts",
                   "Full operation test before we leave"],
         "close": "You get the full price before any work begins."},
    ],
    "why_h": "What you can expect from TML",     # TML's words
    "why_lede": "",
    "why": ["Same day on-time service", "Emergency Services",
            "No extra charges for weekend appointments",
            "Well-trained and insured technicians", "100% satisfaction guaranteed"],
    "why_close": "",
    "faq": [
        ("Do you service the gate opener as well as the gate itself?",
         "Yes. Our residential technicians repair and install both driveway entry gates and gate "
         "openers, so one visit covers the gate hardware and the operator that drives it."),
        ("Can you come out the same day?",
         "Same-day and emergency appointments are available across Conroe, The Woodlands, Spring and "
         "greater Houston, and there is no extra charge for a weekend appointment."),
        ("My gate is stuck open — is that urgent?",
         "A gate stuck open leaves the property unsecured, so we treat it as an emergency call. "
         "Call (832) 887-8747 and a real person will get a technician routed to you."),
        ("Will I know the price before any work starts?",
         "Yes. Your technician diagnoses the problem on site and gives you the full price before "
         "anything is repaired or replaced — upfront pricing with no hidden fees."),
    ],
    "areas_h": "Serving Conroe, The Woodlands, Spring &amp; greater Houston",
    "areas_lede": "We provide residential driveway gate service throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "If you're nearby, contact us to check service availability.",
    "cta_h": "Get your driveway gate working again",
    "cta_p": "Tell us what the gate is doing and we'll get a technician out — same-day and emergency "
             "appointments available, and a real person answers the phone.",
}

OVERHEAD = {
    "slug": "commercial-overhead-door-services",
    "h1": "Commercial Overhead Door Repair &amp; Installation — Houston Area",
    "title": "Commercial Overhead Door Repair &amp; Installation | Houston &amp; Conroe | TML Garage Door Services",
    "desc": ("Overhead door repair, replacement and new installation for businesses across the "
             "greater Houston area. Same-day and emergency service. Call (832) 887-8747."),
    "service": "Commercial overhead door repair and installation",
    "hero_img": f"{A1}/66b511bf3289a9426e0f95bb_Commercial%20Overhead%20Door%20Services.jpg",
    "hero_sub": ("When an overhead door stops working, everything behind it stops too. We diagnose "
                 "the fault, tell you the price before we start, and get the opening back in service."),
    "intro_h": "Commercial Overhead Door Services",
    "intro_p": [
        # TML's words, verbatim from the original page
        "TML Garage Door Services' residential and commercial technicians are highly proficient at "
        "repairing all garage door and opener brands.",
        "Our commercial team services overhead doors for businesses throughout the greater Houston "
        "area — repair, replacement, and new installation.",
    ],
    "triage_h": "Common overhead door problems",
    "triage_lede": "We service the faults that take a commercial opening out of use:",
    "triage": ["Door won't open or won't close", "Door has come off its track",
               "Broken springs or cables", "Bent, dented or damaged panels or slats",
               "Door drifts down or won't stay up", "Grinding or unusually loud operation",
               "Operator runs but the door doesn't move", "Door binds or moves unevenly",
               "Damaged or missing bottom seal", "Worn rollers, hinges or bearings",
               "Safety sensor or control faults", "Door stuck open, leaving the building unsecured"],
    "triage_close": "A door that won't close is a security problem as well as an operational one — "
                    "same-day and emergency appointments are available.",
    "price_tail": "for your door",
    "jobs": [],
    "jobs_close": "",
    "blocks": [
        {"kind": "steps", "tint": True, "h": "What a commercial overhead door service call includes",
         "items": ["Inspection of the door, springs, cables and hardware",
                   "Operator and control system check",
                   "Track, roller and bearing inspection",
                   "Spring tension and door balance check",
                   "Safety system and reversing test",
                   "Panel, slat and bottom seal inspection",
                   "Adjustment and lubrication of moving parts",
                   "Full cycle test under normal operating load",
                   "A clear recommendation, and the price, before anything is replaced"],
         "close": "We service overhead doors for businesses throughout the greater Houston area — "
                  "repair, replacement, and new installation."},
    ],
    "why_h": "What you can expect from TML",     # TML's words
    "why_lede": "",
    "why": ["Same day on-time service", "Emergency Services",
            "No extra charges for weekend appointments",
            "Well-trained and insured technicians", "100% satisfaction guaranteed"],
    "why_close": "",
    "faq": [
        ("How fast can you get a commercial door back in service?",
         "Same-day service is available across the Houston area, including weekends at no extra "
         "charge. A door that won't open can stop shipping, receiving, or customer access entirely, "
         "so commercial calls are treated as downtime."),
        ("Do you repair the door, the operator, or both?",
         "Both. Our technicians are proficient at repairing all garage door and opener brands, so a "
         "single visit covers the door hardware and the operator that runs it."),
        ("Can you replace a door rather than repair it?",
         "Yes — we handle repair, replacement and new installation for commercial overhead doors. "
         "Your technician will tell you which makes more sense for the door in front of them, and "
         "the price, before anything is replaced."),
        ("Will I know the cost before work starts?",
         "Yes. You get the full price before any work begins — upfront pricing with no hidden fees."),
    ],
    "areas_h": "Serving businesses across greater Houston",
    "areas_lede": "We provide commercial overhead door service throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "Contact us to discuss your facility's overhead doors.",
    "cta_h": "Get your overhead door back in service",
    "cta_p": "Tell us what the door is doing and we'll route a technician — same-day and emergency "
             "service, with no weekend surcharge.",
}

PAGES = [GATE, OVERHEAD]


def hero(spec):
    return (
        f'<section class="sp-hero" style="background-image:url({spec["hero_img"]})">'
        '<div class="sp-wrap"><div class="sp-box">'
        f'<h1>{spec["h1"]}</h1><p>{H.escape(spec["hero_sub"])}</p>'
        '<ul class="sp-strip">'
        '<li><span class="sp-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span> 5.0 from 213 Google reviews</li>'
        "<li>Same-day service</li><li>No weekend surcharge</li><li>Insured technicians</li></ul>"
        '<div class="sp-acts">'
        f'<a class="sp-btn p" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
        f'<a class="sp-btn s" href="{BOOK}" data-book="hero">Book online</a>'
        "</div></div></div></section>")


def faq_html(spec):
    return ('<h2>Frequently asked questions</h2><div class="sv2-faq">'
            + "".join(f"<details><summary>{H.escape(q)}</summary><p>{H.escape(a)}</p></details>"
                      for q, a in spec["faq"])
            + "</div>")


def schema(spec):
    import json
    url = f"https://www.tmlgarageservices.com/our-services/{spec['slug']}"
    blocks = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": "https://www.tmlgarageservices.com/"},
            {"@type": "ListItem", "position": 2, "name": "Services",
             "item": "https://www.tmlgarageservices.com/services"},
            {"@type": "ListItem", "position": 3, "name": spec["service"], "item": url}]},
        {"@context": "https://schema.org", "@type": "Service", "serviceType": spec["service"],
         "provider": {"@type": "HomeAndConstructionBusiness", "name": "TML Garage Door Services",
                      "telephone": "+18328878747",
                      "address": {"@type": "PostalAddress", "streetAddress": "2330 FM 1488 #400",
                                  "addressLocality": "Conroe", "addressRegion": "TX",
                                  "postalCode": "77384"}},
         "areaServed": [{"@type": "City", "name": c} for c in spec["areas"][:8]], "url": url},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in spec["faq"]]},
    ]
    return "".join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False)
                   + "</script>" for b in blocks)


def rebuild(spec):
    page = SITE / "fixed" / "our-services" / spec["slug"] / "index.html"
    html = page.read_text("utf-8", errors="replace")

    for sid in ("tmlsp-css", "tmlsv2-css", "tmlsv2faq-css"):
        html = re.sub(r'<style id="%s">.*?</style>' % sid, "", html, flags=re.S)
    html = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", '
                  r'"@type": "(?:BreadcrumbList|Service|FAQPage)".*?</script>', "", html, flags=re.S)

    # 1. the plain title band becomes the same hero the other service pages use
    m = re.search(r'<section class="title-section">.*?</section>', html, re.S)
    if m:
        html = html[:m.start()] + hero(spec) + html[m.end():]

    # 2. the body
    m = re.search(r'<section class="section-3"[^>]*>', html)
    if not m:
        print(f"  {spec['slug']}: no section-3 — skipped")
        return
    depth, end = 1, None
    for t in re.finditer(r"<section\b|</section>", html[m.end():]):
        depth += 1 if t.group(0) == "<section" else -1
        if depth == 0:
            end = m.end() + t.start()
            break
    if end is None:
        print(f"  {spec['slug']}: unbalanced section-3 — skipped")
        return

    body = build(spec, "<!--tmlrev--><!--/tmlrev-->", faq_html(spec))
    html = html[:m.end()] + body + html[end:]

    # 3. head
    from build_service_body import CSS as SV2_CSS
    html = re.sub(r"<title>.*?</title>", f"<title>{spec['title']}</title>", html, count=1, flags=re.S)
    html = re.sub(r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")',
                  lambda mm: mm.group(1) + H.escape(spec["desc"]) + mm.group(2), html, count=1)
    html = html.replace("</head>", HERO_CSS + SV2_CSS + FAQ_CSS + schema(spec) + "</head>", 1)
    page.write_text(html, "utf-8")
    print(f"  {spec['slug']}: built out")


def main():
    for spec in PAGES:
        rebuild(spec)
    print("now run bake_reviews.py to fill the review placeholder")


if __name__ == "__main__":
    main()
