#!/usr/bin/env python3
"""Service pages: separate the closing CTA from the FAQ, and give each its
own styled block.

The legacy pages are one flat rich-text blob: ... <h2>Frequently Asked
Questions</h2> h3/p pairs ... <h2>Schedule ... Today</h2> p ... CTA link.
That made the booking CTA read as another FAQ answer.

This wraps the FAQ Q&As in their own card block (with FAQPage schema for
search/AI engines) and lifts the closing CTA into a distinct green band.
Idempotent.
"""
import html as H
import json
import re
from pathlib import Path
from collections import Counter

F = Path(__file__).parent / "site" / "fixed" / "our-services"
n = Counter()

PHONE_HREF = "tel:+18328878747"
PHONE_DISPLAY = "(832) 887-8747"
BOOK = "/fixed/schedule-consult"

CSS = (
    '<style id="tmlfaq-css">'
    '.tmlfaq{margin:26px 0 8px;}'
    '.tmlfaq-h{font-size:clamp(21px,3vw,28px);margin:0 0 14px;color:#1f2418;}'
    '.tmlfaq details{background:#fff;border:1px solid #e2e5d9;border-radius:12px;margin-bottom:10px;overflow:hidden;}'
    '.tmlfaq details[open]{box-shadow:0 10px 26px -18px rgba(20,27,13,.5);}'
    '.tmlfaq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:14px;'
    'align-items:center;padding:15px 18px;font-weight:700;font-size:16.5px;color:#1f2418;}'
    '.tmlfaq summary::-webkit-details-marker{display:none;}'
    '.tmlfaq summary::after{content:"+";font-size:22px;line-height:1;color:#587735;transition:transform .2s ease;}'
    '.tmlfaq details[open] summary::after{transform:rotate(45deg);}'
    '.tmlfaq details p{margin:0;padding:0 18px 16px;color:#5c6553;font-size:15.5px;line-height:1.6;}'
    '.tmlcta{background:#587735;border-radius:16px;padding:clamp(22px,4vw,34px);margin:30px 0 10px;color:#fff;}'
    '.tmlcta h2{color:#fff!important;font-size:clamp(21px,3vw,29px);margin:0 0 10px;max-width:22ch;}'
    '.tmlcta p{color:#eef3e6!important;font-size:16px;line-height:1.6;margin:0 0 10px;max-width:64ch;}'
    '.tmlcta-acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px;}'
    '.tmlcta-acts a{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:0 24px;'
    'border-radius:10px;font-weight:800;font-size:16.5px;text-decoration:none;white-space:nowrap;}'
    '.tmlcta-call{background:#fff;color:#1f2418;}'
    '.tmlcta-call:hover{background:#1f2418;color:#fff;}'
    '.tmlcta-book{background:#1f2418;color:#fff;border:2px solid rgba(255,255,255,.45);}'
    '.tmlcta-book:hover{background:#fff;color:#1f2418;border-color:#fff;}'
    "</style>")

FAQ_H2 = re.compile(r"<h2>\s*Frequently Asked Questions\s*</h2>", re.I)
QA = re.compile(r"<h3>(?P<q>.*?)</h3>\s*(?P<a>(?:<p>.*?</p>\s*)+)", re.S)
NEXT_H2 = re.compile(r"<h2>", re.I)

for f in sorted(F.glob("*/index.html")):
    h = orig = f.read_text("utf-8", errors="replace")
    m = FAQ_H2.search(h)
    if not m:
        continue
    if "tmlfaq" in h:                       # already processed; rebuild from scratch
        h = re.sub(r'<style id="tmlfaq-css">.*?</style>', "", h, flags=re.S)

    # ---- 1. the FAQ run: from the heading to the next <h2> --------------
    start = m.start()
    nxt = NEXT_H2.search(h, m.end())
    faq_end = nxt.start() if nxt else len(h)
    faq_body = h[m.end():faq_end]

    pairs = [(H.unescape(re.sub(r"<[^>]+>", "", q)).strip(),
              H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a))).strip())
             for q, a in QA.findall(faq_body)]
    if not pairs:
        continue

    faq_html = ('<div class="tmlfaq"><h2 class="tmlfaq-h">Frequently asked questions</h2>'
                + "".join(f"<details><summary>{H.escape(q)}</summary><p>{H.escape(a)}</p></details>"
                          for q, a in pairs)
                + "</div>")

    # ---- 2. the closing CTA: next <h2> block through its button --------
    cta_html = ""
    cta_end = faq_end
    if nxt:
        after = h[nxt.start():]
        head_m = re.match(r"<h2>(?P<t>.*?)</h2>", after, re.S)
        btn_m = re.search(r'<a[^>]*>\s*Get a FREE Quote\s*</a>', after, re.I)
        if head_m and btn_m and btn_m.start() < 2600:
            title = H.unescape(re.sub(r"<[^>]+>", "", head_m.group("t"))).strip()
            body = after[head_m.end():btn_m.start()]
            paras = [H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", p))).strip()
                     for p in re.findall(r"<p>.*?</p>", body, re.S)]
            paras = [p for p in paras if len(p) > 2]
            cta_html = (
                '<div class="tmlcta">'
                f"<h2>{H.escape(title)}</h2>"
                + "".join(f"<p>{H.escape(p)}</p>" for p in paras)
                + '<div class="tmlcta-acts">'
                f'<a class="tmlcta-call" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE_DISPLAY}</a>'
                f'<a class="tmlcta-book" href="{BOOK}" data-book="service-cta">Book online</a>'
                "</div></div>")
            cta_end = nxt.start() + btn_m.end()
            n["ctas"] += 1

    # the cut region carried closing </div>s (it ended inside the old CTA's
    # wrapper); the replacement is self-balanced, so re-emit whatever it closed
    # or the page ends up with an unclosed <div> and the sidebar gets swallowed
    cut = h[start:cta_end]
    orphan_closers = cut.count("</div>") - len(re.findall(r"<div\b", cut))
    h = h[:start] + faq_html + cta_html + "</div>" * max(0, orphan_closers) + h[cta_end:]
    n["faqs"] += 1

    # ---- 3. FAQPage schema (search + AI engines can quote these) -------
    h = re.sub(r'<script type="application/ld\+json">\{"@context": ?"https://schema\.org", ?"@type": ?"FAQPage".*?</script>', "", h, flags=re.S)
    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
    h = h.replace("</head>", '<script type="application/ld+json">'
                  + json.dumps(schema, ensure_ascii=False) + "</script>" + CSS + "</head>", 1)

    if h != orig:
        f.write_text(h, "utf-8")
        n["pages"] += 1

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
