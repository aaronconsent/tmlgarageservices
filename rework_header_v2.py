#!/usr/bin/env python3
"""Header pass 2: left-aligned nav with small icons, and a Brands menu that
behaves properly.

What was wrong with the old one:
  * It used Webflow's hover-only dropdown. Hover menus don't work on touch — a
    tap either does nothing or fires the link — and on desktop the panel closes
    the moment the pointer strays off the diagonal between label and list.
  * The toggle was a <div>, so it was unreachable by keyboard and announced
    nothing to a screen reader.
  * The items sat centred in the bar, drifting away from the logo.

What replaces it: the same four items, same type, same colours, moved to the
left beside the logo with a small line icon each. Brands is now a real <button>
with aria-expanded and an owned panel — click or keyboard on any device, hover
and it opens on click rather than hover, so it behaves the same on a phone as on
a desktop. Escape, outside-click and arrow keys all work.

Runs after rework_header.py. Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

ICON = {
    "home": '<path d="M3 9.5 10 4l7 5.5V16a1 1 0 0 1-1 1h-3.5v-4.5h-5V17H4a1 1 0 0 1-1-1z"/>',
    "services": '<path d="M12.6 3.3a4 4 0 0 0-5 5L3.4 12.5a1.6 1.6 0 1 0 2.2 2.2l4.2-4.2a4 4 0 0 0 5-5l-2.3 2.3-1.9-.4-.4-1.9z"/>',
    "brands": '<path d="M10 3l2.1 4.3 4.7.7-3.4 3.3.8 4.7L10 13.8 5.8 16l.8-4.7L3.2 8l4.7-.7z"/>',
    "about": '<circle cx="10" cy="6.6" r="2.8"/><path d="M4 16.4a6 6 0 0 1 12 0z"/>',
}
CHEVRON = ('<svg class="tmlnav2-chev" viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
           '<path d="M5.5 8l4.5 4.5L14.5 8" fill="none" stroke="currentColor" '
           'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def icon(name):
    return (f'<svg class="tmlnav2-ico" viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
            f'{ICON[name]}</svg>')


CSS = """<style id="tmlnav2-css">
.tmlnav2{display:flex;align-items:center;gap:4px;}
.tmlnav2-link{display:inline-flex;align-items:center;gap:8px;padding:9px 12px;border-radius:9px;
 font-weight:700;font-size:14.5px;letter-spacing:.02em;text-transform:uppercase;color:#1f2418;
 text-decoration:none;background:none;border:0;cursor:pointer;font-family:inherit;line-height:1;
 white-space:nowrap;transition:background .14s ease,color .14s ease;}
.tmlnav2-link:hover{background:#eef1e6;color:#3f5a22;}
.tmlnav2-link:focus-visible{outline:2px solid #587735;outline-offset:2px;}
.tmlnav2-ico{width:17px;height:17px;flex:0 0 auto;fill:currentColor;opacity:.72;}
.tmlnav2-link:hover .tmlnav2-ico{opacity:1;}
.tmlnav2-chev{width:14px;height:14px;flex:0 0 auto;transition:transform .16s ease;opacity:.7;}
.tmlnav2-toggle[aria-expanded="true"]{background:#eef1e6;color:#3f5a22;}
.tmlnav2-toggle[aria-expanded="true"] .tmlnav2-chev{transform:rotate(180deg);}
.tmlnav2-drop{position:relative;}
.tmlnav2-panel{position:absolute;top:calc(100% + 8px);left:0;min-width:212px;z-index:60;
 background:#fff;border:1px solid #e2e5d9;border-radius:12px;padding:6px;
 box-shadow:0 14px 34px rgba(31,36,24,.14);}
.tmlnav2-panel[hidden]{display:none;}
.tmlnav2-panel a{display:block;padding:10px 12px;border-radius:8px;font-weight:600;font-size:14.5px;
 color:#1f2418;text-decoration:none;line-height:1.25;transition:background .12s ease,color .12s ease;}
.tmlnav2-panel a:hover{background:#f2f5eb;color:#3f5a22;}
.tmlnav2-panel a:focus-visible{outline:2px solid #587735;outline-offset:-2px;}
/* nav sits beside the logo instead of floating in the middle of the bar */
.navbar-wrapper .nav-menu{flex:1 1 auto;display:flex!important;align-items:center;
 justify-content:space-between!important;gap:18px;}
.navbar-wrapper .nav-inner{margin-right:auto;justify-content:flex-start!important;}
@media(prefers-reduced-motion:reduce){
 .tmlnav2-link,.tmlnav2-chev,.tmlnav2-panel a{transition:none;}
}
@media(max-width:991px){
 .tmlnav2{display:block;}
 .tmlnav2-link{width:100%;justify-content:flex-start;font-size:16.5px;padding:13px 2px;border-radius:0;}
 .tmlnav2-link:hover{background:none;}
 .tmlnav2-drop{position:static;}
 .tmlnav2-toggle{justify-content:space-between!important;}
 .tmlnav2-toggle .tmlnav2-chev{margin-left:auto;}
 .tmlnav2-panel{position:static;border:0;box-shadow:none;padding:0 0 6px 25px;min-width:0;background:none;}
 .tmlnav2-panel a{padding:10px 0;font-size:15.5px;}
 .navbar-wrapper .nav-menu{display:block!important;}
}
</style>"""

JS = """<script id="tmlnav2-js">
/* Click-only, on every device. Hover-to-open was the whole problem: it fights
   the click (hover opens, the click then toggles it shut), it can't be used on
   a touchscreen, and it closes if the pointer strays off the diagonal between
   the label and the list. A click has none of those failure modes. */
(function () {
  var wrap = document.querySelector(".tmlnav2-drop");
  if (!wrap) return;
  var btn = wrap.querySelector(".tmlnav2-toggle");
  var panel = wrap.querySelector(".tmlnav2-panel");
  if (!btn || !panel) return;

  function set(open) {
    panel.hidden = !open;
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  btn.addEventListener("click", function (e) {
    e.preventDefault(); e.stopPropagation();
    set(panel.hidden);
  });
  document.addEventListener("click", function (e) {
    if (!panel.hidden && !wrap.contains(e.target)) set(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) { set(false); btn.focus(); }
  });
  wrap.addEventListener("focusout", function (e) {
    if (!wrap.contains(e.relatedTarget)) set(false);
  });
  btn.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault(); set(true);
      var links = panel.querySelectorAll("a");
      (e.key === "ArrowDown" ? links[0] : links[links.length - 1]).focus();
    }
  });
  panel.addEventListener("keydown", function (e) {
    var links = Array.prototype.slice.call(panel.querySelectorAll("a"));
    var i = links.indexOf(document.activeElement);
    if (i < 0) return;
    if (e.key === "ArrowDown") { e.preventDefault(); (links[i + 1] || links[0]).focus(); }
    if (e.key === "ArrowUp") { e.preventDefault(); (links[i - 1] || links[links.length - 1]).focus(); }
    if (e.key === "Home") { e.preventDefault(); links[0].focus(); }
    if (e.key === "End") { e.preventDefault(); links[links.length - 1].focus(); }
  });
})();
</script>"""

# matches both the original Webflow markup and this script's own output, so a
# re-run can update the CSS/JS instead of silently doing nothing
LINK = re.compile(r'<a[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<label>.*?)</a>', re.S)
TAGS = re.compile(r"<[^>]+>")


def build_nav(inner):
    """Rebuild the nav items from whatever the current header already links to."""
    brand_links, main = [], {}
    for m in LINK.finditer(inner):
        href = m.group("href")
        label = TAGS.sub("", m.group("label")).strip()
        if not label:
            continue
        if "/brands/" in href:
            brand_links.append((href, label))
        else:
            main[label.lower()] = (href, label)

    def one(key, ico, text):
        hit = next((v for k, v in main.items() if k.startswith(key)), None)
        if not hit:
            return ""
        return f'<a class="tmlnav2-link" href="{hit[0]}">{icon(ico)}<span>{text}</span></a>'

    out = [one("home", "home", "Home"), one("service", "services", "Services")]
    if brand_links:
        out.append(
            '<div class="tmlnav2-drop">'
            '<button class="tmlnav2-link tmlnav2-toggle" type="button" aria-expanded="false" '
            f'aria-controls="tmlnav2-brands">{icon("brands")}<span>Brands</span>{CHEVRON}</button>'
            '<div class="tmlnav2-panel" id="tmlnav2-brands" hidden>'
            + "".join(f'<a href="{h}">{l}</a>' for h, l in brand_links)
            + "</div></div>")
    out.append(one("about", "about", "About"))
    return '<div class="nav-inner tmlnav2">' + "".join(x for x in out if x) + "</div>"


def main():
    changed = 0
    for f in sorted(F.rglob("index.html")):
        h = orig = f.read_text("utf-8", errors="replace")
        m = re.search(r'<div class="nav-inner[^"]*">', h)
        if not m:
            continue
        depth, end = 1, None
        for t in re.finditer(r"<div\b|</div>", h[m.end():]):
            depth += 1 if t.group(0) == "<div" else -1
            if depth == 0:
                end = m.end() + t.end()
                break
        if end is None:
            continue
        nav = build_nav(h[m.end():end])
        if 'class="tmlnav2-link"' not in nav:
            continue
        h = h[:m.start()] + nav + h[end:]
        h = re.sub(r'<style id="tmlnav2-css">.*?</style>', "", h, flags=re.S)
        h = re.sub(r'<script id="tmlnav2-js">.*?</script>', "", h, flags=re.S)
        h = h.replace("</head>", CSS + "</head>", 1)
        h = h.replace("</body>", JS + "</body>", 1)
        if h != orig:
            f.write_text(h, "utf-8")
            changed += 1
    print(f"headers reworked: {changed}")


if __name__ == "__main__":
    main()
