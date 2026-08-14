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
.tb-hero{position:relative;color:#fff;padding:60px 0 56px;background:#3f5a22 url('/assets/66b2dae9e779df43d0d269c9/66b5115cc6a1fdc1f8b546d6_modern-garage-door-services.jpg') center/cover no-repeat;}
.tb-hero::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,.25) 55%,rgba(0,0,0,.1) 100%);}
.tb-hero .tb-wrap{position:relative;}
.tb-hero-box{background:rgba(0,0,0,.55);border-radius:10px;padding:24px 24px 22px;max-width:660px;}
.tb-wrap{width:min(100% - 36px,1180px);margin:0 auto;}
.tb-hero h1{font-size:clamp(30px,5vw,50px);line-height:1.05;margin:0 0 14px;max-width:20ch;color:#fff!important;}
.tb-hero p.lede{font-size:clamp(16px,2vw,19px);line-height:1.5;max-width:56ch;margin:0 0 20px;color:#eef3e6;}
.tb-trust{display:flex;flex-wrap:wrap;gap:10px 26px;padding:0;margin:0;list-style:none;}
.tb-trust li{display:flex;align-items:center;gap:8px;font-weight:600;font-size:15px;color:#fff;white-space:nowrap;}
.tb-trust li::before{content:"✓";display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#587735;color:#fff;font-size:13px;font-weight:800;}
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
/* ── native booking picker (prototype) ─────────────────────────── */
.bk{padding:4px 6px 8px;}
.bk-demo{margin:0 0 14px;background:#fff8e1;border:1px dashed #d9b23a;color:#6b5310;
 border-radius:8px;padding:8px 12px;font-size:13px;font-weight:600;}
.bk-step{margin-bottom:18px;}
.bk-q{display:block;font-weight:800;font-size:15.5px;color:var(--ink);margin:0 0 9px;}
.bk-chips{display:flex;flex-wrap:wrap;gap:8px;}
.bk-chip{font:inherit;font-size:14.5px;font-weight:600;color:var(--ink);background:#fff;
 border:1.5px solid var(--line);border-radius:999px;padding:10px 15px;cursor:pointer;
 transition:background .14s ease,border-color .14s ease,color .14s ease,transform .12s ease;}
.bk-chip:hover{border-color:var(--g);}
.bk-chip:active{transform:scale(.97);}
.bk-chip.on{background:var(--g);border-color:var(--g);color:#fff;}
.bk-urgent[hidden],.bk-done[hidden],#bk-form[hidden]{display:none!important;}
.bk-urgent{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;background:#fdeceb;
 border:1px solid #f0b7b2;border-radius:10px;padding:11px 14px;margin:0 0 18px;font-size:14.5px;color:#8c2f27;}
.bk-urgent a{color:#8c2f27;font-weight:800;text-decoration:underline;}
.bk-days{display:flex;gap:8px;overflow-x:auto;padding:2px 2px 8px;margin:0 -2px 10px;scrollbar-width:none;}
.bk-days::-webkit-scrollbar{display:none;}
.bk-day{flex:0 0 auto;min-width:78px;font:inherit;background:#fff;border:1.5px solid var(--line);
 border-radius:12px;padding:9px 8px;cursor:pointer;text-align:center;line-height:1.25;
 transition:border-color .14s ease,background .14s ease,transform .12s ease;}
.bk-day:hover{border-color:var(--g);}
.bk-day:active{transform:scale(.97);}
.bk-day span{display:block;font-size:12px;color:var(--mut);font-weight:600;text-transform:uppercase;letter-spacing:.04em;}
.bk-day b{display:block;font-size:17px;color:var(--ink);}
.bk-day.on{background:var(--g);border-color:var(--g);}
.bk-day.on span,.bk-day.on b{color:#fff;}
.bk-windows{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.bk-win{font:inherit;background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:11px 6px;
 cursor:pointer;text-align:center;transition:border-color .14s ease,background .14s ease,transform .12s ease;}
.bk-win:hover{border-color:var(--g);}
.bk-win:active{transform:scale(.97);}
.bk-win b{display:block;font-size:14.5px;color:var(--ink);}
.bk-win span{display:block;font-size:12px;color:var(--mut);margin-top:2px;}
.bk-win.on{background:var(--g);border-color:var(--g);}
.bk-win.on b,.bk-win.on span{color:#fff;}
.bk-fields{display:grid;gap:10px;}
.bk-in{font:inherit;font-size:16px;padding:13px 14px;border:1.5px solid var(--line);border-radius:10px;
 background:#fff;color:var(--ink);width:100%;}
.bk-in:focus{outline:none;border-color:var(--g);box-shadow:0 0 0 3px rgba(88,119,53,.18);}
.bk-in.bad{border-color:#c0392b;background:#fdf3f2;}
.bk-hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0;}
.bk-err{margin:0 0 10px;color:#c0392b;font-size:14px;font-weight:600;}
.bk-submit{width:100%;margin-top:4px;}
.bk-submit[disabled]{opacity:.65;cursor:progress;}
.bk-done{padding:10px 6px 8px;text-align:center;}
.bk-check{width:56px;height:56px;border-radius:50%;background:var(--g);color:#fff;font-size:30px;
 display:grid;place-items:center;margin:6px auto 12px;}
.bk-done h3{margin:0 0 6px;font-size:23px;color:var(--ink);}
.bk-ref{margin:0 0 14px;color:var(--mut);font-size:14.5px;}
.bk-ref b{color:var(--ink);letter-spacing:.06em;}
.bk-summary{display:grid;gap:6px;text-align:left;background:#f6f8f1;border:1px solid var(--line);
 border-radius:12px;padding:14px 16px;margin:0 0 14px;font-size:14.5px;color:var(--ink);}
.bk-summary div{display:flex;justify-content:space-between;gap:14px;}
.bk-summary span{color:var(--mut);}
.bk-next{margin:0 0 14px;color:var(--mut);font-size:14.5px;line-height:1.55;}
.bk-payload{text-align:left;margin:0 0 14px;}
.bk-payload summary{cursor:pointer;font-size:13px;color:var(--mut);font-weight:600;}
.bk-payload pre{background:#1f2418;color:#cfe0b8;border-radius:10px;padding:12px;overflow-x:auto;
 font-size:12px;line-height:1.5;margin:8px 0 0;}
@media(min-width:620px){.bk-fields{grid-template-columns:1fr 1fr;}.bk-in.wide{grid-column:1/-1;}}
@media(max-width:600px){.tb-hero{padding:34px 0 32px;}.tb-hero-box{padding:18px 16px;}}
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

/* ── native booking picker — PROTOTYPE ───────────────────────────────────
   Everything below is UX only: no request is sent. When the Workiz API
   token is in place, `submitBooking()` POSTs this same payload to
   /api/book (see WORKIZ-BOOKING-DESIGN.md) instead of faking the delay. */
(function () {
  var form = document.getElementById("bk-form");
  if (!form) return;
  var state = { issue: "", day: null, win: null, range: "" };

  /* day strip: today + next 6 days */
  var DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var daysEl = document.getElementById("bk-days");
  var today = new Date();
  for (var i = 0; i < 7; i++) {
    var d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i);
    var b = document.createElement("button");
    b.type = "button";
    b.className = "bk-day";
    b.dataset.iso = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    b.dataset.label = (i === 0 ? "Today" : i === 1 ? "Tomorrow" : DOW[d.getDay()] + " " + MON[d.getMonth()] + " " + d.getDate());
    b.innerHTML = "<span>" + (i === 0 ? "Today" : i === 1 ? "Tomorrow" : DOW[d.getDay()]) + "</span><b>" +
                  (i < 2 ? MON[d.getMonth()] + " " + d.getDate() : d.getDate()) + "</b>";
    daysEl.appendChild(b);
  }

  function pick(container, el, key, extra) {
    [].forEach.call(container.children, function (c) { c.classList.remove("on"); });
    el.classList.add("on");
    state[key] = el.dataset[extra || key] || el.textContent.trim();
  }

  document.getElementById("bk-issues").addEventListener("click", function (e) {
    var b = e.target.closest(".bk-chip"); if (!b) return;
    pick(this, b, "issue", "issue");
    var urgent = state.issue === "Broken spring" || state.issue === "Door won't open" || state.issue === "Off track";
    document.getElementById("bk-urgent").hidden = !urgent;
  });
  daysEl.addEventListener("click", function (e) {
    var b = e.target.closest(".bk-day"); if (!b) return;
    pick(this, b, "day", "iso");
    state.dayLabel = b.dataset.label;
  });
  document.getElementById("bk-windows").addEventListener("click", function (e) {
    var b = e.target.closest(".bk-win"); if (!b) return;
    pick(this, b, "win", "win");
    state.range = b.dataset.range;
  });

  /* light phone formatting as they type */
  var phone = document.getElementById("bk-phone");
  phone.addEventListener("input", function () {
    var v = this.value.replace(/\\D/g, "").slice(0, 10);
    this.value = v.length > 6 ? "(" + v.slice(0, 3) + ") " + v.slice(3, 6) + "-" + v.slice(6)
               : v.length > 3 ? "(" + v.slice(0, 3) + ") " + v.slice(3) : v;
  });

  function fail(msg, el) {
    var e = document.getElementById("bk-err");
    e.textContent = msg; e.hidden = false;
    if (el) { el.classList.add("bad"); el.focus(); }
    return false;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    document.getElementById("bk-err").hidden = true;
    [].forEach.call(form.querySelectorAll(".bk-in"), function (i) { i.classList.remove("bad"); });
    if (form.company_website.value) return;                       /* honeypot */
    var name = document.getElementById("bk-name"),
        addr = document.getElementById("bk-addr"),
        notes = document.getElementById("bk-notes");
    if (!state.issue) return fail("Pick what's going on so we send the right technician.");
    if (!state.day) return fail("Choose a day that works for you.");
    if (!state.win) return fail("Choose an arrival window.");
    if (!name.value.trim()) return fail("We need a name for the appointment.", name);
    if (phone.value.replace(/\\D/g, "").length !== 10) return fail("Enter a 10-digit mobile number so we can text your confirmation.", phone);
    if (addr.value.trim().length < 6) return fail("Enter the service address.", addr);

    var q = new URLSearchParams(location.search);
    var payload = {
      JobDateTime: state.day + "T" + state.range.split("–")[0].padStart(5, "0") + ":00",
      JobEndDateTime: state.day + "T" + state.range.split("–")[1].padStart(5, "0") + ":00",
      FirstName: name.value.trim().split(" ")[0],
      LastName: name.value.trim().split(" ").slice(1).join(" "),
      Phone: "+1" + phone.value.replace(/\\D/g, ""),
      Address: addr.value.trim(),
      City: "", State: "TX", Country: "US", PostalCode: "",
      JobType: state.issue,
      JobNotes: notes.value.trim(),
      JobSource: q.get("utm_source") || (q.get("gclid") ? "google-ads" : "website"),
      Campaign: q.get("utm_campaign") || ""
    };

    var btn = document.getElementById("bk-submit");
    btn.disabled = true; btn.textContent = "Sending…";
    setTimeout(function () {                                       /* mock latency */
      var ref = "TML-" + Math.random().toString(36).slice(2, 7).toUpperCase();
      document.getElementById("bk-ref").textContent = ref;
      document.getElementById("bk-summary").innerHTML =
        "<div><span>Service</span><b>" + state.issue + "</b></div>" +
        "<div><span>When</span><b>" + state.dayLabel + ", " + state.win + " (" + state.range.replace("–", "–") + ")</b></div>" +
        "<div><span>Where</span><b>" + addr.value.trim() + "</b></div>" +
        "<div><span>Contact</span><b>" + name.value.trim() + " · " + phone.value + "</b></div>";
      document.getElementById("bk-json").textContent = JSON.stringify(payload, null, 2);
      form.hidden = true;
      document.getElementById("bk-done").hidden = false;
      document.getElementById("bk-done").scrollIntoView({ block: "center", behavior: "smooth" });
      btn.disabled = false; btn.textContent = "Request this time";
      if (window.dataLayer) window.dataLayer.push({ event: "booking_submitted_demo", job_type: state.issue });
    }, 700);
  });

  document.getElementById("bk-again").addEventListener("click", function () {
    document.getElementById("bk-done").hidden = true;
    form.hidden = false;
    form.scrollIntoView({ block: "center", behavior: "smooth" });
  });
})();
</script>"""

def faq_html():
    return "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)

BODY = f"""
<div class="tb">
<section class="tb-hero">
  <div class="tb-wrap">
    <div class="tb-hero-box">
    <h1>Book online now</h1>
    <p class="lede">Pick a time that works for you — most jobs are booked same-day, including weekends at no extra charge.
    A trained, insured technician arrives and quotes the full price before any work starts.</p>
    <ul class="tb-trust">
      <li><span class="tb-hero-stars">★★★★★</span>&nbsp;5.0 from 213 Google reviews</li>
      <li>Same-day appointments</li>
      <li>Upfront pricing</li>
    </ul>
    </div>
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
        <form class="bk" id="bk-form" novalidate>
          <p class="bk-demo">Prototype — nothing is booked yet. This is the flow that will push to Workiz.</p>

          <div class="bk-step">
            <label class="bk-q">1. What's going on?</label>
            <div class="bk-chips" id="bk-issues" role="radiogroup" aria-label="Problem type">
              <button type="button" class="bk-chip" data-issue="Broken spring">Broken spring</button>
              <button type="button" class="bk-chip" data-issue="Door won't open">Door won't open</button>
              <button type="button" class="bk-chip" data-issue="Opener trouble">Opener trouble</button>
              <button type="button" class="bk-chip" data-issue="Off track">Off track</button>
              <button type="button" class="bk-chip" data-issue="New door quote">New door</button>
              <button type="button" class="bk-chip" data-issue="Tune-up">Tune-up</button>
              <button type="button" class="bk-chip" data-issue="Something else">Something else</button>
            </div>
          </div>

          <div class="bk-urgent" id="bk-urgent" hidden>
            <b>Door stuck right now?</b> A call gets a technician moving faster than a form.
            <a href="{PHONE_HREF}" data-book="call">Call {PHONE_DISPLAY} →</a>
          </div>

          <div class="bk-step">
            <label class="bk-q">2. Which day works?</label>
            <div class="bk-days" id="bk-days" role="radiogroup" aria-label="Day"></div>
            <div class="bk-windows" id="bk-windows" role="radiogroup" aria-label="Arrival window">
              <button type="button" class="bk-win" data-win="Morning" data-range="8:00–12:00"><b>Morning</b><span>8am – 12pm</span></button>
              <button type="button" class="bk-win" data-win="Afternoon" data-range="12:00–16:00"><b>Afternoon</b><span>12pm – 4pm</span></button>
              <button type="button" class="bk-win" data-win="Evening" data-range="16:00–19:00"><b>Evening</b><span>4pm – 7pm</span></button>
            </div>
          </div>

          <div class="bk-step">
            <label class="bk-q">3. Where should we come?</label>
            <div class="bk-fields">
              <input class="bk-in" id="bk-name" name="name" placeholder="Your name" autocomplete="name" required>
              <input class="bk-in" id="bk-phone" name="phone" type="tel" placeholder="Mobile number" autocomplete="tel" inputmode="tel" required>
              <input class="bk-in wide" id="bk-addr" name="address" placeholder="Service address" autocomplete="street-address" required>
              <input class="bk-in wide" id="bk-notes" name="notes" placeholder="Anything we should know? (optional)">
              <input class="bk-hp" name="company_website" tabindex="-1" autocomplete="off" aria-hidden="true">
            </div>
          </div>

          <p class="bk-err" id="bk-err" hidden></p>
          <button class="tb-btn p bk-submit" id="bk-submit" type="submit">Request this time</button>
          <p class="tb-note">We'll text to confirm your arrival window — usually within the hour during business hours.
          Prefer to talk? <a href="{PHONE_HREF}" data-book="call">Call {PHONE_DISPLAY}</a> or
          <a href="{SMS_HREF}" data-book="text">send a text</a>.</p>
        </form>

        <div class="bk-done" id="bk-done" hidden>
          <div class="bk-check" aria-hidden="true">✓</div>
          <h3>You're on the schedule</h3>
          <p class="bk-ref">Reference <b id="bk-ref"></b></p>
          <div class="bk-summary" id="bk-summary"></div>
          <p class="bk-next">A TML dispatcher will text you shortly to confirm the exact arrival time.
          Need it sooner? <a href="{PHONE_HREF}" data-book="call">Call {PHONE_DISPLAY}</a>.</p>
          <details class="bk-payload"><summary>Developer preview: what gets sent to Workiz</summary><pre id="bk-json"></pre></details>
          <button class="tb-btn s" type="button" id="bk-again">Book another time</button>
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
    </aside>
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
