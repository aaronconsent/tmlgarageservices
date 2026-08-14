#!/usr/bin/env python3
"""Bake TML's real Google reviews into site/fixed/ as server-rendered HTML
plus LocalBusiness/AggregateRating/Review JSON-LD (replaces the quota-broken
Trustmary + Elfsight widgets). Re-run after `reviews.py --fresh`."""
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

CARDS = "".join(
    f'<figure class="tmlrev-card"><div class="tmlrev-stars" aria-label="5 out of 5 stars">★★★★★</div>'
    f'<blockquote>{H.escape(r["text"])}</blockquote>'
    f'<figcaption>{H.escape(r["name"])} · Google review · {r["date"]}</figcaption></figure>'
    for r in FEATURED)

SECTION = (
    '<div class="tmlrev">'
    f'<p class="tmlrev-agg"><strong>Rated {RATING}.0 ★ from {COUNT} Google reviews</strong></p>'
    f'<div class="tmlrev-grid">{CARDS}</div>'
    f'<p class="tmlrev-link"><a href="{GOOGLE_URL}" target="_blank" rel="noopener">Read all {COUNT} reviews on Google →</a></p>'
    '</div>')

STYLE = ('<style id="tmlrev-css">'
         '.tmlrev{padding:8px 0;}'
         '.tmlrev-agg{text-align:center;font-size:20px;margin:0 0 18px;}'
         '.tmlrev-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:16px;text-align:left;}'
         '.tmlrev-card{margin:0;background:#fff;border:1px solid #e2e2da;border-radius:10px;padding:18px;box-shadow:0 8px 22px -14px rgba(20,27,13,.25);}'
         '.tmlrev-stars{color:#e7a600;letter-spacing:2px;font-size:15px;margin-bottom:8px;}'
         '.tmlrev-card blockquote{margin:0 0 10px;font-size:15px;line-height:1.55;color:#30302f;}'
         '.tmlrev-card figcaption{font-size:13px;color:#6c6c66;}'
         '.tmlrev-link{text-align:center;margin:18px 0 0;}'
         '.tmlrev-link a{font-weight:600;color:#587735;}'
         '</style>')

TRUSTMARY = re.compile(r'<div class="code-embed w-embed w-script"><script src="https://widget\.trustmary\.com/[^"]*"></script></div>')
ELFSIGHT = re.compile(r'<div class="[^"]*w-embed w-script"><!-- Elfsight[^>]*-->\s*<script src="https://elfsightcdn\.com/platform\.js" async></script>\s*<div class="elfsight-app-[^"]*"[^>]*></div></div>', re.S)

def schema(with_reviews):
    biz = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": "https://www.tmlgarageservices.com/#business",
        "name": "TML Garage Door Services",
        "telephone": "+18328878747",
        "email": "info@tmlgarageservices.com",
        "url": "https://www.tmlgarageservices.com/",
        "image": "https://tmlgarageservices.aironz.workers.dev/assets/66b2dae9e779df43d0d269c9/66b5115cc6a1fdc1f8b546d6_modern-garage-door-services.jpg",
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
    h, r1 = TRUSTMARY.subn(SECTION, h)
    h, r2 = ELFSIGHT.subn(SECTION, h)
    n["widgets_replaced"] += r1 + r2
    has_reviews = r1 + r2 > 0
    # refresh any previous bake artifacts
    h = re.sub(r'<style id="tmlrev-css">.*?</style>', "", h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "LocalBusiness".*?</script>', "", h, flags=re.S)
    if has_reviews:
        h = h.replace("</head>", STYLE + "</head>", 1)
    h = h.replace("</head>", schema(has_reviews) + "</head>", 1)
    n["schema_added"] += 1
    if h != orig:
        f.write_text(h, "utf-8")
        n["pages_changed"] += 1

print(f"featured reviews: {len(FEATURED)} | rating {RATING}.0 x {COUNT}")
for k, v in sorted(n.items()):
    print(f"{k}: {v}")
