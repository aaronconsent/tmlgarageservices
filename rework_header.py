#!/usr/bin/env python3
"""Header rework across site/fixed/ (desktop nav + mobile menu + footer).

- nav order: Home · Services · Brands · About
- Service Areas dropdown removed from the header, added to the footer
- "Schedule Service" nav item removed
- right side: phone button + Book Now button (-> /fixed/schedule-consult/)
Idempotent: safe to re-run.
"""
import re
from pathlib import Path
from collections import Counter

F = Path(__file__).parent / "site" / "fixed"
n = Counter()

PHONE_HREF = "tel:+18328878747"
PHONE_DISPLAY = "(832) 887-8747"
BOOK_URL = "/fixed/schedule-consult"

NAV_ITEM = re.compile(
    r'<div[^>]*class="nav-links"[^>]*>\s*<a href="(?P<href>[^"]+)"[^>]*class="nav-link[^"]*"[^>]*>(?P<label>[^<]*)</a>\s*<div class="nav-line"></div>\s*</div>',
    re.I)
DROPDOWN = re.compile(
    r'<div data-hover="true"[^>]*class="w-dropdown">\s*<div class="dropdown-toggle w-dropdown-toggle">.*?<div class="nav-link">(?P<label>[^<]*)</div>\s*</div>.*?</nav>\s*</div>',
    re.S | re.I)

RIGHT_HTML = (
    '<div class="nav-right">'
    f'<a href="{PHONE_HREF}" class="nav-btn w-button hdr-call" data-book="call">'
    f'<span class="hdr-ico" aria-hidden="true">&#9742;</span>{PHONE_DISPLAY}</a>'
    f'<a href="{BOOK_URL}" class="nav-btn w-button hdr-book" data-book="header">Book Now</a>'
    "</div>")

NAV_CSS_MOBILE = (
    "@media(max-width:991px){"
    ".nav-menu{display:none!important;}"
    ".tmlnav-open .nav-menu{display:block!important;position:absolute!important;top:100%!important;"
    "left:0!important;right:0!important;height:auto!important;max-height:calc(100vh - 76px);overflow-y:auto;"
    "transform:none!important;background:#fff;padding:10px 18px 20px;"
    "box-shadow:0 18px 40px -18px rgba(20,27,13,.45);border-top:1px solid #e2e5d9;z-index:9990;}"
    ".tmlnav-open .nav-inner{display:block!important;}"
    ".tmlnav-open .nav-links{display:block!important;padding:2px 0;}"
    ".tmlnav-open .nav-link{display:block!important;padding:11px 0!important;font-size:17px!important;text-align:left!important;}"".tmlnav-open .nav-links{text-align:left!important;}"".tmlnav-open .dropdown-toggle{justify-content:flex-start!important;text-align:left!important;}"
    ".tmlnav-open .w-dropdown{display:block!important;width:100%;}"
    ".tmlnav-open .dropdown-list{position:static!important;display:block!important;background:transparent!important;"
    "box-shadow:none!important;padding:0 0 0 14px!important;}"
    ".tmlnav-open .dropdown-toggle{padding:11px 0!important;}"
    ".tmlnav-open .nav-line{display:none!important;}"
    "}")

HDR_CSS = (
    '<style id="tmlhdr-css">'
    '.nav-right{display:flex;align-items:center;gap:10px;}'
    '.nav-right .hdr-call{background:#fff!important;color:#1f2418!important;border:2px solid #1f2418!important;'
    'display:inline-flex;align-items:center;gap:7px;white-space:nowrap;}'
    '.nav-right .hdr-call:hover{background:#1f2418!important;color:#fff!important;}'
    '.nav-right .hdr-book{background:#587735!important;color:#fff!important;border:2px solid #587735!important;white-space:nowrap;}'
    '.nav-right .hdr-book:hover{background:#3f5a22!important;border-color:#3f5a22!important;color:#fff!important;}'
    '.nav-right .hdr-ico{font-size:1.05em;line-height:1;}'
    + NAV_CSS_MOBILE +
    '@media(max-width:991px){.nav-right{width:100%;gap:8px;padding:10px 0 4px;}'
    '.nav-right .nav-btn{flex:1;justify-content:center;text-align:center;}}'
    "</style>")

NAV_JS = """<script id="tmlnav-js">
/* Deterministic mobile menu: owns open/close instead of relying on Webflow's
   interaction script, which doesn't reliably drive this rebuilt header. */
(function () {
  var btn = document.querySelector(".menu-button");
  var menu = document.querySelector(".nav-menu");
  if (!btn || !menu) return;
  var open = false;
  function set(v) {
    open = v;
    document.documentElement.classList.toggle("tmlnav-open", v);
    btn.setAttribute("aria-expanded", v ? "true" : "false");
  }
  btn.setAttribute("aria-label", "Menu");
  btn.setAttribute("aria-expanded", "false");
  btn.addEventListener("click", function (e) {
    e.preventDefault(); e.stopImmediatePropagation();
    set(!open);
  }, true);
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) set(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && open) set(false); });
  document.addEventListener("click", function (e) {
    if (open && !menu.contains(e.target) && !btn.contains(e.target)) set(false);
  });
})();
</script>"""


for f in sorted(F.rglob("index.html")):
    h = orig = f.read_text("utf-8", errors="replace")

    i, j = h.find("<nav"), h.find("</nav>")
    if i == -1:
        continue

    # the header block spans the primary <nav> plus the trailing nav-right div
    right_start = h.find('<div class="nav-right">')
    right_end = h.find("</div></nav>", right_start)
    if right_start == -1 or right_end == -1:
        continue
    header = h[i:right_end + len("</div></nav>")]

    # 1. collect the pieces we keep
    items = {m.group("label").strip().lower(): m.group(0) for m in NAV_ITEM.finditer(header)}
    drops = {m.group("label").strip().lower(): m.group(0) for m in DROPDOWN.finditer(header)}

    def item(*keys):
        for k in keys:
            for label, html in items.items():
                if label.startswith(k):
                    return html
        return ""

    def drop(*keys):
        for k in keys:
            for label, html in drops.items():
                if k in label:
                    return html
        return ""

    home, services, about = item("home"), item("services"), item("about")
    brands = drop("brand")
    if not (home and services and about and brands):
        continue

    # 2. rebuild: Home · Services · Brands · About  (+ new right side)
    inner_start = header.find('<div class="nav-inner">')
    if inner_start == -1:
        continue
    new_header = (header[:inner_start] + '<div class="nav-inner">'
                  + home + services + brands + about + "</div>" + RIGHT_HTML + "</nav>")
    h = h.replace(header, new_header, 1)
    n["headers"] += 1

    # 3. mobile menu mirrors the same structure (Webflow reuses this nav markup)
    #    — nothing extra to do; the same block drives both.

    # 4. Service Areas -> footer (once), next to the existing footer link column
    if "tmlhdr-areas" not in h:
        areas = ('<div class="tmlhdr-areas"><h4>Service areas</h4><ul>'
                 '<li><a href="/fixed/service-areas/the-woodlands-tx">The Woodlands, TX</a></li>'
                 "<li>Conroe, TX</li><li>Spring, TX</li><li>Magnolia, TX</li>"
                 "<li>Tomball, TX</li><li>Montgomery, TX</li><li>Willis, TX</li>"
                 "<li>Houston, TX</li></ul></div>")
        css = ('<style id="tmlhdr-areas-css">'
               '.tmlhdr-areas{padding:26px 0 4px;}'
               '.tmlhdr-areas h4{color:#cfe84d;font-size:14px;letter-spacing:.08em;text-transform:uppercase;margin:0 0 10px;}'
               '.tmlhdr-areas ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px 18px;}'
               '.tmlhdr-areas li{color:#cfd6c4;font-size:14px;}'
               '.tmlhdr-areas a{color:#fff;text-decoration:none;font-weight:600;}'
               '.tmlhdr-areas a:hover{color:#cfe84d;}'
               "</style>")
        foot = h.find('<section class="footer">')
        if foot > -1:
            close = h.find("</section>", foot)
            container_end = h.rfind("</div>", foot, close)
            if container_end > -1:
                h = h[:container_end] + areas + h[container_end:]
                h = h.replace("</head>", css + "</head>", 1)
                n["footers"] += 1

    # always refresh our injected css/js so edits take effect on re-run
    h = re.sub(r'<style id="tmlhdr-css">.*?</style>', "", h, flags=re.S)
    h = re.sub(r'<script id="tmlnav-js">.*?</script>', "", h, flags=re.S)
    h = h.replace("</head>", HDR_CSS + "</head>", 1)
    h = h.replace("</body>", NAV_JS + "</body>", 1)

    if h != orig:
        f.write_text(h, "utf-8")
        n["pages"] += 1

for k, v in sorted(n.items()):
    print(f"{k}: {v}")
