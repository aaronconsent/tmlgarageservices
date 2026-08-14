#!/usr/bin/env python3
"""Rebuild site/fixed/schedule-consult/ as a high-converting booking page
with a Workiz Online Booking slot.

The Workiz widget is config-driven (see TML_WORKIZ below): paste the account
token from Workiz → Online Booking → Get embed code and the iframe replaces
the fallback automatically. Until then the page books through TML's existing
Google Calendar link, so it converts today.

Re-runnable: rebuilds the page from the contact page's shell (nav + footer)
so it always matches the rest of the site. Run bake_reviews.py afterwards to
fill the review showcase marker.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"
SHELL_SRC = F / "contact" / "index.html"
DEST = F / "schedule-consult" / "index.html"

PHONE_DISPLAY = "(832) 887-8747"
PHONE_HREF = "tel:+18328878747"
SMS_HREF = "sms:+18328878747"
GCAL = "https://calendar.app.google/juqN1UNcknf4KZ9v9"
A = "/assets/66b2dae9e779df43d0d269c9"

TITLE = "Book Garage Door Service Online | TML Garage Services | Conroe, TX"
DESC = ("Book garage door repair, opener service, or a $69 tune-up online in under a minute. "
        "Same-day appointments across Conroe, The Woodlands, Spring and greater Houston. "
        "5.0 stars from 213 Google reviews. Call (832) 887-8747.")

shell = SHELL_SRC.read_text("utf-8", errors="replace")
head_end = shell.find("</head>")
body_open = shell.find("<body")
body_start = shell.find(">", body_open) + 1
first_section = shell.find('<section class="title-section">')
footer_at = shell.find('<section class="footer">')

HEAD = shell[:head_end]
PRE = shell[body_start:first_section]          # nav + menu markup
POST = shell[footer_at:]                        # footer + scripts + mobile drawer

# page-specific head: title, description, canonical-ish meta, FAQ schema
HEAD = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", HEAD, count=1, flags=re.S)
HEAD = re.sub(r'(<meta[^>]*name="description"[^>]*content=")[^"]*(")', f"\\g<1>{DESC}\\2", HEAD, count=1)

FAQ = [
    ("How fast can you get here?",
     "Same-day appointments are available most days, including weekends at no extra charge. "
     "If your door is stuck or a spring is broken, call (832) 887-8747 and we'll get you on the schedule right away."),
    ("What does a service call cost?",
     "Pricing is upfront — your technician gives you the full price before any work begins, so there are no surprises. "
     "A complete garage door tune-up and safety inspection is $69."),
    ("Do you charge extra for weekends?",
     "No. There are no extra charges for weekend appointments."),
    ("What happens after I book?",
     "You'll get a confirmation, then our team reaches out to lock in your arrival window. "
     "A trained, insured technician arrives, diagnoses the problem, and quotes the price before starting."),
    ("Do you offer financing?",
     "Yes. Renovate now, pay later — contact us for a soft-pull pre-approval, it only takes a few minutes."),
]
FAQ_SCHEMA = (
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage",'
    '"mainEntity":[' + ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (repr(q).replace("'", '"'), repr(a).replace("'", '"')) for q, a in FAQ) + "]}</script>")

SERVICE_SCHEMA = (
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Service",'
    '"serviceType":"Garage door repair and installation",'
    '"provider":{"@type":"LocalBusiness","name":"TML Garage Door Services","telephone":"+18328878747"},'
    '"areaServed":["Conroe TX","The Woodlands TX","Spring TX","Houston TX"],'
    '"hasOfferCatalog":{"@type":"OfferCatalog","name":"Garage door services","itemListElement":['
    '{"@type":"Offer","itemOffered":{"@type":"Service","name":"Garage door tune-up and safety inspection"},"price":"69","priceCurrency":"USD"}]}}</script>')

STYLE = """<style id="tmlbook-css">
.tb{--g:#587735;--gd:#3f5a22;--ink:#1f2418;--mut:#5c6553;--line:#e2e5d9;}
.tb *{box-sizing:border-box;}
.tb-hero{background:#587735;color:#fff;padding:44px 0 40px;}
.tb-wrap{width:min(100% - 36px,1180px);margin:0 auto;}
.tb-hero h1{font-size:clamp(30px,5vw,50px);line-height:1.05;margin:0 0 14px;max-width:20ch;}
.tb-hero p.lede{font-size:clamp(16px,2vw,19px);line-height:1.5;max-width:56ch;margin:0 0 22px;color:#eef3e6;}
.tb-trust{display:flex;flex-wrap:wrap;gap:10px 26px;padding:0;margin:0;list-style:none;}
.tb-trust li{display:flex;align-items:center;gap:8px;font-weight:600;font-size:15px;}
.tb-trust li::before{content:"✓";display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#cfe84d;color:#1f2418;font-size:13px;font-weight:800;}
.tb-hero-stars{color:#ffd35c;letter-spacing:2px;}
.tb-main{padding:38px 0 10px;}
.tb-grid{display:grid;gap:24px;}
.tb-panel{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 18px 40px -26px rgba(20,27,13,.5);overflow:hidden;}
.tb-panel-head{padding:20px 22px 0;}
.tb-panel-head h2{font-size:clamp(21px,3vw,27px);margin:0 0 6px;color:var(--ink);}
.tb-panel-head p{margin:0;color:var(--mut);font-size:15px;}
.tb-slot{padding:14px 14px 18px;}
.tb-slot[data-workiz=live]{min-height:720px;}
.tb-slot iframe{width:100%;border:0;display:block;border-radius:10px;min-height:720px;}
.tb-fallback{padding:6px 8px 10px;}
.tb-fallback .row{display:grid;gap:10px;}
.tb-btn{display:flex;align-items:center;justify-content:center;gap:9px;min-height:56px;border-radius:12px;padding:0 22px;white-space:nowrap;
 font-weight:800;font-size:17px;text-decoration:none;letter-spacing:.01em;transition:transform .14s ease;}
.tb-btn:active{transform:scale(.98);}
.tb-btn.p{background:var(--g);color:#fff;box-shadow:0 10px 22px -12px rgba(46,63,23,.8);}
.tb-btn.p:hover{background:var(--gd);color:#fff;}
.tb-btn.s{background:#fff;color:var(--ink);border:2px solid var(--ink);}
.tb-btn.s:hover{background:var(--ink);color:#fff;}
.tb-note{margin:12px 2px 0;font-size:13.5px;color:var(--mut);line-height:1.5;}
.tb-side{display:grid;gap:16px;align-content:start;}
.tb-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 18px 20px;}
.tb-card.dark{background:#1f2418;border-color:#1f2418;color:#fff;}
.tb-card h3{margin:0 0 8px;font-size:19px;color:inherit;}
.tb-card p{margin:6px 0;color:var(--mut);font-size:14.5px;line-height:1.55;}
.tb-card.dark p{color:#cfd6c4;}
.tb-phone{display:inline-block;font-size:30px;font-weight:800;letter-spacing:-.5px;color:#fff;text-decoration:none;line-height:1.1;margin:2px 0 4px;}
.tb-phone:hover{color:#cfe84d;}
.tb-mini{display:grid;gap:8px;margin:12px 0 0;padding:0;list-style:none;}
.tb-mini li{display:flex;gap:9px;align-items:flex-start;font-size:14.5px;color:var(--mut);}
.tb-mini li::before{content:"✓";color:var(--g);font-weight:800;}
.tb-card.dark .tb-mini li{color:#cfd6c4;}
.tb-card.dark .tb-mini li::before{color:#cfe84d;}
.tb-price{display:inline-flex;align-items:baseline;gap:8px;background:#f3f6ec;border:1px dashed #9fb277;border-radius:10px;padding:10px 14px;margin-top:6px;}
.tb-price b{font-size:26px;color:var(--ink);}
.tb-price span{font-size:14px;color:var(--mut);}
.tb-steps{padding:34px 0 6px;}
.tb-steps h2{text-align:center;font-size:clamp(22px,3.4vw,30px);margin:0 0 22px;color:var(--ink);}
.tb-steplist{display:grid;gap:16px;counter-reset:s;}
.tb-step{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 18px 18px 62px;position:relative;}
.tb-step::before{counter-increment:s;content:counter(s);position:absolute;left:16px;top:16px;width:32px;height:32px;
 border-radius:50%;background:var(--g);color:#fff;display:grid;place-items:center;font-weight:800;font-size:15px;}
.tb-step b{display:block;font-size:17px;color:var(--ink);margin-bottom:4px;}
.tb-step span{color:var(--mut);font-size:14.5px;line-height:1.55;}
.tb-faq{padding:34px 0 40px;}
.tb-faq h2{text-align:center;font-size:clamp(22px,3.4vw,30px);margin:0 0 20px;color:var(--ink);}
.tb-faq details{background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:10px;overflow:hidden;}
.tb-faq summary{cursor:pointer;list-style:none;padding:16px 18px;font-weight:700;font-size:16px;color:var(--ink);
 display:flex;justify-content:space-between;gap:14px;align-items:center;}
.tb-faq summary::-webkit-details-marker{display:none;}
.tb-faq summary::after{content:"+";font-size:22px;color:var(--g);line-height:1;transition:transform .2s ease;}
.tb-faq details[open] summary::after{transform:rotate(45deg);}
.tb-faq p{margin:0;padding:0 18px 16px;color:var(--mut);font-size:15px;line-height:1.6;}
.tb-final{background:#1f2418;color:#fff;padding:34px 0;}
.tb-final .in{display:grid;gap:16px;align-items:center;}
.tb-final h2{margin:0;font-size:clamp(22px,3.4vw,30px);}
.tb-final p{margin:6px 0 0;color:#cfd6c4;font-size:15.5px;}
.tb-final .acts{display:grid;gap:10px;}
@media(min-width:860px){
 .tb-grid{grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);align-items:start;}
 .tb-side{position:sticky;top:100px;}
 .tb-steplist{grid-template-columns:repeat(3,1fr);}
 .tb-fallback .row{grid-template-columns:1fr 1fr;}
 .tb-final .in{grid-template-columns:1fr auto;}
 .tb-final .acts{grid-auto-flow:column;}
 .tb-faq .inner{max-width:820px;margin:0 auto;}
}
@media(prefers-reduced-motion:reduce){.tb-btn{transition:none;}}
</style>"""

SCRIPT = """<script id="tmlbook-js">
/* ── Workiz Online Booking ─────────────────────────────────────────────
   To go live: paste the account token from
   Workiz → Online Booking → Get embed code  (the ac=... value)
   into `account` below. Everything else is automatic. Leave it empty and
   the page falls back to the Google Calendar booking link + call/text.   */
window.TML_WORKIZ = {
  account: "",                                   // e.g. "5680b25d9dff9abc..."
  base: "https://online-booking.workiz.com/",
  height: 760,                                   // px; widget scrolls internally
  adGroupParam: "ad_group"                       // Workiz ad-source tracking
};
(function () {
  var cfg = window.TML_WORKIZ || {};
  var slot = document.getElementById("tmlbook-slot");
  if (!slot) return;
  var override = new URLSearchParams(location.search).get("workiz");  // ?workiz=TOKEN to preview
  var account = override || cfg.account;
  if (!account) return;                          // keep the fallback panel

  /* attribution: carry the visitor's campaign into the booking record */
  var q = new URLSearchParams(location.search);
  var src = q.get("utm_source") || q.get("utm_medium") || (q.get("gclid") ? "google-ads" : "") ||
            (document.referrer && document.referrer.indexOf(location.hostname) === -1
              ? (document.referrer.split("/")[2] || "referral") : "website");
  var camp = q.get("utm_campaign");
  var adGroup = camp ? src + "|" + camp : src;

  var url = cfg.base + "?ac=" + encodeURIComponent(account) +
            "&" + (cfg.adGroupParam || "ad_group") + "=" + encodeURIComponent(adGroup);

  var f = document.createElement("iframe");
  f.src = url;
  f.title = "Book garage door service";
  f.loading = "lazy";
  f.style.minHeight = (cfg.height || 760) + "px";
  f.setAttribute("allow", "payment");
  slot.innerHTML = "";
  slot.appendChild(f);
  slot.setAttribute("data-workiz", "live");
  if (window.dataLayer) window.dataLayer.push({ event: "booking_widget_loaded", ad_group: adGroup });
})();
/* booking-intent tracking for GTM */
document.addEventListener("click", function (e) {
  var a = e.target.closest("[data-book]");
  if (a && window.dataLayer) window.dataLayer.push({ event: "book_click", method: a.getAttribute("data-book") });
});
</script>"""

def faq_html():
    return "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)

BODY = f"""
<div class="tb">
<section class="tb-hero">
  <div class="tb-wrap">
    <h1>Book your garage door service online</h1>
    <p class="lede">Pick a time that works for you — most jobs are booked same-day, including weekends at no extra charge.
    A trained, insured technician arrives and quotes the full price before any work starts.</p>
    <ul class="tb-trust">
      <li><span class="tb-hero-stars">★★★★★</span>&nbsp;5.0 from 213 Google reviews</li>
      <li>Same-day appointments</li>
      <li>No weekend surcharge</li>
      <li>Upfront pricing</li>
    </ul>
  </div>
</section>

<section class="tb-main">
  <div class="tb-wrap tb-grid">
    <div class="tb-panel">
      <div class="tb-panel-head">
        <h2>Schedule your appointment</h2>
        <p>Takes about a minute. You'll get a confirmation right away.</p>
      </div>
      <div class="tb-slot" id="tmlbook-slot">
        <div class="tb-fallback">
          <div class="row">
            <a class="tb-btn p" href="{GCAL}" target="_blank" rel="noopener" data-book="calendar">📅 Pick a time now</a>
            <a class="tb-btn s" href="{PHONE_HREF}" data-book="call">📞 Call {PHONE_DISPLAY}</a>
          </div>
          <p class="tb-note">Prefer to text? <a href="{SMS_HREF}" data-book="text">Send us a text</a> and we'll get you scheduled.
          Broken spring or a door that won't open? Call — we keep same-day slots open for emergencies.</p>
        </div>
      </div>
    </div>

    <aside class="tb-side">
      <div class="tb-card dark">
        <h3>Need it today?</h3>
        <a class="tb-phone" href="{PHONE_HREF}" data-book="call">{PHONE_DISPLAY}</a>
        <p>The owner or a live in-house rep answers every call — no phone tree, no dispatch service.</p>
        <ul class="tb-mini">
          <li>Same-day &amp; emergency service</li>
          <li>Well-trained, insured technicians</li>
          <li>100% satisfaction guaranteed</li>
        </ul>
      </div>
      <div class="tb-card">
        <h3>Garage door tune-up</h3>
        <div class="tb-price"><b>$69</b><span>complete tune-up &amp; safety inspection</span></div>
        <ul class="tb-mini">
          <li>Full inspection of the door system</li>
          <li>Spring balancing &amp; tension adjustment</li>
          <li>Roller, cable, track &amp; hinge inspection</li>
          <li>Lubrication and safety test</li>
        </ul>
      </div>
      <div class="tb-card">
        <h3>Financing available</h3>
        <p>Renovate now, pay later. Contact us for your soft-pull pre-approval — it only takes a few minutes.</p>
      </div>
    </aside>
  </div>
</section>

<section class="tb-steps">
  <div class="tb-wrap">
    <h2>What happens after you book</h2>
    <div class="tb-steplist">
      <div class="tb-step"><b>Pick your time</b><span>Choose the appointment window that fits your schedule — weekends included, at no extra charge.</span></div>
      <div class="tb-step"><b>We confirm</b><span>Our team reaches out to lock in your arrival window and answer any questions before we head out.</span></div>
      <div class="tb-step"><b>We fix it right</b><span>Your technician diagnoses the problem and gives you the full price before starting. No surprises.</span></div>
    </div>
  </div>
</section>

<section class="tb-steps" style="padding-top:14px;">
  <div class="tb-wrap">
    <!--tmlrev--><!--/tmlrev-->
  </div>
</section>

<section class="tb-faq">
  <div class="tb-wrap inner">
    <h2>Booking questions</h2>
    {faq_html()}
  </div>
</section>

<section class="tb-final">
  <div class="tb-wrap in">
    <div>
      <h2>Rather just talk to someone?</h2>
      <p>Call or text {PHONE_DISPLAY} — a real person picks up.</p>
    </div>
    <div class="acts">
      <a class="tb-btn p" href="{PHONE_HREF}" data-book="call">📞 Call now</a>
      <a class="tb-btn s" href="{SMS_HREF}" data-book="text" style="background:#fff;">💬 Send us a text</a>
    </div>
  </div>
</section>
</div>
"""

html = HEAD + STYLE + FAQ_SCHEMA + SERVICE_SCHEMA + "</head><body>" + PRE + BODY + POST
html = html.replace("</body>", SCRIPT + "</body>", 1)
DEST.write_text(html, "utf-8")
print(f"rebuilt {DEST.relative_to(ROOT)} ({len(html):,} bytes)")
print("Workiz slot: paste the ac= token into TML_WORKIZ.account (or preview with ?workiz=TOKEN)")
