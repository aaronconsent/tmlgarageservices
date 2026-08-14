#!/usr/bin/env python3
"""Bake TML's real Google reviews into site/fixed/ as a showcase section:
desktop = score rail + card grid; mobile = swipeable snap-carousel with 2s
autoplay (pauses on touch, disabled under prefers-reduced-motion).
Server-rendered HTML + LocalBusiness/AggregateRating/Review JSON-LD.
Idempotent: replaces widget embeds or any previously-baked section.
Re-run after `reviews.py --fresh`."""
import html as H
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"
n = Counter()

data = json.load(open(ROOT / "data-reviews" / "reviews.json"))
res = data["tasks"][0]["result"][0]
RATING = res["rating"]["value"]
COUNT = res["reviews_count"]
GOOGLE_URL = "https://search.google.com/local/reviews?placeid=ChIJGcCLGTc7R4YR9gwp3xFvXps"
AUTOPLAY_MS = 2000  # mobile carousel interval

def featured(items, want=6):
    picks = []
    for it in items or []:
        text = (it.get("review_text") or "").strip()
        if it.get("rating", {}).get("value") != 5 or len(text) < 100:
            continue
        picks.append({
            "name": (it.get("profile_name") or "Google user").strip(),
            "date": (it.get("timestamp") or "")[:10],
            "text": text if len(text) <= 300 else text[:280].rsplit(" ", 1)[0] + "…",
            "full": text,
        })
        if len(picks) == want:
            break
    return picks

FEATURED = featured(res.get("items"))

G_SVG = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
         '<path fill="#4285F4" d="M23.5 12.3c0-.9-.1-1.5-.3-2.2H12v4.1h6.6c-.1 1.1-.9 2.8-2.5 3.9l3.8 2.9c2.3-2.1 3.6-5.2 3.6-8.7z"/>'
         '<path fill="#34A853" d="M12 24c3.2 0 6-1.1 7.9-2.9l-3.8-2.9c-1 .7-2.4 1.2-4.1 1.2-3.2 0-5.9-2.1-6.8-5L1.3 17.3C3.3 21.3 7.3 24 12 24z"/>'
         '<path fill="#FBBC05" d="M5.2 14.4c-.2-.7-.4-1.5-.4-2.4s.1-1.6.4-2.4L1.3 6.7C.5 8.3 0 10.1 0 12s.5 3.7 1.3 5.3l3.9-2.9z"/>'
         '<path fill="#EA4335" d="M12 4.6c1.8 0 3 .8 3.7 1.4l3.4-3.3C17.9 1 15.2 0 12 0 7.3 0 3.3 2.7 1.3 6.7l3.9 2.9c.9-2.9 3.6-5 6.8-5z"/></svg>')

def initial_badge(name):
    ch = next((c for c in name if c.isalpha()), "T").upper()
    return f'<span class="tmlrev-init" aria-hidden="true">{ch}</span>'

CARDS = "".join(
    '<figure class="tmlrev-card">'
    '<div class="tmlrev-stars" aria-label="5 out of 5 stars">★★★★★</div>'
    f'<blockquote>{H.escape(r["text"])}</blockquote>'
    f'<figcaption>{initial_badge(r["name"])}<span class="who"><b>{H.escape(r["name"])}</b>'
    f'<small>{G_SVG} Google review · {r["date"]}</small></span></figcaption>'
    "</figure>"
    for r in FEATURED)

DOTS = "".join(f'<button class="tmlrev-dot{" on" if i == 0 else ""}" aria-label="Review {i+1}"></button>'
               for i in range(len(FEATURED)))

SECTION = (
    "<!--tmlrev-->"
    '<div class="tmlrev">'
    '<div class="tmlrev-rail">'
    f'<span class="tmlrev-big">{RATING}.0</span>'
    '<span class="tmlrev-bigstars" aria-hidden="true">★★★★★</span>'
    f'<span class="tmlrev-sub">{G_SVG} <b>{COUNT} five-star</b>&nbsp;Google reviews</span>'
    f'<a class="tmlrev-btn" href="{GOOGLE_URL}" target="_blank" rel="noopener">Read them all on Google</a>'
    "</div>"
    f'<div class="tmlrev-wrap"><div class="tmlrev-track" data-autoplay="{AUTOPLAY_MS}">{CARDS}</div>'
    f'<div class="tmlrev-dots">{DOTS}</div></div>'
    "</div>"
    "<!--/tmlrev-->")

STYLE = ('<style id="tmlrev-css">'
         '.tmlrev{display:grid;gap:26px;padding:10px 0;text-align:left;width:100%;max-width:100%;min-width:0;box-sizing:border-box;}''.tmlrev-wrap,.tmlrev-track{min-width:0;max-width:100%;}'
         '.tmlrev-rail{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;}'
         '.tmlrev-big{font-size:76px;line-height:1;font-weight:800;color:#1f2418;letter-spacing:-2px;}'
         '.tmlrev-bigstars{color:#f5b301;font-size:30px;letter-spacing:5px;text-shadow:0 1px 0 rgba(0,0,0,.08);}'
         '.tmlrev-sub{display:inline-flex;align-items:baseline;flex-wrap:wrap;gap:6px;font-size:16px;color:#3c4633;max-width:16em;}'
         '.tmlrev-sub svg{flex:0 0 auto;}'
         '.tmlrev-btn{display:inline-block;margin-top:12px;background:#587735;color:#fff;font-weight:700;'
         'padding:13px 26px;border-radius:999px;text-decoration:none;letter-spacing:.02em;'
         'box-shadow:0 8px 20px -8px rgba(46,63,23,.55);transition:transform .15s ease;}'
         '.tmlrev-btn:active{transform:scale(.97);}'
         '.tmlrev-track{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;}'
         '.tmlrev-card{margin:0;background:#fff;border:1px solid #e4e6dc;border-radius:16px;padding:22px;'
         'box-shadow:0 14px 30px -18px rgba(20,27,13,.35);display:flex;flex-direction:column;}'
         '.tmlrev-stars{color:#f5b301;letter-spacing:3px;font-size:17px;margin-bottom:10px;}'
         '.tmlrev-card blockquote{margin:0 0 16px;font-size:15px;line-height:1.6;color:#30302f;flex:1;}'
         '.tmlrev-card figcaption{display:flex;align-items:center;gap:10px;}'
         '.tmlrev-init{flex:0 0 auto;width:40px;height:40px;border-radius:50%;background:#587735;color:#fff;'
         'display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:17px;}'
         '.tmlrev-card .who{display:flex;flex-direction:column;line-height:1.3;}'
         '.tmlrev-card .who b{font-size:14px;color:#1f2418;}'
         '.tmlrev-card .who small{display:inline-flex;align-items:center;gap:5px;color:#6c6c66;font-size:12px;margin-top:2px;}'
         '.tmlrev-card .who small svg{width:13px;height:13px;}'
         '.tmlrev-dots{display:none;}'
         '@media(min-width:768px){'
         '.tmlrev{grid-template-columns:290px minmax(0,1fr);align-items:center;}'
         '.tmlrev-rail{align-items:flex-start;text-align:left;position:sticky;top:110px;}'
         '}'
         '@media(max-width:767px){'
         '.tmlrev-track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:14px;'
         'padding:4px 4px 12px;margin:0 -4px;-webkit-overflow-scrolling:touch;scrollbar-width:none;}'
         '.tmlrev-track::-webkit-scrollbar{display:none;}'
         '.tmlrev-card{flex:0 0 min(86vw,420px);scroll-snap-align:center;}'
         '.tmlrev-dots{display:flex;justify-content:center;gap:8px;margin-top:2px;}'
         '.tmlrev-dot{width:8px;height:8px;border-radius:50%;border:0;padding:0;background:#c9cfbc;cursor:pointer;}'
         '.tmlrev-dot.on{background:#587735;width:22px;border-radius:99px;transition:width .2s ease;}'
         '}'
         '</style>')

SCRIPT = ("<script id=\"tmlrev-js\">(function(){"
          "if(window.__tmlrev)return;window.__tmlrev=1;"
          "var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;"
          "document.querySelectorAll('.tmlrev-wrap').forEach(function(wrap){"
          "var track=wrap.querySelector('.tmlrev-track');"
          "var dots=[].slice.call(wrap.querySelectorAll('.tmlrev-dot'));"
          "var cards=[].slice.call(track.children);if(!cards.length)return;"
          "var idx=0,timer=null,hold=false;"
          "function setDot(i){dots.forEach(function(d,j){d.classList.toggle('on',j===i);});}"
          "function go(i,smooth){idx=(i+cards.length)%cards.length;"
          "var c=cards[idx];track.scrollTo({left:c.offsetLeft-(track.clientWidth-c.clientWidth)/2,"
          "behavior:smooth===false?'auto':'smooth'});setDot(idx);}"
          "function isMobile(){return matchMedia('(max-width:767px)').matches;}"
          "function tick(){if(!hold&&isMobile()&&!document.hidden)go(idx+1);}"
          "function start(){if(reduce||timer)return;"
          "timer=setInterval(tick,parseInt(track.dataset.autoplay||'2000',10));}"
          "['pointerdown','touchstart'].forEach(function(ev){"
          "track.addEventListener(ev,function(){hold=true;clearTimeout(track.__r);"
          "track.__r=setTimeout(function(){hold=false;},6000);},{passive:true});});"
          "track.addEventListener('scroll',function(){clearTimeout(track.__s);"
          "track.__s=setTimeout(function(){var m=0,best=0;cards.forEach(function(c,j){"
          "var v=Math.min(c.offsetLeft+c.clientWidth,track.scrollLeft+track.clientWidth)-"
          "Math.max(c.offsetLeft,track.scrollLeft);if(v>m){m=v;best=j;}});idx=best;setDot(idx);},80);},{passive:true});"
          "dots.forEach(function(d,j){d.addEventListener('click',function(){hold=true;go(j);"
          "clearTimeout(track.__r);track.__r=setTimeout(function(){hold=false;},6000);});});"
          "start();});})();</script>")

TRUSTMARY = re.compile(r'<div class="code-embed w-embed w-script"><script src="https://widget\.trustmary\.com/[^"]*"></script></div>')
ELFSIGHT = re.compile(r'<div class="[^"]*w-embed w-script"><!-- Elfsight[^>]*-->\s*<script src="https://elfsightcdn\.com/platform\.js" async></script>\s*<div class="elfsight-app-[^"]*"[^>]*></div></div>', re.S)
OLD_BAKE = re.compile(r'(?:<!--tmlrev-->.*?<!--/tmlrev-->|<div class="tmlrev">.*?Read all \d+ reviews on Google[^<]*</a></p></div>)', re.S)

def schema(with_reviews):
    biz = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": "https://www.tmlgarageservices.com/#business",
        "name": "TML Garage Door Services",
        "telephone": "+18328878747",
        "email": "info@tmlgarageservices.com",
        "url": "https://www.tmlgarageservices.com/",
        "image": "https://tmlgarageservices.aironz.workers.dev/assets/tml-og.jpg",
        "address": {"@type": "PostalAddress", "streetAddress": "2330 FM 1488 #400",
                    "addressLocality": "Conroe", "addressRegion": "TX", "postalCode": "77384"},
        "areaServed": ["Conroe TX", "The Woodlands TX", "Spring TX", "Montgomery TX", "Magnolia TX", "Willis TX", "Tomball TX", "Houston TX"],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": f"{RATING}.0",
                            "reviewCount": COUNT, "bestRating": "5"},
    }
    if with_reviews:
        biz["review"] = [{
            "@type": "Review",
            "author": {"@type": "Person", "name": r["name"]},
            "datePublished": r["date"],
            "reviewBody": r["full"],
            "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
        } for r in FEATURED]
    return '<script type="application/ld+json">' + json.dumps(biz, ensure_ascii=False) + "</script>"

for f in F.rglob("index.html"):
    h = orig = f.read_text("utf-8", errors="replace")
    h, r0 = OLD_BAKE.subn(SECTION, h)
    h, r1 = TRUSTMARY.subn(SECTION, h)
    h, r2 = ELFSIGHT.subn(SECTION, h)
    n["sections"] += r0 + r1 + r2
    has_reviews = r0 + r1 + r2 > 0
    h = re.sub(r'<style id="tmlrev-css">.*?</style>', "", h, flags=re.S)
    h = re.sub(r'<script id="tmlrev-js">.*?</script>', "", h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "LocalBusiness".*?</script>', "", h, flags=re.S)
    if has_reviews:
        h = h.replace("</head>", STYLE + "</head>", 1)
        h = h.replace("</body>", SCRIPT + "</body>", 1)
    h = h.replace("</head>", schema(has_reviews) + "</head>", 1)
    if h != orig:
        f.write_text(h, "utf-8")
        n["pages_changed"] += 1

print(f"featured {len(FEATURED)} reviews | {RATING}.0 x {COUNT}")
for k, v in sorted(n.items()):
    print(f"{k}: {v}")
