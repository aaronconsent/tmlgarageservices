#!/usr/bin/env python3
"""Replace the dead Webflow contact form with the appointment booking flow.

The form on six pages had no action and method="get". On the real Webflow site
its script posts to Webflow's servers; on this exported copy those servers are
not there, so every "REQUEST APPOINTMENT" went nowhere — no email, no record,
and no error shown to the visitor. It has been silently losing leads.

It is replaced by a panel pointing at the booking page, which is the flow that
actually captures a job (problem, day, time window, contact details), plus the
two things a customer in a hurry wants anyway: call and text. That also removes
the last thing on the site depending on the Webflow bundle.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

PHONE, PHONE_HREF, SMS_HREF = "(832) 887-8747", "tel:+18328878747", "sms:+18328878747"
BOOK = "/fixed/schedule-consult"

CSS = """<style id="tmlbook-css">
.tmlbook{background:#f5f7ef;border:1px solid #dfe3d5;border-radius:16px;
 padding:clamp(22px,3.4vw,32px);max-width:620px;}
.tmlbook h3{margin:0 0 10px;font-size:clamp(20px,2.6vw,26px);line-height:1.15;color:#1f2418;}
.tmlbook p{margin:0 0 20px;font-size:16.5px;line-height:1.6;color:#535c48;max-width:52ch;}
.tmlbook-acts{display:flex;flex-wrap:wrap;gap:11px;}
.tmlbook-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;
 padding:0 24px;border-radius:11px;font-weight:800;font-size:16.5px;text-decoration:none;
 white-space:nowrap;transition:background .14s ease,color .14s ease,border-color .14s ease;}
.tmlbook-btn.go{background:#587735;color:#fff;}
.tmlbook-btn.go:hover{background:#3f5a22;color:#fff;}
.tmlbook-btn.alt{background:#fff;color:#1f2418;border:2px solid #1f2418;}
.tmlbook-btn.alt:hover{background:#1f2418;color:#fff;}
.tmlbook-btn:focus-visible{outline:2px solid #587735;outline-offset:2px;}
.tmlbook-note{margin:16px 0 0;font-size:14.5px;color:#5c6553;}
@media(prefers-reduced-motion:reduce){.tmlbook-btn{transition:none;}}
</style>"""

PANEL = (
    '<div class="tmlbook">'
    "<h3>Book your appointment</h3>"
    "<p>Tell us what the door is doing and pick a time that works. Same-day and "
    "weekend appointments are available at no extra charge.</p>"
    '<div class="tmlbook-acts">'
    f'<a class="tmlbook-btn go" href="{BOOK}" data-book="form-replacement">Book online</a>'
    f'<a class="tmlbook-btn alt" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
    f'<a class="tmlbook-btn alt" href="{SMS_HREF}" data-book="text">&#128172; Text us</a>'
    "</div>"
    '<p class="tmlbook-note">A real person answers — no phone tree, no dispatch service.</p>'
    "</div>")


def convert(html):
    """Swap the <form> (and the Webflow wrapper holding its success/error blocks)."""
    i = html.find('<form')
    if i == -1:
        return html, 0
    # the wrapper carries w-form plus the done/fail messages; replace the whole thing
    start = html.rfind("<div", 0, i)
    m = re.match(r"<div[^>]*>", html[start:])
    if not m or "w-form" not in m.group(0):
        start, m = i, re.match(r"<form[^>]*>", html[i:])
        if not m:
            return html, 0
        end = html.find("</form>", i)
        if end == -1:
            return html, 0
        return html[:start] + PANEL + html[end + len("</form>"):], 1

    depth, pos = 1, start + m.end()
    for t in re.finditer(r"<div\b|</div>", html[pos:]):
        depth += 1 if t.group(0) == "<div" else -1
        if depth == 0:
            end = pos + t.end()
            break
    else:
        return html, 0
    return html[:start] + PANEL + html[end:], 1


def main():
    pages = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "w-form" not in html or "tmlbook" in html:
            continue
        html, n = convert(html)
        if not n:
            continue
        html = re.sub(r'<style id="tmlbook-css">.*?</style>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            print(f"  {f.relative_to(F)}: dead form -> booking panel")
    print(f"pages changed: {pages}")


if __name__ == "__main__":
    main()
