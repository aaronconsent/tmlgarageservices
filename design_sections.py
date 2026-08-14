#!/usr/bin/env python3
"""Turn the long rich-text blocks on the service pages into designed
sections: alternating photo/text splits, symptom cards, checklist panels
and type grids — using TML's own photo library (no stock, no AI people).

Runs AFTER build_service_pages.py. Idempotent.
"""
import html as H
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent
SITE = ROOT / "site"
F = SITE / "fixed" / "our-services"
n = Counter()

A1 = "/assets/66b2dae9e779df43d0d269c9"
A2 = "/assets/66b2dae9e779df43d0d269e7"

# real TML photos, matched to what each section is actually about
IMG = {
    "spring-hero": f"{A1}/6a543368b89f6b6fe88b1284_1F1EB104-997F-40F2-AAC8-9630A0DF66CC.PNG",
    "spring-product": f"{A2}/6a54260670dbe02d7e8ec87f_68DF2D4A-C38C-4154-B26F-3D2148B574F7.PNG",
    "opener-install": f"{A1}/6a542e2ec6b8791b21582f07_Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png",
    "opener-customer": f"{A1}/6a6fa5ef7c6dd0cbdbbc4d52_F18562D0-6DF1-4CBC-A9C4-1513524B9391.PNG",
    "opener-wiring": f"{A1}/6a6f95756ecb7a47b54e82e8_IMG_3555.jpg",
    "door-traditional": f"{A1}/66b2ec2555069ca418a48646_garage-door-repair-and-installer.png",
    "door-modern": f"{A1}/66b2f63fedd0e3b2f83a04ae_555249ec745308b19d24469f04c99071_modern%20doors.png",
    "door-carriage": f"{A1}/66b2ec26499b608d7f02271d_garage-door-services.png",
    "door-chevron": f"{A1}/6a5d16d6089f1016a7e8321a_reserve-le-chevron-822.webp",
    "door-new": f"{A1}/66b2ec2561b760fe6fee299b_549fbd18a3bc84b4e30fc12d9d7d4ccb_new-garage-door-service-install-conroe.png",
    "tech-driver": f"{A1}/6a5d15f2cf5561baa2f5b51c_2026-07-18%20(1).png",
    "resi-tech": f"{A1}/6a542a3cc1d76f4028c06fb8_2C6A44D6-3090-4449-81C8-D96132FB7ED7.PNG",
    "commercial-bay": f"{A1}/6a543355c034cb7d551b686f_E796B398-C84E-4B4B-8948-E05CBCB1864E.PNG",
    "commercial-dock": f"{A2}/6a5433d6f361bf9f86682598_C2BB1CBF-4898-4C21-96DA-1E25A82EBDF2.PNG",
}

# per page: which photo pairs with which heading, and how that block renders
PLAN = {
    "garage-door-spring-replacement": {
        "signs you need": ("cards", IMG["spring-hero"], "TML technician adjusting a garage door torsion spring"),
        "our spring replacement service includes": ("checklist", IMG["tech-driver"], "TML technician servicing garage door hardware"),
        "we replace all types": ("grid", IMG["resi-tech"], "TML technician checking garage door spring hardware"),
        "why choose us": ("skip", "", ""),
        "serving houston": ("skip", None, ""),
    },
    "garage-door-opener-installation": {
        "common garage door opener problems": ("cards", IMG["opener-customer"], "TML technician showing a homeowner a LiftMaster opener"),
        "opener installation &": ("checklist", IMG["opener-install"], "TML technician installing a LiftMaster garage door opener"),
        "types of garage door openers": ("grid", IMG["opener-wiring"], "TML technician wiring a ceiling-mounted opener"),
        "features of modern": ("grid", "", ""),
        "brands we service": ("chips", "", ""),
        "why choose": ("skip", "", ""),
        "serving houston": ("skip", None, ""),
    },
    "residential-garage-door-services": {
        "why install a new garage door": ("cards", IMG["door-new"], "Newly installed garage door in Conroe"),
        "our garage door installation service includes": ("checklist", IMG["tech-driver"], "TML technician at a completed garage door installation"),
        "garage door styles we install": ("gallery", "", ""),
        "why choose": ("skip", "", ""),
        "serving houston": ("skip", None, ""),
    },
    "commercial-garage-door-installation": {
        "common commercial garage door problems": ("cards", "", ""),
        "commercial garage door installation": ("checklist", IMG["commercial-bay"], "TML technician at a commercial door installation"),
        "types of commercial doors": ("grid", "", ""),
        "commercial door operator": ("checklist", IMG["opener-wiring"], "TML technician wiring a commercial door operator"),
        "preventive maintenance": ("checklist", IMG["tech-driver"], "TML service van on a scheduled maintenance route"),
        "industries we serve": ("grid", "", ""),
        "why choose": ("skip", "", ""),
        "serving houston": ("skip", None, ""),
    },
}

# door styles -> photos, for the residential gallery
STYLE_IMG = {
    "traditional raised panel": IMG["door-traditional"],
    "modern": IMG["door-modern"],
    "carriage house": IMG["door-chevron"],
}

CSS = """<style id="tmlsec-css">
.ds{--g:#587735;--gd:#3f5a22;--ink:#1f2418;--mut:#5c6553;--line:#e2e5d9;}
.ds-split{display:grid;gap:20px;grid-template-columns:1fr;align-items:center;margin:30px 0;}
.ds-split.flip .ds-shot{order:2;}
.ds-shot{border-radius:14px;overflow:hidden;background:#eef0e7;}
.ds-shot img{width:100%;height:100%;object-fit:cover;aspect-ratio:4/3;display:block;}
.ds-h{font-size:clamp(20px,3vw,27px);margin:0 0 10px;color:var(--ink);}
.ds-lede{color:var(--mut);font-size:15.5px;line-height:1.6;margin:0 0 14px;}
.ds-cards{display:grid;gap:10px;grid-template-columns:1fr;}
.ds-card{display:flex;gap:10px;align-items:flex-start;background:#fff;border:1px solid var(--line);
 border-radius:10px;padding:12px 14px;font-size:15px;color:var(--ink);line-height:1.45;}
.ds-card::before{content:"!";flex:0 0 auto;width:22px;height:22px;border-radius:50%;background:#fdeceb;
 color:#b3352b;font-weight:800;font-size:13px;display:grid;place-items:center;margin-top:1px;}
.ds .ds-check{display:grid;gap:9px;grid-template-columns:1fr;margin:0;padding:0!important;list-style:none!important;}
.ds .ds-check li{display:flex;gap:10px;align-items:flex-start;color:var(--mut);font-size:15px;line-height:1.5;}
.ds .ds-check li::before{content:"✓";flex:0 0 auto;width:21px;height:21px;border-radius:50%;background:var(--g);
 color:#fff;font-size:12px;font-weight:800;display:grid;place-items:center;}
.ds-grid{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(min(210px,100%),1fr));}
.ds-tile{background:#f6f8f1;border:1px solid var(--line);border-radius:10px;padding:13px 15px;
 font-weight:600;color:var(--ink);font-size:15px;}
.ds-grid-tail{margin-top:14px;}
.ds-gal{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));}
.ds-galitem{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;}
.ds-galitem img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;}
.ds-galitem span{display:block;padding:11px 14px;font-weight:600;color:var(--ink);font-size:14.5px;}
.ds .ds-chips{display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;gap:8px;padding:0!important;margin:0;list-style:none!important;}
.ds .ds-chips li{display:inline-block!important;width:auto!important;padding:8px 14px;border-radius:999px;border:1px solid var(--line);
 background:#fff;color:var(--ink);font-weight:600;font-size:14px;}
.ds-prose{margin:24px 0;max-width:74ch;}
.ds-band{background:#f6f8f1;border-radius:14px;padding:clamp(18px,3vw,26px);margin:26px 0;}
@media(min-width:820px){
 .ds-split{grid-template-columns:1fr 1fr;gap:34px;}
 .ds-cards{grid-template-columns:1fr 1fr;}
 .ds .ds-check{grid-template-columns:1fr 1fr;}
}
</style>"""


def blocks_from(rich: str):
    """Split the rich-text HTML into (heading, inner_html) chunks."""
    # promote "Our Service Includes"-style paragraphs (short, followed by a list)
    # a short lead-in that is NOT a colon-introduced lede acts as its own heading
    rich = re.sub(r"<p>((?:(?!</p>).){0,90}?[^:\s])\s*</p>\s*(?=<ul)",
                  lambda m: "<h3>" + m.group(1) + "</h3>", rich, flags=re.S)
    parts = re.split(r"(<h[23]>.*?</h[23]>)", rich, flags=re.S)
    out, cur_h, buf = [], None, []
    for seg in parts:
        if re.match(r"<h[23]>", seg or "", re.S):
            if cur_h is not None or buf:
                out.append((cur_h, "".join(buf)))
            cur_h, buf = seg, []
        else:
            buf.append(seg or "")
    out.append((cur_h, "".join(buf)))
    return out


def txt(html_frag):
    return H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html_frag))).strip()


def prose(heading_txt, inner):
    ps = [H.escape(x) for x in (txt(m.group(1)) for m in re.finditer(r"<p>(.*?)</p>", inner, re.S)) if len(x) > 2]
    if not ps:
        return ""
    return ('<div class="ds-prose"><h2 class="ds-h">' + H.escape(heading_txt) + '</h2>'
            + "".join('<p class="ds-lede">' + x + '</p>' for x in ps) + '</div>')


def render(kind, heading_txt, inner, img, alt, flip):
    lis = [H.escape(x) for x in
           (txt(m.group(1)) for m in re.finditer(r"<li>(.*?)</li>", inner, re.S)) if x]
    # keep document order: paragraphs written before the list stay above it
    cut = inner.find("<ul")
    before, after = (inner[:cut], inner[cut:]) if cut != -1 else (inner, "")
    def paras_in(frag):
        return [H.escape(x) for x in
                (txt(m.group(1)) for m in re.finditer(r"<p>(.*?)</p>", frag, re.S)) if len(x) > 2]
    lede = "".join(f'<p class="ds-lede">{x}</p>' for x in paras_in(before))
    tail = "".join(f'<p class="ds-lede">{x}</p>' for x in paras_in(after))
    head = f'<h2 class="ds-h">{H.escape(heading_txt)}</h2>'

    if kind == "cards":
        body = '<div class="ds-cards">' + "".join('<div class="ds-card">' + x + '</div>' for x in lis) + '</div>'
    elif kind == "checklist":
        body = '<ul class="ds-check">' + "".join('<li>' + x + '</li>' for x in lis) + '</ul>'
    elif kind == "grid":
        body = '<div class="ds-grid">' + "".join('<div class="ds-tile">' + x + '</div>' for x in lis) + '</div>'
    elif kind == "gallery":
        shots, rest = [], []
        for x in lis:
            key = next((k for k in STYLE_IMG if k in x.lower()), None)
            if key:
                shots.append(f'<div class="ds-galitem"><img src="{STYLE_IMG[key]}" alt="{x}" loading="lazy" '
                             f'decoding="async"><span>{x}</span></div>')
            else:
                rest.append(f'<div class="ds-tile">{x}</div>')
        # photos and text-only styles in one grid leaves ragged holes; keep them apart
        body = ('<div class="ds-gal">' + "".join(shots) + '</div>' if shots else "")
        if rest:
            body += '<div class="ds-grid ds-grid-tail">' + "".join(rest) + '</div>'
    elif kind == "chips":
        body = '<ul class="ds-chips">' + "".join('<li>' + x + '</li>' for x in lis) + '</ul>'
    else:
        return None

    content = head + lede + body + tail
    if img:
        shot = f'<div class="ds-shot"><img src="{img}" alt="{H.escape(alt)}" loading="lazy" decoding="async"></div>'
        cls = "ds-split flip" if flip else "ds-split"
        return f'<div class="{cls}">{shot}<div>{content}</div></div>'
    return f'<div class="ds-band">{content}</div>'


for slug, plan in PLAN.items():
    p = F / slug / "index.html"
    if not p.exists():
        continue
    h = orig = p.read_text("utf-8", errors="replace")
    h = re.sub(r'<style id="tmlsec-css">.*?</style>', "", h, flags=re.S)

    m = re.search(r'(<div class="rich-text w-richtext">)(.*?)(</div>)', h, re.S)
    if not m:
        continue
    rich = m.group(2)
    if 'class="ds-' in rich:            # already designed; rebuild from source is not possible
        n["skipped"] += 1
        continue

    h1 = txt(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1)) if re.search(r"<h1", h) else ""
    seen_titles = {h1.lower().rstrip(" ."), "garage door " + slug.replace("-", " ")}
    rebuilt, flip, changed = [], False, 0
    for head_html, inner in blocks_from(rich):
        if head_html is None:
            rebuilt.append(inner)
            continue
        htxt = txt(head_html)
        # a heading that just repeats the page H1 adds nothing above the hero
        if htxt.lower().rstrip(" .") in seen_titles:
            rebuilt.append(inner)
            continue
        seen_titles.add(htxt.lower().rstrip(" ."))
        key = next((k for k in plan if k in htxt.lower()), None)
        if key:
            kind, img, alt = plan[key]
        elif "<li>" in inner:
            kind, img, alt = "checklist", None, ""   # design every list, not just planned ones
        else:
            rebuilt.append(prose(htxt, inner))
            continue
        if kind == "skip":               # duplicated by the template's own panels
            n["dropped_dupes"] += 1
            continue
        out = render(kind, htxt, inner, img, alt, flip)
        if out:
            rebuilt.append(out)
            changed += 1
            if img:
                flip = not flip
        else:
            rebuilt.append(head_html + inner)

    if changed:
        h = h[:m.start(2)] + "".join(rebuilt) + h[m.end(2):]
        h = h.replace("</head>", CSS + "</head>", 1)
        h = h.replace('<div class="rich-text w-richtext">', '<div class="rich-text w-richtext ds">', 1)
        p.write_text(h, "utf-8")
        n["pages"] += 1
        n["sections"] += changed

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
