#!/usr/bin/env python3
"""Remove Webflow leftovers from the Fixed site, one approved step at a time.

Each step is a named, self-contained transform. Only the steps listed in
APPROVED run, so nothing goes in without a decision. Every step must be
visually inert — it removes something dead, not something the page uses.

Idempotent: a page already clean is left untouched.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

# steps the owner has signed off on, in the order they were approved
APPROVED = [
    "dead-script",
    "self-host-fonts",
    "video-control",
    "cms-templates",
    "webflow-js",
    "last-published",
    "wf-identifiers",
    "interaction-hooks",
    "dead-classes",
    "empty-states",
    "ix-styles",
    "video-fallback-class",
]


def dead_script(html):
    """A Webflow tracking stub that was never exported: the path 404s on every
    page load. Nothing reads it, nothing depends on it."""
    return re.subn(r'<script[^>]+src="/g0lnomhfn3mg[^"]*"[^>]*>\s*</script>', "", html)


FONT_LINK = ('<link rel="preload" href="/assets/fonts/Inter-400-latin.woff2" as="font" '
             'type="font/woff2" crossorigin>'
             '<link rel="preload" href="/assets/fonts/BebasNeue-400-latin.woff2" as="font" '
             'type="font/woff2" crossorigin>'
             '<link rel="stylesheet" href="/assets/fonts/fonts.css">')


def self_host_fonts(html):
    """Drop the Google WebFont loader for a local stylesheet.

    The loader pulled a script from ajax.googleapis.com which then requested six
    families at every weight — about 36 font files' worth — for the four faces
    the site renders. It is render-blocking, so text waited on a third-party
    round-trip. The replacement serves the same faces from this site."""
    n = 0
    html, a = re.subn(r'<script[^>]+src="https://ajax\.googleapis\.com/ajax/libs/webfont/[^"]*"[^>]*>\s*</script>', "", html)
    html, b = re.subn(r'<script[^>]*>\s*WebFont\.load\(.*?\);?\s*</script>', "", html, flags=re.S)
    n += a + b
    if n and "/assets/fonts/fonts.css" not in html:
        html = html.replace("</head>", FONT_LINK + "</head>", 1)
    return html, n


VIDEO_JS = """<script id="tmlvid-js">
/* Play/pause for the hero background video. The <video> element already
   autoplays natively (autoplay + muted + loop + playsinline) and the stylesheet
   already sets object-fit, so Webflow's script was only driving this button. */
(function () {
  document.querySelectorAll("[data-w-bg-video-control]").forEach(function (btn) {
    var vid = document.getElementById(btn.getAttribute("aria-controls"));
    if (!vid) return;
    var icons = btn.querySelectorAll("span");
    function render() {
      var playing = !vid.paused;
      if (icons[0]) icons[0].hidden = !playing;
      if (icons[1]) icons[1].hidden = playing;
      btn.setAttribute("aria-label", playing ? "Pause video" : "Play video");
    }
    btn.addEventListener("click", function () {
      if (vid.paused) { vid.play(); } else { vid.pause(); }
    });
    vid.addEventListener("play", render);
    vid.addEventListener("pause", render);
    render();
    /* someone who has asked their device for less motion should not be handed
       a looping video; the button still lets them start it */
    try {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) vid.pause();
    } catch (e) {}
  });
})();
</script>"""


def video_control(html):
    """Take the background-video play/pause button off the Webflow bundle."""
    if "data-w-bg-video-control" not in html:
        return html, 0
    html = re.sub(r'<script id="tmlvid-js">.*?</script>', "", html, flags=re.S)
    return html.replace("</body>", VIDEO_JS + "</body>", 1), 1


def cms_templates(html):
    """Webflow CMS repeater templates: a URL-encoded copy of the list markup that
    the browser never renders. Dead weight, and every one of them still points at
    Webflow's own CDN rather than this site."""
    return re.subn(r'<script type="text/x-wf-template"[^>]*>.*?</script>', "", html, flags=re.S)


def webflow_js(html):
    """Remove jQuery and the Webflow bundle.

    Safe only once nothing on the page needs them. At the time this was enabled:
    slider, tabs, lightbox, forms and the FAQ accordions had all been replaced
    with native equivalents; the background video plays on its own attributes;
    the nav is driven by our own script; and no element is hidden waiting for a
    Webflow interaction to reveal it (checked across all 36 pages)."""
    n = 0
    html, a = re.subn(r'<script[^>]+src="[^"]*jquery[^"]*"[^>]*>\s*</script>', "", html)
    html, b = re.subn(r'<script[^>]+src="[^"]*/js/webflow[^"]*"[^>]*>\s*</script>', "", html)
    # the touch/JS feature-detect stub Webflow inlines next to them
    html, c = re.subn(r'<script[^>]*>\s*!function\(o,c\)\{var n=c\.documentElement.*?</script>', "", html, flags=re.S)
    return html, a + b + c


# checked against the stylesheet: these six w-* classes are matched by no rule in
# the site CSS or any injected block, so they are inert markup. The other 26 w-*
# classes ARE styled and must stay unless the stylesheet is rewritten with them.
DEAD_CLASSES = ("w-dyn-item", "w-dyn-repeater-item", "w-dyn-list", "w-dyn-items",
                "w-script", "w-background-video-atom")


def dead_classes(html):
    """Drop CMS-wrapper classes that nothing styles and nothing reads."""
    n = 0

    def clean(m):
        nonlocal n
        classes = m.group(1).split()
        keep = [c for c in classes if c not in DEAD_CLASSES]
        if len(keep) == len(classes):
            return m.group(0)
        n += len(classes) - len(keep)
        return f'class="{" ".join(keep)}"' if keep else ""

    return re.sub(r'class="([^"]*)"', clean, html), n


def empty_states(html):
    """Delete Webflow's CMS empty-state placeholders instead of keeping a Webflow
    class around to hide them.

    'No project gallery found.' and the empty <p class="w-dyn-bind-empty"></p>
    stubs exist only so an unfilled CMS field renders as nothing. They are hidden
    by .w-dyn-hide / .w-dyn-empty rules, so removing the class alone would make
    the placeholder text visible — the element has to go with it."""
    n = 0
    html, a = re.subn(r'<div[^>]*class="[^"]*w-dyn-(?:hide|empty)[^"]*"[^>]*>.*?</div>\s*</div>',
                      "", html, flags=re.S)
    html, b = re.subn(r'<p class="w-dyn-bind-empty"></p>', "", html)
    return html, a + b


def ix_styles(html):
    """Webflow emits <style> rules keyed to [data-w-id] to pre-position elements
    for its interactions engine. Both the engine and the attributes are gone, and
    the rules are also gated on html.w-mod-js which is no longer set."""
    return re.subn(r'<style>@media[^<]*\[data-w-id[^<]*</style>', "", html)


def video_fallback_class(html):
    """The <noscript> poster image was styled via [data-wf-bgvideo-fallback-img],
    an attribute the earlier step stripped. Rather than put a Webflow attribute
    back, point the same rules at a class so the no-JavaScript and
    reduced-motion behaviour stays exactly as it was."""
    if "tmlvid-fallback" in html or "data-wf-bgvideo-fallback-img" not in html:
        return html, 0
    n = 0
    html, a = re.subn(r'\[data-wf-bgvideo-fallback-img\]', ".tmlvid-fallback", html)
    # the poster <img> lives inside the same <noscript> as the rule, after a
    # <style> block — not immediately after <noscript>, and not the first
    # <noscript><img> in the document (that one is the Facebook pixel)
    def tag_img(m):
        return m.group(0).replace("<img ", '<img class="tmlvid-fallback" ', 1)
    html, b = re.subn(r'<noscript><style>[^<]*tmlvid-fallback.*?</noscript>', tag_img, html, flags=re.S)
    return html, a + b


def last_published(html):
    """The '<!-- Last Published: ... -->' banner Webflow stamps on every export."""
    return re.subn(r"<!--\s*Last Published:.*?-->", "", html, flags=re.S)


def wf_identifiers(html):
    """data-wf-domain / -page / -site / -collection / -item. Only Webflow's own
    runtime read these, and that is no longer loaded."""
    return re.subn(r'\sdata-wf-[a-z-]+="[^"]*"', "", html)


def interaction_hooks(html):
    """data-w-id pointed the Webflow interactions engine at an element. With the
    engine gone they address nothing. Also drops the widget config attributes
    that only its scripts read (data-animation / -collapse / -duration / -easing
    / -delay / -autoplay and friends on nav, slider and dropdown wrappers)."""
    n = 0
    html, a = re.subn(r'\sdata-w-id="[^"]*"', "", html)
    html, b = re.subn(r'\sdata-(?:animation|collapse|duration|easing2?|delay|autoplay|'
                      r'autoplay-limit|hide-arrows|disable-swipe|nav-spacing|infinite|'
                      r'hover|doc-height|no-scroll)="[^"]*"', "", html)
    return html, a + b


STEPS = {
    "dead-script": ("dead 404 script tag", dead_script),
    "last-published": ("Last Published comment", last_published),
    "wf-identifiers": ("data-wf-* identifiers", wf_identifiers),
    "self-host-fonts": ("Google WebFont loader -> self-hosted", self_host_fonts),
    "video-control": ("background-video play/pause -> native", video_control),
    "cms-templates": ("dead CMS repeater templates", cms_templates),
    "webflow-js": ("jQuery + Webflow bundle", webflow_js),
    "interaction-hooks": ("data-w-id + widget config attributes", interaction_hooks),
    "dead-classes": ("unstyled w-dyn-* wrapper classes", dead_classes),
    "empty-states": ("CMS empty-state placeholders", empty_states),
    "ix-styles": ("inert [data-w-id] interaction styles", ix_styles),
    "video-fallback-class": ("video fallback: attribute selector -> class", video_fallback_class),
}


def main():
    steps = sys.argv[1:] or APPROVED
    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        sys.exit(f"unknown step(s): {', '.join(unknown)}\nknown: {', '.join(STEPS)}")

    for name in steps:
        label, fn = STEPS[name]
        pages = hits = 0
        for f in sorted(F.rglob("index.html")):
            html = f.read_text("utf-8", errors="replace")
            new, n = fn(html)
            if n:
                f.write_text(new, "utf-8")
                pages += 1
                hits += n
        print(f"  {label}: removed {hits} on {pages} pages")


if __name__ == "__main__":
    main()
