#!/usr/bin/env python3
"""Rebuild the body of a service page: everything between the hero and the
shared footer blocks.

Architecture follows the order a homeowner with a broken door actually asks
things in:

  1. triage      - "is this what mine is doing?"  their symptom, within a screen
  2. price       - "what will this cost me?"      answered before we sell
  3. the work    - repair vs replace, side by side, with real photos
  4. proof       - 5.0 from 213 Google reviews
  5. specs       - types / features / brands, for the researcher not the panicked
  6. why us      - the client's own reasons, on a dark panel
  7. FAQ         - accordion
  8. area + CTA  - where we work, then one clear way to act

Every word of the client's copy is preserved; only sequence and presentation
change. Header, hero and the shared trailing blocks are not touched.

Idempotent. Currently scoped to one page for review.
"""
import html as H
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
PHONE, PHONE_HREF, SMS_HREF = "(832) 887-8747", "tel:+18328878747", "sms:+18328878747"
BOOK = "/fixed/schedule-consult"
A1 = "/assets/66b2dae9e779df43d0d269c9"
A2 = "/assets/66b2dae9e779df43d0d269e7"

PAGE = {
    "slug": "garage-door-opener-installation",
    "intro_h": "Professional Garage Door Opener Services in Houston &amp; Surrounding Areas",
    "intro_p": [
        "A dependable garage door opener makes daily life more convenient and keeps your garage "
        "secure. Whether your opener has stopped working, is making unusual noises, or you're ready "
        "to upgrade to a smart opener, TML Garage Door Services provides expert garage door opener "
        "installation, repair, and replacement throughout Houston and the surrounding areas.",
        "Our experienced technicians service all major garage door opener brands and can quickly "
        "diagnose the problem to get your garage door operating safely and reliably.",
    ],
    "triage_h": "Common Garage Door Opener Problems",
    "triage_lede": "If your garage door opener isn't working properly, we'll identify the issue and "
                   "recommend the most cost-effective solution.",
    "triage": ["Garage door opener won't work", "Remote control not responding",
               "Wall button not working", "Door won't open or close completely",
               "Garage door reverses unexpectedly", "Flashing opener lights",
               "Loud or unusual noises", "Motor runs but the door doesn't move",
               "Intermittent operation", "Safety sensors not working",
               "Keypad won't open the door", "Wi-Fi or smart opener connectivity issues"],
    "triage_close": "Our technicians arrive with the tools and common replacement parts needed to "
                    "complete many repairs during the first visit.",
    "jobs": [
        {"h": "Garage Door Opener Repair",
         "p": "If your garage door opener isn't working properly, we'll identify the issue and "
              "recommend the most cost-effective solution.",
         "img": f"{A2}/6a6fa5ef7c6dd0cbdbbc4d52_F18562D0-6DF1-4CBC-A9C4-1513524B9391.PNG",
         "alt": "TML technician showing a homeowner what failed on their garage door opener",
         "list_h": "", "list": []},
        {"h": "Garage Door Opener Installation &amp; Replacement",
         "p": "If your opener is outdated, damaged, or beyond repair, we can install a new system "
              "that delivers smooth, quiet, and dependable performance.",
         "img": f"{A1}/6a542e2ec6b8791b21582f07_Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png",
         "alt": "TML technician installing a new LiftMaster garage door opener",
         "list_h": "Our installation service includes:",
         "list": ["Removal of your old garage door opener", "Professional installation of a new opener",
                  "Rail and drive system installation", "Motor mounting and setup",
                  "Safety sensor installation", "Wall control installation", "Remote programming",
                  "Wireless keypad setup", "Smart phone app configuration (when available)",
                  "Complete safety testing", "Final adjustments and operation check"]},
    ],
    "jobs_close": "We'll make sure your new opener is properly adjusted and ready for reliable everyday use.",
    "specs": [
        ("Types of Garage Door Openers We Install", "We install and replace:",
         ["Belt Drive Garage Door Openers", "Chain Drive Garage Door Openers",
          "Wall Mount (Jackshaft) Openers", "Smart Wi-Fi Garage Door Openers",
          "Battery Backup Garage Door Openers", "Quiet Garage Door Openers",
          "Heavy-Duty Garage Door Openers"],
         "Our team can help you choose the best opener based on your garage door, budget, and "
         "desired features."),
        ("Features of Modern Garage Door Openers", "Available features include:",
         ["Smartphone control from anywhere", "Wi-Fi connectivity", "Battery backup operation",
          "LED lighting", "Rolling code security technology", "Quiet belt-drive systems",
          "Motion-detecting control panels", "Automatic locking features", "Multiple remote controls",
          "Wireless keypads"],
         "We'll explain your options and help you choose the right opener for your home."),
        ("Brands We Service", "Our technicians work on most major garage door opener brands, including:",
         ["LiftMaster", "Chamberlain", "Genie", "Craftsman", "Linear", "Marantec", "Guardian", "Sommer"],
         "Not sure what brand you have? We'll identify it during the inspection."),
    ],
    "why_h": "Why Choose TML Garage Door Services?",
    "why_lede": "Homeowners trust us because we provide:",
    "why": ["Experienced local technicians", "Fast scheduling and same-day service",
            "Honest, upfront pricing", "Quality replacement parts", "Professional installation",
            "Reliable repairs", "Friendly customer service", "Satisfaction-focused workmanship"],
    "why_close": "Our goal is to keep your garage door opener operating safely, quietly, and reliably.",
    "areas_h": "Serving Houston &amp; Nearby Communities",
    "areas_lede": "We proudly provide garage door opener services throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "If you're in the area, contact us to schedule your service.",
    "cta_h": "Schedule Your Garage Door Opener Service Today",
    "cta_p": "Same-day appointments across Conroe, The Woodlands, Spring and greater Houston — "
             "and a real person answers the phone.",
}

CSS = """<style id="tmlsv2-css">
.sv2{--g:#587735;--gd:#3f5a22;--ink:#1f2418;--mut:#535c48;--line:#dfe3d5;--cream:#f5f7ef;
 --shell:#fff;color:var(--ink);}
.sv2 *{box-sizing:border-box;}
.sv2 .sv2-wrap{width:min(100% - 40px,1060px);margin:0 auto;}
.sv2 .sv2-band{padding:clamp(40px,6vw,76px) 0;background:var(--shell);}
.sv2 .sv2-band.sv2-tint{background:var(--cream);}
.sv2 .sv2-band.sv2-tight{padding:clamp(28px,4vw,44px) 0;}
.sv2 h2{font-size:clamp(24px,3.6vw,36px);line-height:1.08;margin:0 0 14px;color:var(--ink);text-wrap:balance;}
.sv2 h3{font-size:clamp(19px,2.2vw,23px);line-height:1.15;margin:0 0 10px;color:var(--ink);}
.sv2 p{font-size:17px;line-height:1.62;color:var(--mut);margin:0 0 16px;max-width:64ch;text-wrap:pretty;}
.sv2 p:last-child{margin-bottom:0;}
.sv2 .sv2-kicker{font-size:17px;font-weight:700;color:var(--ink);margin:0 0 14px;}

/* trust strip under the hero */
.sv2 .sv2-trust{display:grid;gap:1px;background:var(--line);border-top:1px solid var(--line);
 border-bottom:1px solid var(--line);grid-template-columns:1fr;}
.sv2 .sv2-trust div{background:var(--shell);padding:16px 20px;}
.sv2 .sv2-trust b{display:block;font-size:15.5px;color:var(--ink);margin-bottom:2px;}
.sv2 .sv2-trust span{font-size:14.5px;color:var(--mut);line-height:1.45;}
@media(min-width:640px){.sv2 .sv2-trust{grid-template-columns:1fr 1fr;}}
@media(min-width:980px){.sv2 .sv2-trust{grid-template-columns:repeat(4,1fr);}}

/* symptom triage: ruled rows, not a field of boxes */
.sv2 .sv2-sym{list-style:none;margin:22px 0 24px;padding:0;display:grid;grid-template-columns:1fr;
 column-gap:36px;border-top:1px solid var(--line);}
.sv2 .sv2-sym li{display:flex;gap:12px;align-items:flex-start;padding:13px 2px;
 border-bottom:1px solid var(--line);font-size:16px;line-height:1.4;color:var(--ink);}
.sv2 .sv2-sym li::before{content:"";flex:0 0 auto;width:7px;height:7px;border-radius:50%;
 background:#b3352b;margin-top:8px;}
@media(min-width:620px){.sv2 .sv2-sym{grid-template-columns:1fr 1fr;}}
@media(min-width:940px){.sv2 .sv2-sym{grid-template-columns:repeat(3,1fr);}}

/* price: deliberately unlike anything else on the page */
.sv2 .sv2-price{border:2px dashed #9fb277;border-radius:14px;padding:clamp(20px,3vw,28px);background:var(--shell);}
.sv2 .sv2-price h2{font-size:clamp(21px,2.6vw,26px);margin-bottom:10px;}
.sv2 .sv2-price p{max-width:70ch;}

/* the two jobs */
.sv2 .sv2-jobs{display:grid;gap:clamp(26px,4vw,46px);grid-template-columns:1fr;}
@media(min-width:880px){.sv2 .sv2-jobs{grid-template-columns:1fr 1fr;}}
.sv2 .sv2-job figure{margin:0 0 18px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#eef0e7;}
.sv2 .sv2-job picture{display:block;}
.sv2 .sv2-job img{width:100%;display:block;aspect-ratio:16/11;object-fit:cover;}
.sv2 .sv2-check{list-style:none;margin:0;padding:0;display:grid;gap:10px;}
.sv2 .sv2-check li{display:flex;gap:11px;align-items:flex-start;font-size:15.5px;line-height:1.5;color:var(--mut);}
.sv2 .sv2-check li::before{content:"✓";flex:0 0 auto;width:21px;height:21px;border-radius:50%;
 background:var(--g);color:#fff;font-size:12px;font-weight:800;display:grid;place-items:center;}

/* specs: three plain groups, chips not cards */
.sv2 .sv2-specs{display:grid;gap:clamp(26px,4vw,40px);grid-template-columns:1fr;}
@media(min-width:820px){.sv2 .sv2-specs{grid-template-columns:repeat(3,1fr);align-items:start;}}
.sv2 .sv2-chips{list-style:none;margin:0 0 14px;padding:0;display:flex;flex-wrap:wrap;gap:8px;}
.sv2 .sv2-chips li{padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--shell);
 font-size:14.5px;font-weight:600;color:var(--ink);}
.sv2 .sv2-band.sv2-tint .sv2-chips li{background:var(--shell);}

/* why us */
.sv2 .sv2-dark{background:var(--ink);color:#fff;border-radius:18px;padding:clamp(24px,4.2vw,44px);}
.sv2 .sv2-dark h2{color:#fff;}
.sv2 .sv2-dark p{color:#c9d0bd;}
.sv2 .sv2-dark .sv2-kicker{color:#fff;}
.sv2 .sv2-dark .sv2-check{grid-template-columns:1fr;}
.sv2 .sv2-dark .sv2-check li{color:#dfe4d6;}
.sv2 .sv2-dark .sv2-check li::before{background:#cfe84d;color:#1f2418;}
@media(min-width:760px){.sv2 .sv2-dark .sv2-check{grid-template-columns:1fr 1fr;column-gap:30px;}}

/* areas */
.sv2 .sv2-areas{list-style:none;margin:0 0 16px;padding:0;display:flex;flex-wrap:wrap;gap:8px;}
.sv2 .sv2-areas li{padding:9px 15px;border:1px solid var(--line);border-radius:999px;background:var(--shell);
 font-size:14.5px;font-weight:600;color:var(--ink);}

/* closing CTA */
.sv2 .sv2-cta{background:var(--g);border-radius:18px;color:#fff;padding:clamp(24px,4.2vw,44px);}
.sv2 .sv2-cta h2{color:#fff;margin-bottom:8px;}
.sv2 .sv2-cta p{color:#eaf1de;max-width:56ch;margin-bottom:20px;}
.sv2 .sv2-acts{display:flex;flex-wrap:wrap;gap:11px;}
.sv2 .sv2-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;
 padding:0 22px;border-radius:11px;font-weight:800;font-size:16.5px;text-decoration:none;
 white-space:nowrap;flex:0 0 auto;
 transition:background .14s ease,color .14s ease,border-color .14s ease;}
.sv2 .sv2-btn.sv2-p{background:#fff;color:var(--ink);}
.sv2 .sv2-btn.sv2-p:hover{background:var(--ink);color:#fff;}
.sv2 .sv2-btn.sv2-s{background:transparent;color:#fff;border:2px solid rgba(255,255,255,.62);}
.sv2 .sv2-btn.sv2-s:hover{background:#fff;color:var(--ink);border-color:#fff;}
.sv2 .sv2-btn.sv2-ink{background:var(--ink);color:#fff;}
.sv2 .sv2-btn.sv2-ink:hover{background:var(--gd);}
.sv2 .sv2-btn.sv2-outline{background:var(--shell);color:var(--ink);border:2px solid var(--ink);}
.sv2 .sv2-btn.sv2-outline:hover{background:var(--ink);color:#fff;}

/* related services */
.sv2 .sv2-rel{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));}
.sv2 .sv2-rel a{display:block;padding:15px 17px;border:1px solid var(--line);border-radius:12px;
 background:var(--shell);color:var(--ink);text-decoration:none;font-weight:600;font-size:15.5px;
 transition:border-color .14s ease,color .14s ease;}
.sv2 .sv2-rel a:hover{border-color:var(--g);color:var(--gd);}

.sv2 .sv2-rule{border:0;border-top:1px solid var(--line);margin:0;}
</style>"""

WIDTHS = (500, 800, 1080)


def picture(url, alt, sizes, eager=False):
    cands = []
    for w in WIDTHS:
        d = url.rsplit(".", 1)[0] + f"-w{w}.webp"
        import urllib.parse
        if (SITE / urllib.parse.unquote(d).lstrip("/")).exists():
            cands.append(f"{d} {w}w")
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    img = f'<img src="{url}" alt="{alt}" {load} decoding="async">'
    if not cands:
        return img
    return ('<picture><source type="image/webp" srcset="' + ", ".join(cands)
            + f'" sizes="{sizes}">' + img + "</picture>")


def band(inner, tint=False, tight=False):
    cls = "sv2-band" + (" sv2-tint" if tint else "") + (" sv2-tight" if tight else "")
    return f'<div class="{cls}"><div class="sv2-wrap">{inner}</div></div>'


def acts(dark=True):
    a, b = ("sv2-btn sv2-p", "sv2-btn sv2-s") if dark else ("sv2-btn sv2-ink", "sv2-btn sv2-outline")
    return ('<div class="sv2-acts">'
            f'<a class="{a}" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
            f'<a class="{b}" href="{SMS_HREF}" data-book="text">&#128172; Text us</a>'
            f'<a class="{b}" href="{BOOK}" data-book="service-cta">Book online</a>'
            "</div>")


def keep(html, cls):
    """Pull an already-rendered component (reviews, FAQ) out of the old body."""
    m = re.search(r'<div class="%s"[^>]*>' % re.escape(cls), html)
    if not m:
        return ""
    depth = 1
    for t in re.finditer(r"<div\b|</div>", html[m.end():]):
        depth += 1 if t.group(0) == "<div" else -1
        if depth == 0:
            return html[m.start():m.end() + t.end()]
    return ""


def build(p, reviews, faq):
    out = []

    # 1. trust strip + intro
    out.append(band(
        '<div class="sv2-trust">'
        "<div><b>The price before the work</b><span>Upfront pricing with no hidden fees.</span></div>"
        "<div><b>Same-day &amp; emergency</b><span>No extra charge for weekends.</span></div>"
        "<div><b>Insured technicians</b><span>Well-trained, and they work for TML.</span></div>"
        "<div><b>100% satisfaction guaranteed</b><span>We're not done until the door works right.</span></div>"
        "</div>", tight=True))

    out.append(band(f'<h2>{p["intro_h"]}</h2>'
                    + "".join(f"<p>{H.escape(x)}</p>" for x in p["intro_p"])))

    # 2. triage — their symptom, first
    out.append(band(
        f'<h2>{H.escape(p["triage_h"])}</h2>'
        f'<p>{H.escape(p["triage_lede"])}</p>'
        '<ul class="sv2-sym">' + "".join(f"<li>{H.escape(x)}</li>" for x in p["triage"]) + "</ul>"
        f'<p>{H.escape(p["triage_close"])}</p>' + acts(dark=False), tint=True))

    # 3. price, before any selling
    out.append(band(
        '<div class="sv2-price"><h2>What will it cost?</h2>'
        "<p>Your technician diagnoses the problem on site and gives you the full price before any "
        f'work begins — fair, upfront pricing with no hidden fees. Call <a href="{PHONE_HREF}">{PHONE}</a> '
        "and we can talk through the likely range for your opener before we come out.</p></div>",
        tight=True))

    # 4. the two jobs
    jobs = []
    for i, j in enumerate(p["jobs"]):
        lst = ('<p class="sv2-kicker">' + H.escape(j["list_h"]) + "</p>"
               '<ul class="sv2-check">' + "".join(f"<li>{H.escape(x)}</li>" for x in j["list"]) + "</ul>"
               ) if j["list"] else ""
        jobs.append('<div class="sv2-job"><figure>'
                    + picture(j["img"], H.escape(j["alt"]),
                              "(min-width:880px) 46vw, 92vw", eager=(i == 0))
                    + f'</figure><h3>{j["h"]}</h3><p>{H.escape(j["p"])}</p>{lst}</div>')
    out.append(band('<div class="sv2-jobs">' + "".join(jobs) + "</div>"
                    f'<p style="margin-top:26px">{H.escape(p["jobs_close"])}</p>'))

    # 5. proof
    if reviews:
        out.append(band(reviews, tint=True))

    # 6. specs for the researcher
    specs = []
    for h, lede, items, close in p["specs"]:
        specs.append(f'<div><h3>{h}</h3><p>{H.escape(lede)}</p>'
                     '<ul class="sv2-chips">' + "".join(f"<li>{H.escape(x)}</li>" for x in items) + "</ul>"
                     f"<p>{H.escape(close)}</p></div>")
    out.append(band('<div class="sv2-specs">' + "".join(specs) + "</div>"))

    # 7. why us, in the client's own words
    out.append(band(
        f'<div class="sv2-dark"><h2>{H.escape(p["why_h"])}</h2>'
        f'<p class="sv2-kicker">{H.escape(p["why_lede"])}</p>'
        '<ul class="sv2-check">' + "".join(f"<li>{H.escape(x)}</li>" for x in p["why"]) + "</ul>"
        f'<p style="margin-top:18px">{H.escape(p["why_close"])}</p></div>', tight=True))

    # 8. FAQ
    if faq:
        out.append(band(faq, tint=True))

    # 9. where we work
    out.append(band(
        f'<h2>{p["areas_h"]}</h2><p>{H.escape(p["areas_lede"])}</p>'
        '<ul class="sv2-areas">' + "".join(f"<li>{H.escape(x)}</li>" for x in p["areas"]) + "</ul>"
        f'<p>{H.escape(p["areas_close"])}</p>', tight=True))

    # 10. one clear way to act
    out.append(band(f'<div class="sv2-cta"><h2>{H.escape(p["cta_h"])}</h2>'
                    f'<p>{H.escape(p["cta_p"])}</p>' + acts(dark=True) + "</div>", tight=True))

    # 11. related services
    out.append(band(
        '<h3 style="margin-bottom:14px">Other services</h3><div class="sv2-rel">'
        '<a href="/fixed/our-services/residential-garage-door-services">New Garage Door Installation</a>'
        '<a href="/fixed/our-services/garage-door-spring-replacement">Garage Door Spring Replacement</a>'
        '<a href="/fixed/our-services/commercial-garage-door-installation">Commercial Garage Doors</a>'
        "</div>", tight=True))

    return '<div class="sv2">' + "".join(out) + "</div>"


def main():
    page = SITE / "fixed" / "our-services" / PAGE["slug"] / "index.html"
    html = page.read_text("utf-8", errors="replace")

    # strip the previous run's stylesheet FIRST: it lives in <head>, so removing it
    # after computing offsets would shift every index below it
    html = re.sub(r'<style id="tmlsv2-css">.*?</style>', "", html, flags=re.S)

    reviews = keep(html, "tmlrev")
    faq = keep(html, "tmlfaq")

    m = re.search(r'<section class="section-3"[^>]*>', html)
    if not m:
        print("section-3 not found — nothing rebuilt")
        return
    depth, end = 1, None
    for t in re.finditer(r"<section\b|</section>", html[m.end():]):
        depth += 1 if t.group(0) == "<section" else -1
        if depth == 0:
            end = m.end() + t.start()
            break
    if end is None:
        print("could not find the end of section-3")
        return

    body = build(PAGE, reviews, faq)
    html = html[:m.end()] + body + html[end:]
    html = html.replace("</head>", CSS + "</head>", 1)
    page.write_text(html, "utf-8")
    print(f"rebuilt body: {PAGE['slug']}  (reviews kept: {bool(reviews)}, faq kept: {bool(faq)})")


if __name__ == "__main__":
    main()
