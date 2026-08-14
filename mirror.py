#!/usr/bin/env python3
"""Static mirror of www.tmlgarageservices.com (Webflow) -> site/

- Crawls sitemap.xml + all internal links found in pages.
- Saves pages as site/<path>/index.html.
- Mirrors all cdn.prod.website-files.com assets (incl. srcset variants and
  url() refs inside CSS) to site/assets/, and the Webflow jQuery from
  cloudfront to site/assets/cf/.
- Rewrites absolute self-domain links to root-relative paths.
"""
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = "https://www.tmlgarageservices.com"
CDN = "https://cdn.prod.website-files.com/"
CF = "https://d3e54v103j8qbb.cloudfront.net/"
OUT = Path(__file__).parent / "site"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def page_path(url_path: str) -> Path:
    p = url_path.strip("/")
    return OUT / "index.html" if not p else OUT / p / "index.html"

def asset_local(url: str) -> Path:
    if url.startswith(CDN):
        rel, prefix = url[len(CDN):], "assets"
    else:
        rel, prefix = url[len(CF):], "assets/cf"
    rel = urllib.parse.unquote(rel.split("?")[0])
    return OUT / prefix / rel

# ---- 1. collect page URLs -------------------------------------------------
sitemap = fetch(BASE + "/sitemap.xml").decode()
queue = {u.replace(BASE, "") or "/" for u in re.findall(r"<loc>([^<]+)</loc>", sitemap)}
queue.add("/")
seen, pages = set(), {}

while queue:
    path = queue.pop()
    if path in seen:
        continue
    seen.add(path)
    url = BASE + urllib.parse.quote(path, safe="/-_.~:")
    try:
        html = fetch(url).decode("utf-8", "replace")
    except Exception as e:
        print(f"  SKIP {path}: {e}")
        continue
    pages[path] = html
    print(f"  page {path}")
    for href in re.findall(r'href="(/[^"#?]*)"', html) + re.findall(
            rf'href="{BASE}(/[^"#?]*)"', html):
        h = href.rstrip("/") or "/"
        if "." not in h.split("/")[-1] and h not in seen:
            queue.add(h)

# Webflow custom 404 page (assets scanned below like any page)
try:
    not_found = fetch(BASE + "/definitely-not-a-page-404").decode("utf-8", "replace")
except urllib.error.HTTPError as e:
    not_found = e.read().decode("utf-8", "replace")

# ---- 2. collect asset URLs ------------------------------------------------
raw_re = re.compile(r'https://(?:cdn\.prod\.website-files\.com|d3e54v103j8qbb\.cloudfront\.net)/[^\s"\'<>]+')

def find_assets(text: str) -> set:
    urls = set()
    found = []
    for m in raw_re.findall(text):
        parts = m.split(",https://")  # data-video-urls lists
        found.append(parts[0])
        found.extend("https://" + p for p in parts[1:])
    for cand in found:
        cand = cand.split("&quot;")[0].split("\\")[0].rstrip(",;&")
        # css url(...) leaves an unbalanced trailing paren; filenames like "(2).jpg" are balanced
        while cand.endswith(")") and cand.count("(") < cand.count(")"):
            cand = cand[:-1]
        if len(cand) > len(CDN):
            urls.add(cand)
    return urls

assets = set()
for html in list(pages.values()) + [not_found]:
    assets.update(find_assets(html))

def grab(url: str, extract_css: bool = False):
    dest = asset_local(url)
    if dest.exists():
        return None
    try:
        data = fetch(url)
    except Exception as e:
        print(f"  SKIP asset {url}: {e}")
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    if extract_css or dest.suffix == ".css":
        return find_assets(data.decode("utf-8", "replace"))
    return None

print(f"\n{len(assets)} assets ...")
with ThreadPoolExecutor(16) as ex:
    nested = [r for r in ex.map(grab, assets) if r]
    sub = {u for lst in nested for u in lst} - assets
    if sub:
        print(f"  +{len(sub)} css-referenced assets")
        list(ex.map(grab, sub))

# ---- 3. rewrite + write pages --------------------------------------------
def rewrite(html: str) -> str:
    html = re.sub(r'<link href="https://cdn\.prod\.website-files\.com" rel="preconnect"[^>]*/>', "", html)
    # SRI hashes no longer match once cdn URLs inside the assets are rewritten
    html = re.sub(r'\s+integrity="[^"]*"', "", html)
    html = html.replace(CDN, "/assets/").replace(CF, "/assets/cf/")
    # %2F-encoded slashes in asset paths would 404 on a static host
    html = re.sub(r'/assets/[^"\'\s<>]*', lambda m: m.group(0).replace("%2F", "/"), html)
    html = html.replace(f'href="{BASE}/', 'href="/').replace(f'href="{BASE}"', 'href="/"')
    # the live site has two internal links with a stray space in the path
    html = re.sub(r'href="(/[^"]*?) +([^" ]*)"', r'href="\1\2"', html)
    # keep the mirror out of search indexes until the domain cutover
    if 'name="robots"' not in html:
        html = html.replace("<head>", '<head><meta name="robots" content="noindex, nofollow">', 1)
    # version switcher (site/switch.js); NOTE: a mirror refresh only rewrites
    # the ORIGINAL pages — site/fixed/ keeps its applied fixes
    html = html.replace("</body>", '<script src="/switch.js" defer></script></body>', 1)
    return html

for path, html in pages.items():
    if " " in path:  # space-path duplicates of real pages; links are fixed in rewrite()
        continue
    dest = page_path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rewrite(html), encoding="utf-8")

# Webflow custom 404 page -> 404.html (Cloudflare Pages convention)
(OUT / "404.html").write_text(rewrite(not_found), encoding="utf-8")

# also rewrite CSS url() refs to the cdn
for css in OUT.rglob("*.css"):
    t = css.read_text("utf-8", errors="replace")
    if CDN in t or CF in t:
        css.write_text(t.replace(CDN, "/assets/").replace(CF, "/assets/cf/"), "utf-8")

print(f"\nDone: {len(pages)} pages -> {OUT}")
