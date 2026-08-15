#!/usr/bin/env python3
"""One business name across the site: TML Garage Door Services.

The export carried at least six spellings — "T.M.L. Garage Services",
"TML Garage Services", "TML Garage DOOR Services", "TML garage DOOR services"
and so on — across page titles, social preview tags, body copy and image
descriptions. A business whose own name is written six ways reads as careless,
and search engines treat a consistent name as a local-ranking signal.

Only visible text and the attributes people actually read are touched:
page titles, meta descriptions, social tags, alt text and body copy. Addresses,
links, e-mail addresses and the domain itself (tmlgarageservices.com) are left
exactly as they are — those are not the name, and changing them would break
things.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

NAME = "TML Garage Door Services"

# every spelling seen in the audit, longest first so partial forms don't win
VARIANTS = [
    r"T\.M\.L\.\s+Garage\s+Door\s+Services",
    r"T\.M\.L\.\s+Garage\s+Services",
    r"TML\s+Garage\s+DOOR\s+Services",
    r"TML\s+garage\s+DOOR\s+SERVICES",
    r"TML\s+garage\s+DOOR\s+services",
    r"TMl\s+garage\s+DOOR\s+SERVICES",
    r"TML\s+GARAGE\s+DOOR\s+SERVICES",
    r"TML\s+Garage\s+Services",
]
PATTERN = re.compile("|".join(f"(?:{v})" for v in VARIANTS))

# regions that must never be rewritten: code, and anything that is an address
PROTECT = re.compile(
    r"<script\b.*?</script>|<style\b.*?</style>|"
    r'(?:href|src|srcset|action|data-full)="[^"]*"|'
    r"tmlgarageservices|sendajob|workiz",
    re.S | re.I)


def swap(text):
    """Replace the name outside protected regions."""
    out, last, n = [], 0, 0
    for m in PROTECT.finditer(text):
        chunk, k = PATTERN.subn(NAME, text[last:m.start()])
        out.append(chunk)
        out.append(m.group(0))
        n += k
        last = m.end()
    chunk, k = PATTERN.subn(NAME, text[last:])
    out.append(chunk)
    return "".join(out), n + k


# the Conroe location photo is described by the previous business name. The file
# path stays (it is an asset address); the words a screen reader announces do not.
ALT_FIXES = {
    'alt="TML Home Improvement 1488 Conroe Texas"':
        'alt="TML Garage Door Services on FM 1488 in Conroe, Texas"',
}


def main():
    pages = total = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        html, n = swap(html)
        for old, new in ALT_FIXES.items():
            if old in html:
                html = html.replace(old, new)
                n += 1
        if n and html != orig:
            f.write_text(html, "utf-8")
            pages += 1
            total += n
            print(f"  {f.relative_to(F)}: {n} corrected")
    print(f"pages changed: {pages}, name corrections: {total}")


if __name__ == "__main__":
    main()
