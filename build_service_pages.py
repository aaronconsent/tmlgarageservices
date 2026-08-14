#!/usr/bin/env python3
"""Apply the conversion/SEO/AEO template to each service page.

Preserves every word of TML's existing service content (symptom lists,
what's-included, types) and wraps it in the template: phone-first hero,
trust row, question-first "quick answers" capsules, honest pricing block,
differentiator panel, brands, reviews, service areas, service-specific FAQ,
and a closing CTA — plus Service/FAQPage/BreadcrumbList schema.

FACTS TML STILL OWES US live in FACTS below. Fill them in and re-run; the
page upgrades itself. Until then the page shows their real, published
promise ("full price before any work begins") instead of invented numbers.
Idempotent.
"""
import html as H
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed" / "our-services"
n = Counter()

PHONE_HREF, SMS_HREF, PHONE = "tel:+18328878747", "sms:+18328878747", "(832) 887-8747"
BOOK = "/fixed/schedule-consult"
PROD = "https://www.tmlgarageservices.com/our-services"
A = "/assets/66b2dae9e779df43d0d269c9"
AREAS = ["Conroe", "The Woodlands", "Spring", "Magnolia", "Montgomery", "Willis", "Tomball", "Houston"]

# ─────────────────────────────────────────────────────────────────────────
# FILL THESE IN when the owner answers, then re-run. Empty = not shown.
FACTS = {
    "spring_from": "",        # e.g. "189"  → "Spring replacement from $189"
    "opener_repair_from": "",
    "opener_install_from": "",
    "door_install_from": "",
    "service_call": "",       # e.g. "59"
    "service_call_waived": None,   # True/False → "waived with any repair"
    "workmanship_warranty": "",    # e.g. "1-year"
    "parts_warranty": "",
    "employees_not_subs": None,    # True once confirmed
    "background_checked": None,    # True once confirmed
    "years_in_business": "",
    "authorized_dealer": "",       # e.g. "LiftMaster ProVantage"
}
# ─────────────────────────────────────────────────────────────────────────

PAGES = {
    "garage-door-spring-replacement": dict(
        h1="Garage Door Spring Repair in Conroe, TX — Same-Day Service",
        title="Garage Door Spring Repair in Conroe & The Woodlands, TX | Same-Day | TML Garage Door Services",
        desc=("Broken garage door spring? TML replaces torsion and extension springs same-day across Conroe, "
              "The Woodlands, Spring and greater Houston. 5.0 from 213 Google reviews. Call (832) 887-8747."),
        sub=("A broken spring makes the door too heavy to lift and can burn out your opener. We carry "
             "high-cycle springs, balance the door, and test the whole system before we leave."),
        service="Garage door spring repair and replacement",
        img=f"{A}/6a543368b89f6b6fe88b1284_1F1EB104-997F-40F2-AAC8-9630A0DF66CC.PNG",
        price_key="spring_from",
        capsules=[
            ("What causes a garage door spring to break?",
             "Garage door springs break from normal cycle wear — a standard spring is rated for about "
             "10,000 open-and-close cycles, roughly seven years of daily use. Rust from humidity, poor "
             "lubrication, and an unbalanced door shorten that life. Most breaks happen in cold snaps, "
             "when the metal contracts and the weakest coil finally lets go."),
            ("Can I still use my garage door with a broken spring?",
             "No. The springs carry almost all of the door's weight, so with one broken the door becomes "
             "extremely heavy, can fall, and will strain or destroy the opener. Leave the door down, "
             "disconnect the opener if it is straining, and call (832) 887-8747 for same-day service."),
            ("Should both springs be replaced at the same time?",
             "On a two-spring door, yes — both springs were installed together and have taken the same "
             "number of cycles, so when one fails the other is usually close behind. Replacing both at "
             "once keeps the door balanced and avoids paying for a second service visit weeks later."),
        ],
        faq=[
            ("How long does garage door spring replacement take?",
             "Most spring replacements are finished in about one to two hours, depending on the door and "
             "the spring system. That includes removing the broken spring, installing new high-cycle "
             "springs, balancing the door, and testing the opener before we leave."),
            ("Can you replace a garage door spring the same day?",
             "Yes. Same-day and emergency spring replacement is available across Conroe, The Woodlands, "
             "Spring and the greater Houston area, including weekends at no extra charge. Call "
             "(832) 887-8747 and the owner or a live in-house rep will get you scheduled."),
            ("Is replacing a garage door spring dangerous?",
             "Yes — torsion springs are under extreme tension and can cause serious injury if handled "
             "improperly. This is the one garage door repair that should never be a DIY job. Our "
             "technicians are trained and insured to unwind and replace them safely."),
            ("What kinds of springs do you replace?",
             "Torsion springs, extension springs, single and dual spring systems, and high-cycle springs "
             "for doors that open many times a day. We work with all major garage door brands and models."),
            ("Do you charge extra for weekend spring repairs?",
             "No. There are no extra charges for weekend appointments — a Saturday spring replacement "
             "costs the same as a Tuesday one."),
        ]),
    "garage-door-opener-installation": dict(
        h1="Garage Door Opener Repair & Installation in Conroe, TX",
        title="Garage Door Opener Repair in Conroe & The Woodlands, TX | Same-Day | TML Garage Door Services",
        desc=("Garage door opener not working? TML repairs and installs LiftMaster, Genie, Chamberlain and "
              "Craftsman openers across Conroe, The Woodlands and greater Houston. Call (832) 887-8747."),
        sub=("Opener won't respond, reverses on its own, or hums without moving? We diagnose the actual "
             "cause — sensors, logic board, gear, or the door itself — and tell you the price before we start."),
        service="Garage door opener repair and installation",
        img=f"{A}/6a542e2ec6b8791b21582f07_Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png",
        price_key="opener_repair_from",
        brands=True,
        capsules=[
            ("Why won't my garage door opener work?",
             "The most common causes are misaligned or dirty safety sensors, a dead remote battery, a "
             "stripped drive gear, or a failed logic board. If the motor hums but the door doesn't move, "
             "the gear or trolley is usually the culprit; if the door reverses right after touching the "
             "floor, it is normally the sensors or the close-force setting."),
            ("Should I repair or replace my garage door opener?",
             "Repair is usually the better value if the unit is under roughly ten years old and the "
             "failure is a sensor, remote, gear, or spring-related strain. Replacement makes more sense "
             "for older units with a failed logic board, no rolling-code security, or no auto-reverse "
             "safety feature, which modern openers include by law."),
            ("Which garage door openers do you service?",
             "We repair and install all major brands — LiftMaster, Genie, Chamberlain and Craftsman — "
             "across belt drive, chain drive, screw drive and wall-mount (jackshaft) systems, including "
             "smart openers with Wi-Fi and phone-app control."),
        ],
        faq=[
            ("Can you fix my garage door opener today?",
             "Usually yes. Our technicians arrive with the tools and common replacement parts needed to "
             "finish many opener repairs on the first visit, and same-day appointments are available "
             "across Conroe, The Woodlands, Spring and greater Houston."),
            ("My garage door opener lights are flashing — what does that mean?",
             "A flashing opener light almost always means the safety sensors are blocked or out of "
             "alignment. Check that nothing is in the door's path and that both sensor lights are solid. "
             "If the flashing continues, the sensors or their wiring need service."),
            ("Do you install openers I bought myself?",
             "Call (832) 887-8747 and we'll talk through the model you have. In most cases we can install "
             "a customer-supplied opener, though we'll flag anything that isn't a good match for your "
             "door's weight or track configuration."),
            ("How long does a new opener installation take?",
             "A typical opener replacement takes a couple of hours. That covers removing the old unit, "
             "mounting and setting up the new motor, installing safety sensors and the wall control, "
             "programming remotes and keypads, and complete safety testing."),
            ("What does an opener installation include?",
             "Removal of your old opener, professional installation of the new one, rail and drive "
             "system, motor mounting, safety sensors, wall control, remote programming, keypad setup, "
             "smart-app configuration where available, and full safety testing."),
        ]),
    "residential-garage-door-services": dict(
        h1="New Garage Door Installation in Conroe & The Woodlands, TX",
        title="New Garage Door Installation in Conroe, TX | TML Garage Door Services",
        desc=("New garage door installation and residential repairs across Conroe, The Woodlands, Spring "
              "and greater Houston. Insulated, carriage house, modern and traditional doors. "
              "Call (832) 887-8747."),
        sub=("Replacing a worn, dented, or noisy door? We measure, remove the old door, install the new "
             "one with fresh tracks and hardware, balance it, and haul the old one away."),
        service="Residential garage door installation and repair",
        img=f"{A}/6a542a3cc1d76f4028c06fb8_2C6A44D6-3090-4449-81C8-D96132FB7ED7.PNG",
        price_key="door_install_from",
        capsules=[
            ("How long does a new garage door last?",
             "A quality residential garage door typically lasts 15 to 30 years, while the springs and "
             "opener are wear items replaced sooner. Insulated steel doors hold up especially well in "
             "Houston-area heat and humidity, and regular tune-ups keep the hardware from aging the door "
             "prematurely."),
            ("Is an insulated garage door worth it in the Houston area?",
             "For an attached garage, usually yes. An insulated door moderates the temperature of the "
             "garage and any room above or beside it, cuts the noise of the door cycling, and adds "
             "rigidity that helps the door survive wind and daily use better than a single-layer panel."),
            ("How long does a garage door installation take?",
             "Most single-door replacements are completed in a day. That includes removing the existing "
             "door, installing new tracks and hardware, setting and balancing the spring system, "
             "connecting the opener, testing the safety sensors, and hauling away the old materials."),
        ],
        faq=[
            ("What garage door styles do you install?",
             "Traditional raised panel, modern, contemporary glass, carriage house, flush panel, short "
             "panel, long panel and insulated garage doors. We'll bring options that suit your home's "
             "style and the way you actually use the garage."),
            ("Do you remove and dispose of my old garage door?",
             "Yes. Removal of your existing door and cleanup and haul-away of the old materials are part "
             "of the installation — you don't have to arrange disposal."),
            ("Will a new garage door work with my existing opener?",
             "Often yes, and we connect it as part of the installation. If your opener is undersized for "
             "a heavier insulated door or lacks current safety features, we'll tell you before the "
             "install rather than after."),
            ("What's included in a garage door installation?",
             "Free consultation and measurements, removal of the existing door, professional installation, "
             "new tracks and hardware, spring system installation and balancing, rollers and hinges, "
             "opener connection, safety sensor testing, full inspection, final adjustments, and cleanup."),
            ("Do you install garage doors in new construction?",
             "Yes — we handle both new construction and replacement doors for homes across Conroe, The "
             "Woodlands, Spring, Magnolia, Montgomery, Willis, Tomball and greater Houston."),
        ]),
    "commercial-garage-door-installation": dict(
        h1="Commercial Garage Door Repair & Installation — Houston Area",
        title="Commercial Garage Door Repair & Installation | Houston & Conroe | TML Garage Door Services",
        desc=("Commercial overhead door repair, installation and operator service for Houston-area "
              "businesses — rolling steel, sectional, roll-up and warehouse doors. Call (832) 887-8747."),
        sub=("When a commercial door stops working, everything behind it stops too. We service sectional, "
             "rolling steel, roll-up and warehouse doors, plus the operators that run them."),
        service="Commercial garage door repair and installation",
        img=f"{A}/6a543355c034cb7d551b686f_E796B398-C84E-4B4B-8948-E05CBCB1864E.PNG",
        price_key="",
        capsules=[
            ("How fast can you get a commercial door back in service?",
             "Same-day service is available across the Houston area, including weekends at no extra "
             "charge. Because a door that won't open can stop shipping, receiving, or customer access "
             "entirely, commercial calls are treated as downtime — call (832) 887-8747 and a live rep "
             "will get a technician routed to you."),
            ("What commercial door types do you service?",
             "Sectional commercial garage doors, rolling steel doors, roll-up doors, warehouse doors and "
             "loading dock doors, along with the commercial operators, springs, cables, tracks and safety "
             "systems that run them."),
            ("Do you offer preventive maintenance for commercial doors?",
             "Yes. Scheduled maintenance catches worn springs, frayed cables and failing operators before "
             "they become an emergency shutdown — which for most businesses costs far more than the "
             "repair itself."),
        ],
        faq=[
            ("Do you service loading dock doors?",
             "Yes. Loading dock door problems are among the most common commercial calls we take, along "
             "with rolling steel doors and high-cycle warehouse doors."),
            ("Can you service commercial door operators?",
             "Yes — we service and install commercial door operators, including safety system setup and "
             "final adjustment, for all major commercial garage door systems."),
            ("Do you work outside normal business hours?",
             "Emergency service is available, including weekends at no extra charge, so a repair can "
             "often be scheduled around your operating hours instead of interrupting them."),
            ("What's included in a commercial installation?",
             "Site evaluation and measurements, door selection assistance, professional installation, "
             "commercial operator installation, safety system setup, track and hardware installation, "
             "spring system installation, final adjustments and testing, and a safety inspection."),
            ("Which areas do you cover for commercial work?",
             "Conroe, The Woodlands, Spring, Magnolia, Montgomery, Willis, Tomball and the greater "
             "Houston area."),
        ]),
}

BRANDS = [("LiftMaster", "liftmaster"), ("Genie", "genie"), ("Chamberlain", "chamberlain"), ("Craftsman", "craftsman")]

CSS = """<style id="tmlsp-css">
.sp{--g:#587735;--gd:#3f5a22;--ink:#1f2418;--mut:#5c6553;--line:#e2e5d9;}
.sp *{box-sizing:border-box;}
.sp-wrap{width:min(100% - 36px,1180px);margin:0 auto;}
.sp-hero{--ink:#1f2418;--g:#587735;--gd:#3f5a22;position:relative;color:#fff;padding:52px 0 48px;background:#3f5a22 center/cover no-repeat;}
.sp-hero::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.6) 0%,rgba(0,0,0,.3) 55%,rgba(0,0,0,.12) 100%);}
.sp-hero .sp-wrap{position:relative;}
.sp-box{background:rgba(0,0,0,.55);border-radius:10px;padding:24px 24px 22px;max-width:700px;}
.sp-hero h1{font-size:clamp(26px,4.2vw,42px);line-height:1.08;margin:0 0 12px;color:#fff!important;max-width:24ch;}
.sp-hero p{font-size:clamp(15.5px,1.9vw,17.5px);line-height:1.55;color:#eef3e6;margin:0 0 18px;max-width:60ch;}
.sp-strip{display:flex;flex-wrap:wrap;gap:8px 20px;padding:0;margin:0 0 18px;list-style:none;}
.sp-strip li{display:flex;align-items:center;gap:7px;font-weight:600;font-size:14.5px;color:#fff;}
.sp-strip li::before{content:"✓";display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#587735;color:#fff;font-size:12px;font-weight:800;}
.sp-stars{color:#ffd35c;letter-spacing:1px;}
.sp-acts{display:flex;flex-wrap:wrap;gap:10px;}
.sp-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;padding:0 24px;border-radius:10px;
 font-weight:800;font-size:16.5px;text-decoration:none;white-space:nowrap;transition:transform .14s ease;}
.sp-btn:active{transform:scale(.98);}
.sp-btn.p{background:#fff!important;color:#1f2418!important;} .sp-btn.p:hover{background:#1f2418!important;color:#fff!important;}
.sp-btn.s{background:#587735!important;color:#fff!important;border:2px solid rgba(255,255,255,.5);} .sp-btn.s:hover{background:#3f5a22!important;color:#fff!important;}
.sp-trust{display:grid;gap:12px;grid-template-columns:1fr;margin:24px 0 6px;}
.sp-trust div{background:#fff;border:1px solid var(--line);border-radius:12px;padding:15px 17px;}
.sp-trust b{display:block;font-size:15.5px;color:var(--ink);margin-bottom:3px;}
.sp-trust span{color:var(--mut);font-size:14px;line-height:1.5;}
.sp-caps{margin:30px 0 6px;}
.sp-cap{background:#f6f8f1;border-left:0;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:12px;}
.sp-cap h2{font-size:clamp(18px,2.4vw,22px);margin:0 0 8px;color:var(--ink);}
.sp-cap p{margin:0;color:var(--mut);font-size:15.5px;line-height:1.65;}
.sp-price{background:#fff;border:2px dashed #9fb277;border-radius:12px;padding:18px 20px;margin:24px 0 6px;}
.sp-price b{display:block;font-size:17px;color:var(--ink);margin-bottom:6px;}
.sp-price p{margin:0;color:var(--mut);font-size:15px;line-height:1.6;}
.sp-diff{background:#1f2418;color:#fff;border-radius:16px;padding:clamp(20px,3.5vw,30px);margin:28px 0 6px;}
.sp-diff h2{color:#fff;margin:0 0 12px;font-size:clamp(20px,3vw,26px);}
.sp-diff ul{list-style:none;margin:0;padding:0;display:grid;gap:11px;}
.sp-diff li{display:flex;gap:10px;align-items:flex-start;color:#cfd6c4;font-size:15px;line-height:1.55;}
.sp-diff li::before{content:"✓";color:#cfe84d;font-weight:800;}
.sp-diff b{color:#fff;}
.sp-chips{display:flex;flex-wrap:wrap;gap:8px;padding:0;margin:12px 0 0;list-style:none;}
.sp-chips a,.sp-chips span{display:inline-block;padding:9px 15px;border-radius:999px;border:1px solid var(--line);background:#fff;
 color:var(--ink);text-decoration:none;font-weight:600;font-size:14.5px;}
.sp-chips a:hover{border-color:var(--g);color:var(--gd);}
.sp-sec{margin:30px 0 0;}
.sp-sec h2{font-size:clamp(20px,3vw,27px);margin:0 0 10px;color:var(--ink);}
.sp-final{background:var(--g);border-radius:16px;color:#fff;padding:clamp(20px,3.5vw,30px);margin:28px 0 34px;}
.sp-final h2{color:#fff;margin:0 0 8px;} .sp-final p{color:#eef3e6;margin:0 0 16px;font-size:15.5px;}
@media(min-width:760px){.sp-trust{grid-template-columns:repeat(4,1fr);} .sp-diff ul{grid-template-columns:1fr 1fr;}}
@media(max-width:600px){.sp-hero{padding:32px 0 30px;} .sp-box{padding:18px 16px;}}
</style>"""

def trust_row():
    warranty = (f"<div><b>{H.escape(FACTS['workmanship_warranty'])} workmanship warranty</b>"
                "<span>In writing, on the work we perform.</span></div>"
                if FACTS["workmanship_warranty"] else
                "<div><b>100% satisfaction guaranteed</b><span>We're not done until the door works right.</span></div>")
    return ('<div class="sp-trust">'
            "<div><b>The price before the work</b><span>Upfront pricing with no hidden fees.</span></div>"
            "<div><b>Same-day &amp; emergency</b><span>No extra charge for weekends.</span></div>"
            "<div><b>Insured technicians</b><span>Well-trained, and they work for TML.</span></div>"
            + warranty + "</div>")

def price_block(cfg):
    key = cfg.get("price_key") or ""
    amount = FACTS.get(key) or ""
    fee = FACTS.get("service_call") or ""
    if amount:
        line = f"<b>{H.escape(cfg['service'])} from ${H.escape(amount)}</b>"
        extra = ""
        if fee:
            waived = " — waived with any repair" if FACTS.get("service_call_waived") else ""
            extra = f" Service call ${H.escape(fee)}{waived}."
        return ('<div class="sp-price">' + line +
                "<p>Your technician confirms the full price on site before any work begins."
                + extra + "</p></div>")
    # honest fallback until TML supplies real numbers
    return ('<div class="sp-price"><b>What will it cost?</b>'
            "<p>Your technician diagnoses the problem on site and gives you the full price before any "
            "work begins — fair, upfront pricing with no hidden fees. Call "
            f'<a href="{PHONE_HREF}">{PHONE}</a> and we can talk through the likely range for your door '
            "before we come out.</p></div>")

def diff_block():
    techs = ("<li><span><b>Our own technicians.</b> Well-trained and insured — the company that quotes "
             "your job is the company that does it.</span></li>")
    if FACTS.get("employees_not_subs"):
        techs = ("<li><span><b>No subcontractors.</b> Every technician is a TML employee, well-trained "
                 "and insured.</span></li>")
    return ('<div class="sp-diff"><h2>How we keep this straightforward</h2><ul>'
            "<li><span><b>You approve the price first.</b> We diagnose, we quote, you decide — no work "
            "starts before you know the number.</span></li>"
            "<li><span><b>A real person answers.</b> The owner or a live in-house rep takes every call — "
            "no phone tree, no dispatch service.</span></li>"
            + techs +
            "<li><span><b>Weekends cost the same.</b> Same-day, on-time service with no weekend "
            "surcharge, and 100% satisfaction guaranteed.</span></li>"
            "</ul></div>")

def brands_block():
    return ('<div class="sp-sec"><h2>Opener brands we service</h2><ul class="sp-chips">'
            + "".join(f'<li><a href="/fixed/brands/{s}-garage-door-opener-repair-and-installation">{b}</a></li>'
                      for b, s in BRANDS) + "</ul></div>")

def areas_block():
    return ('<div class="sp-sec"><h2>Where we work</h2><ul class="sp-chips">'
            '<li><a href="/fixed/service-areas/the-woodlands-tx">The Woodlands, TX</a></li>'
            + "".join(f"<li><span>{a}, TX</span></li>" for a in AREAS if a != "The Woodlands")
            + "</ul></div>")

for slug, cfg in PAGES.items():
    p = F / slug / "index.html"
    if not p.exists():
        continue
    h = orig = p.read_text("utf-8", errors="replace")

    # strip prior run
    h = re.sub(r'<style id="tmlsp-css">.*?</style>', "", h, flags=re.S)
    h = re.sub(r'<section class="sp-hero">.*?</section>', "", h, flags=re.S)
    h = re.sub(r'<div class="sp-pre">.*?</div><!--/sp-pre-->', "", h, flags=re.S)
    h = re.sub(r'<div class="sp-post">.*?</div><!--/sp-post-->', "", h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "(?:Service|FAQPage|BreadcrumbList)".*?</script>', "", h, flags=re.S)

    # 1. hero replaces the legacy title-section
    hero = (f'<section class="sp-hero" style="background-image:url(\'{cfg["img"]}\')">'
            '<div class="sp-wrap"><div class="sp-box">'
            f'<h1>{H.escape(cfg["h1"])}</h1><p>{H.escape(cfg["sub"])}</p>'
            '<ul class="sp-strip">'
            '<li><span class="sp-stars">★★★★★</span>&nbsp;5.0 from 213 Google reviews</li>'
            "<li>Same-day service</li><li>No weekend surcharge</li><li>Insured technicians</li></ul>"
            f'<div class="sp-acts"><a class="sp-btn p" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
            f'<a class="sp-btn s" href="{BOOK}" data-book="service-hero">Book online</a></div>'
            "</div></div></section>")
    h = re.sub(r'<section class="title-section">.*?</section>', hero, h, count=1, flags=re.S)
    n["heroes"] += 1

    # 2. before their content: trust row + answer capsules (AEO)
    caps = "".join(f'<div class="sp-cap"><h2>{H.escape(q)}</h2><p>{H.escape(a)}</p></div>'
                   for q, a in cfg["capsules"])
    pre = ('<div class="sp"><div class="sp-wrap"><div class="sp-pre">'
           + trust_row() + '<div class="sp-caps">' + caps + "</div></div><!--/sp-pre--></div></div>")
    anchor = h.find('<div class="rich-text w-richtext">')
    if anchor > -1:
        h = h[:anchor] + pre + h[anchor:]
        n["capsules"] += 1

    # 3. after their content, before the FAQ: pricing + difference + brands + areas + reviews
    post = ('<div class="sp"><div class="sp-wrap"><div class="sp-post">'
            + price_block(cfg) + diff_block()
            + (brands_block() if cfg.get("brands") else "")
            + areas_block()
            + '<div class="sp-sec"><!--tmlrev--><!--/tmlrev--></div>'
            + "</div><!--/sp-post--></div></div>")
    faq_at = h.find('<div class="tmlfaq">')
    if faq_at > -1:
        h = h[:faq_at] + post + h[faq_at:]
        n["post"] += 1

    # 4. richer, service-specific FAQ replaces the generic one
    faq_html = ('<div class="tmlfaq"><h2 class="tmlfaq-h">Frequently asked questions</h2>'
                + "".join(f"<details><summary>{H.escape(q)}</summary><p>{H.escape(a)}</p></details>"
                          for q, a in cfg["faq"]) + "</div>")
    h = re.sub(r'<div class="tmlfaq">.*?</div>(?=<div class="tmlcta">|<div class="sp")', faq_html, h, count=1, flags=re.S)

    # 5. closing CTA band after the FAQ (their tmlcta panel stays as the offer block)
    final = ('<div class="sp"><div class="sp-wrap"><div class="sp-final">'
             f'<h2>Need this fixed today?</h2><p>Same-day service across Conroe, The Woodlands, Spring '
             "and greater Houston — a real person answers.</p>"
             f'<div class="sp-acts"><a class="sp-btn p" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
             f'<a class="sp-btn s" href="{SMS_HREF}" data-book="text">&#128172; Send us a text</a></div>'
             "</div></div></div>")
    # drop any band a previous run left behind, or re-running stacks copies
    while True:
        prev = h.find('<div class="sp"><div class="sp-wrap"><div class="sp-final">')
        if prev == -1:
            break
        depth, end = 3, None
        import re as _re
        for _m in _re.finditer(r"<div\b|</div>", h[prev + 58:]):
            depth += 1 if _m.group(0) == "<div" else -1
            if depth == 0:
                end = prev + 58 + _m.end()
                break
        if end is None:
            break
        h = h[:prev] + h[end:]

    cta_at = h.find('<div class="tmlcta">')
    if cta_at > -1:
        end = h.find("</div></div>", cta_at)
        h = h[:end + len("</div></div>")] + final + h[end + len("</div></div>"):]
        n["final"] += 1

    # 6. head: title, description, canonical, schema
    url = f"{PROD}/{slug}"
    h = re.sub(r"<title>.*?</title>", f"<title>{H.escape(cfg['title'])}</title>", h, count=1, flags=re.S)
    h = re.sub(r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")', f"\\g<1>{H.escape(cfg['desc'])}\\2", h, count=1)
    h = re.sub(r'(<meta[^>]*property="og:description"[^>]*content=")[^"]*(")', f"\\g<1>{H.escape(cfg['desc'])}\\2", h, count=1)
    schema = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.tmlgarageservices.com/"},
            {"@type": "ListItem", "position": 2, "name": "Services", "item": "https://www.tmlgarageservices.com/services"},
            {"@type": "ListItem", "position": 3, "name": cfg["service"], "item": url}]},
        {"@context": "https://schema.org", "@type": "Service", "serviceType": cfg["service"],
         "provider": {"@type": "HomeAndConstructionBusiness", "name": "TML Garage Door Services",
                      "telephone": "+18328878747",
                      "address": {"@type": "PostalAddress", "streetAddress": "2330 FM 1488 #400",
                                  "addressLocality": "Conroe", "addressRegion": "TX", "postalCode": "77384"}},
         "areaServed": [f"{a} TX" for a in AREAS]},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in list(cfg["capsules"]) + list(cfg["faq"])]},
    ]
    h = h.replace("</head>", "".join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + "</script>"
                                     for s in schema) + CSS + "</head>", 1)

    if h != orig:
        p.write_text(h, "utf-8")
        n["pages"] += 1

missing = [k for k, v in FACTS.items() if v in ("", None)]
for k, v in sorted(n.items()):
    print(f"{k}: {v}")
print(f"\nplaceholders still empty ({len(missing)}): {', '.join(missing)}")
