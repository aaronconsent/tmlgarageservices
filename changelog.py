#!/usr/bin/env python3
"""Render CHANGELOG.md -> site/changes/index.html (owner-facing log page).

Tiny markdown subset: # / ## / ### headings, - bullets, **bold**, `code`,
--- rules, blank-line paragraphs. Re-run after every CHANGELOG.md edit.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "CHANGELOG.md"
DEST = ROOT / "site" / "changes" / "index.html"

def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

lines = SRC.read_text("utf-8").splitlines()
out, para, in_list = [], [], False

def flush_para():
    global para
    if para:
        out.append(f"<p>{inline(' '.join(para))}</p>")
        para = []

def close_list():
    global in_list
    if in_list:
        out.append("</ul>")
        in_list = False

for ln in lines:
    s = ln.strip()
    if not s:
        flush_para()
        close_list()
    elif s == "---":
        flush_para(); close_list()
        out.append("<hr>")
    elif s.startswith("### "):
        flush_para(); close_list()
        out.append(f"<h3>{inline(s[4:])}</h3>")
    elif s.startswith("## "):
        flush_para(); close_list()
        out.append(f"<h2>{inline(s[3:])}</h2>")
    elif s.startswith("# "):
        flush_para(); close_list()
        out.append(f"<h1>{inline(s[2:])}</h1>")
    elif s.startswith("- "):
        flush_para()
        if not in_list:
            out.append("<ul>")
            in_list = True
        out.append(f"<li>{inline(s[2:])}</li>")
    elif in_list and ln.startswith("  "):
        out[-1] = out[-1][:-5] + " " + inline(s) + "</li>"
    else:
        para.append(s)
flush_para(); close_list()

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Website Fix Log — TML Garage Services</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #f4f6f0; color: #1f2418;
        font: 16px/1.65 -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }}
  .page {{ max-width: 46rem; margin: 0 auto; padding: 2.5rem 1.25rem 5rem; }}
  h1 {{ font-size: 1.9rem; line-height: 1.2; margin: 0 0 0.4rem; }}
  h2 {{ font-size: 1.25rem; margin: 2.4rem 0 0.7rem; padding-top: 1.4rem;
       border-top: 2px solid #587735; color: #2f4416; }}
  h3 {{ font-size: 1.05rem; margin: 1.6rem 0 0.5rem; }}
  p {{ margin: 0.7rem 0; color: #3c4633; }}
  ul {{ margin: 0.6rem 0 1rem; padding-left: 1.3rem; }}
  li {{ margin: 0.5rem 0; color: #3c4633; }}
  strong {{ color: #1f2418; }}
  code {{ background: #e8ecdd; padding: 0.1em 0.35em; border-radius: 4px; font-size: 0.92em; }}
  hr {{ border: 0; height: 1px; background: #d8ddc9; margin: 2rem 0; }}
  .bar {{ display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;
         margin: 1.2rem 0 0; padding: 0.9rem 1.1rem; background: #fff;
         border: 1px solid #d8ddc9; border-radius: 10px; font-size: 0.95rem; }}
  .bar a {{ color: #3f5a22; font-weight: 600; }}
  @media print {{ .bar {{ display: none; }} body {{ background: #fff; }} }}
</style>
</head>
<body>
<div class="page">
{chr(10).join(out)}
<div class="bar">
  <a href="/">View the original site</a>
  <a href="/fixed">View the fixed site</a>
</div>
</div>
</body>
</html>
"""
DEST.parent.mkdir(parents=True, exist_ok=True)
DEST.write_text(page, "utf-8")
print(f"rendered {SRC.name} -> {DEST.relative_to(ROOT)}")
