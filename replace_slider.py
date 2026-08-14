#!/usr/bin/env python3
"""Replace the Webflow slider (and the lightbox inside it) with native code.

The "Some of our work" gallery on five pages was a Webflow slider whose slides
were each a Webflow lightbox link. Between them they are the main reason those
pages still load jQuery and the Webflow bundle.

The replacement is a scroll-snap carousel: the browser does the scrolling, so
swipe, momentum, trackpads and arrow keys all work natively and there is no
animation library. The lightbox becomes a native <dialog>. Roughly 2 KB of CSS
and JS replaces a dependency on ~417 KB of framework.

Behaviour kept: same photos in the same order, arrows, position dots, swipe,
click-a-photo-to-enlarge. Behaviour gained: keyboard support, focus trapping in
the dialog, and it respects reduced-motion.

Idempotent.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmlcar-css">
.tmlcar{position:relative;}
.tmlcar-track{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;
 scroll-behavior:smooth;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:2px;}
.tmlcar-track::-webkit-scrollbar{display:none;}
.tmlcar-track:focus-visible{outline:2px solid #587735;outline-offset:3px;border-radius:14px;}
.tmlcar-item{flex:0 0 78%;scroll-snap-align:start;margin:0;border-radius:14px;overflow:hidden;
 background:#eef0e7;}
.tmlcar-open{display:block;width:100%;padding:0;border:0;background:none;cursor:zoom-in;}
.tmlcar-item picture{display:block;}
.tmlcar-item img{width:100%;height:100%;display:block;aspect-ratio:4/3;object-fit:cover;
 transition:transform .3s ease;}
.tmlcar-open:hover img{transform:scale(1.03);}
.tmlcar-open:focus-visible{outline:2px solid #587735;outline-offset:-2px;}
@media(min-width:640px){.tmlcar-item{flex-basis:calc((100% - 14px)/2);}}
@media(min-width:900px){.tmlcar-item{flex-basis:calc((100% - 28px)/3);}}
@media(min-width:1200px){.tmlcar-item{flex-basis:calc((100% - 56px)/5);}}
.tmlcar-nav{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:44px;height:44px;
 border-radius:50%;border:1px solid #d8ddcc;background:#fff;color:#1f2418;cursor:pointer;
 display:grid;place-items:center;box-shadow:0 4px 14px rgba(31,36,24,.16);
 transition:opacity .16s ease,background .16s ease;}
.tmlcar-nav:hover{background:#f2f5eb;}
.tmlcar-nav:focus-visible{outline:2px solid #587735;outline-offset:2px;}
.tmlcar-nav[disabled]{opacity:0;pointer-events:none;}
/* inside the edges: hanging them outside pushed the page wider than the
   viewport and produced a horizontal scrollbar on narrow screens */
.tmlcar-nav.prev{left:8px;} .tmlcar-nav.next{right:8px;}
.tmlcar-nav svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2;
 stroke-linecap:round;stroke-linejoin:round;}
.tmlcar-dots{display:flex;justify-content:center;gap:7px;margin-top:14px;padding:0;}
.tmlcar-dot{width:8px;height:8px;padding:0;border:0;border-radius:50%;background:#c8cfba;
 cursor:pointer;transition:background .16s ease,transform .16s ease;}
.tmlcar-dot[aria-current="true"]{background:#587735;transform:scale(1.25);}
.tmlcar-dot:focus-visible{outline:2px solid #587735;outline-offset:3px;}
.tmlcar-lb{border:0;padding:0;background:transparent;max-width:min(94vw,1200px);max-height:92vh;}
.tmlcar-lb::backdrop{background:rgba(15,18,12,.86);}
.tmlcar-lb img{display:block;max-width:100%;max-height:88vh;border-radius:12px;}
.tmlcar-lb-close{position:absolute;top:-14px;right:-14px;width:40px;height:40px;border-radius:50%;
 border:0;background:#fff;color:#1f2418;font-size:22px;line-height:1;cursor:pointer;
 box-shadow:0 4px 14px rgba(0,0,0,.3);}
.tmlcar-lb-close:focus-visible{outline:2px solid #587735;outline-offset:2px;}
.tmlcar-lb-inner{position:relative;}
@media(prefers-reduced-motion:reduce){
 .tmlcar-track{scroll-behavior:auto;}
 .tmlcar-item img,.tmlcar-nav,.tmlcar-dot{transition:none;}
}
</style>"""

JS = """<script id="tmlcar-js">
/* Scroll-snap carousel: the browser owns the scrolling, so swipe, momentum and
   keyboard all come for free. Replaces the Webflow slider + lightbox. */
(function () {
  document.querySelectorAll(".tmlcar").forEach(function (car) {
    var track = car.querySelector(".tmlcar-track");
    var prev = car.querySelector(".tmlcar-nav.prev");
    var next = car.querySelector(".tmlcar-nav.next");
    var dots = Array.prototype.slice.call(car.querySelectorAll(".tmlcar-dot"));
    var items = Array.prototype.slice.call(car.querySelectorAll(".tmlcar-item"));
    if (!track || !items.length) return;

    function step() {
      var r = items[0].getBoundingClientRect();
      return r.width + 14;
    }
    function perView() {
      return Math.max(1, Math.round(track.clientWidth / step()));
    }
    function sync() {
      /* tolerance, not zero: the track carries 2px of padding so scrollLeft
         rests at 2 rather than 0 when it is at the start */
      var max = track.scrollWidth - track.clientWidth - 4;
      if (prev) prev.disabled = track.scrollLeft <= 4;
      if (next) next.disabled = track.scrollLeft >= max;
      var page = Math.round(track.scrollLeft / (step() * perView()));
      dots.forEach(function (d, i) { d.setAttribute("aria-current", i === page ? "true" : "false"); });
    }
    function nudge(dir) {
      track.scrollBy({ left: dir * step() * perView(), behavior: "smooth" });
      window.setTimeout(sync, 400);   // belt and braces if no scroll event lands
    }
    if (prev) prev.addEventListener("click", function () { nudge(-1); });
    if (next) next.addEventListener("click", function () { nudge(1); });
    dots.forEach(function (d, i) {
      d.addEventListener("click", function () {
        track.scrollTo({ left: step() * perView() * i, behavior: "smooth" });
      });
    });
    /* sync on every scroll frame: a debounce here left the arrows showing a
       stale enabled/disabled state after a click-driven scroll */
    var ticking = false;
    track.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { ticking = false; sync(); });
    }, { passive: true });
    window.addEventListener("resize", sync);
    sync();

    /* lightbox */
    var dlg = car.querySelector(".tmlcar-lb");
    var full = dlg && dlg.querySelector("img");
    if (!dlg || !full || typeof dlg.showModal !== "function") return;
    car.querySelectorAll(".tmlcar-open").forEach(function (btn) {
      btn.addEventListener("click", function () {
        full.src = btn.getAttribute("data-full");
        full.alt = btn.getAttribute("data-alt") || "";
        dlg.showModal();
      });
    });
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg) dlg.close();          // click the backdrop
    });
    var close = dlg.querySelector(".tmlcar-lb-close");
    if (close) close.addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("close", function () { full.removeAttribute("src"); });
  });
})();
</script>"""

ARROW_L = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>')
ARROW_R = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>')


def balanced_div(html, start):
    m = re.match(r"<div[^>]*>", html[start:])
    if not m:
        return None
    depth, pos = 1, start + m.end()
    for t in re.finditer(r"<div\b|</div>", html[pos:]):
        depth += 1 if t.group(0) == "<div" else -1
        if depth == 0:
            return pos + t.end()
    return None


def convert(html):
    i = html.find("w-slider")
    if i == -1:
        return html, 0
    start = html.rfind("<div", 0, i)
    end = balanced_div(html, start)
    if end is None:
        return html, 0
    block = html[start:end]

    slides = []
    for m in re.finditer(r'<a[^>]*class="[^"]*w-lightbox[^"]*"[^>]*>(.*?)</a>', block, re.S):
        inner = m.group(1)
        pic = re.search(r"<picture>.*?</picture>|<img[^>]*>", inner, re.S)
        if not pic:
            continue
        js = re.search(r'<script type="application/json"[^>]*>(.*?)</script>', inner, re.S)
        fullsrc = ""
        if js:
            try:
                fullsrc = json.loads(js.group(1))["items"][0]["url"]
            except Exception:
                fullsrc = ""
        picture = pic.group(0)
        if not fullsrc:
            src = re.search(r'\ssrc="([^"]+)"', picture)
            fullsrc = src.group(1) if src else ""
        alt = re.search(r'\salt="([^"]*)"', picture)
        slides.append((picture, fullsrc, alt.group(1) if alt else ""))

    if len(slides) < 2:
        return html, 0

    figs = "".join(
        f'<figure class="tmlcar-item">'
        f'<button type="button" class="tmlcar-open" data-full="{full}" data-alt="{alt}" '
        f'aria-label="Enlarge photo{": " + alt if alt else ""}">{pic}</button></figure>'
        for pic, full, alt in slides)
    dots = "".join(f'<button type="button" class="tmlcar-dot" aria-label="Go to slide {n+1}"></button>'
                   for n in range(max(1, (len(slides) + 4) // 5)))

    new = (
        '<div class="tmlcar">'
        '<div class="tmlcar-track" tabindex="0" role="group" aria-label="Photos of our work">'
        + figs + "</div>"
        f'<button type="button" class="tmlcar-nav prev" aria-label="Previous photos">{ARROW_L}</button>'
        f'<button type="button" class="tmlcar-nav next" aria-label="Next photos">{ARROW_R}</button>'
        f'<div class="tmlcar-dots">{dots}</div>'
        '<dialog class="tmlcar-lb" aria-label="Photo"><div class="tmlcar-lb-inner">'
        '<button type="button" class="tmlcar-lb-close" aria-label="Close">&times;</button>'
        '<img alt=""></div></dialog>'
        "</div>")
    return html[:start] + new + html[end:], len(slides)


def main():
    pages = total = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "w-slider" not in html:
            continue
        html, n = convert(html)
        if not n:
            continue
        html = re.sub(r'<style id="tmlcar-css">.*?</style>', "", html, flags=re.S)
        html = re.sub(r'<script id="tmlcar-js">.*?</script>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        html = html.replace("</body>", JS + "</body>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            total += n
            print(f"  {f.relative_to(F)}: {n} photos")
    print(f"sliders replaced: {pages}, photos carried over: {total}")


if __name__ == "__main__":
    main()
