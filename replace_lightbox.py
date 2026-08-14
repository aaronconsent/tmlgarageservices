#!/usr/bin/env python3
"""Replace the remaining Webflow lightbox links with a native <dialog>.

The carousel replacement already took care of the lightboxes inside it. What is
left are the photo grids on the four /projects/ pages. Each is an <a href="#">
whose real behaviour lives in the Webflow bundle — with the bundle gone, those
links would jump to the top of the page instead of opening the photo.

Same behaviour as before: click a photo, it opens large over a dimmed backdrop;
Escape, the close button, or a click outside closes it. The dialog element gives
focus trapping and Escape handling for free, which the Webflow one did not do.

Idempotent.
"""
import html as H
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

CSS = """<style id="tmllb-css">
.tmllb-open{display:block;width:100%;padding:0;border:0;background:none;cursor:zoom-in;}
.tmllb-open picture{display:block;}
.tmllb-open img{display:block;width:100%;}
.tmllb-open:focus-visible{outline:2px solid #587735;outline-offset:2px;}
.tmllb{border:0;padding:0;background:transparent;max-width:min(94vw,1200px);max-height:92vh;}
.tmllb::backdrop{background:rgba(15,18,12,.86);}
.tmllb img{display:block;max-width:100%;max-height:88vh;border-radius:12px;}
.tmllb-inner{position:relative;}
.tmllb-close{position:absolute;top:-14px;right:-14px;width:40px;height:40px;border-radius:50%;
 border:0;background:#fff;color:#1f2418;font-size:22px;line-height:1;cursor:pointer;
 box-shadow:0 4px 14px rgba(0,0,0,.3);}
.tmllb-close:focus-visible{outline:2px solid #587735;outline-offset:2px;}
</style>"""

JS = """<script id="tmllb-js">
/* Native <dialog> lightbox: replaces the Webflow one. */
(function () {
  var dlg = document.querySelector(".tmllb");
  var full = dlg && dlg.querySelector("img");
  var opens = document.querySelectorAll(".tmllb-open");
  if (!dlg || !full || !opens.length) return;
  if (typeof dlg.showModal !== "function") return;   // no dialog support: photos still show inline
  opens.forEach(function (btn) {
    btn.addEventListener("click", function () {
      full.src = btn.getAttribute("data-full");
      full.alt = btn.getAttribute("data-alt") || "";
      dlg.showModal();
    });
  });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  var close = dlg.querySelector(".tmllb-close");
  if (close) close.addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("close", function () { full.removeAttribute("src"); });
})();
</script>"""

DIALOG = ('<dialog class="tmllb" aria-label="Photo"><div class="tmllb-inner">'
          '<button type="button" class="tmllb-close" aria-label="Close">&times;</button>'
          '<img alt=""></div></dialog>')

LINK = re.compile(r'<a[^>]*class="[^"]*w-lightbox[^"]*"[^>]*>(?P<inner>.*?)</a>', re.S)


def convert(html):
    made = 0

    def one(m):
        nonlocal made
        inner = m.group("inner")
        pic = re.search(r"<picture>.*?</picture>|<img[^>]*>", inner, re.S)
        if not pic:
            return m.group(0)
        js = re.search(r'<script type="application/json"[^>]*>(.*?)</script>', inner, re.S)
        full = ""
        if js:
            try:
                full = json.loads(js.group(1))["items"][0]["url"]
            except Exception:
                full = ""
        picture = pic.group(0)
        if not full:
            src = re.search(r'\ssrc="([^"]+)"', picture)
            full = src.group(1) if src else ""
        alt = re.search(r'\salt="([^"]*)"', picture)
        alt = alt.group(1) if alt else ""
        made += 1
        return (f'<button type="button" class="tmllb-open" data-full="{full}" data-alt="{alt}" '
                f'aria-label="Enlarge photo{": " + alt if alt else ""}">{picture}</button>')

    html = LINK.sub(one, html)
    return html, made


def main():
    pages = total = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        if "w-lightbox" not in html:
            continue
        html, n = convert(html)
        if not n:
            continue
        html = re.sub(r'<style id="tmllb-css">.*?</style>', "", html, flags=re.S)
        html = re.sub(r'<script id="tmllb-js">.*?</script>', "", html, flags=re.S)
        html = re.sub(r'<dialog class="tmllb".*?</dialog>', "", html, flags=re.S)
        html = html.replace("</head>", CSS + "</head>", 1)
        html = html.replace("</body>", DIALOG + JS + "</body>", 1)
        if html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            total += n
            print(f"  {f.relative_to(F)}: {n} photos")
    print(f"pages changed: {pages}, lightbox links replaced: {total}")


if __name__ == "__main__":
    main()
