#!/usr/bin/env python3
"""Compose the 1200x630 share card: garage photo + phone CTA + real 5-star
review line. Output: site/assets/tml-og.jpg"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

SITE = Path(__file__).parent / "site"
A = SITE / "assets" / "66b2dae9e779df43d0d269c9"
W, H = 1200, 630

OLIVE = (88, 119, 53)
VIS = (207, 232, 77)
INK = (20, 27, 13)
STAR = (255, 196, 0)

# background: dusk garage photo, cover-cropped, darkened left-to-right
bg = Image.open(A / "66b5115cc6a1fdc1f8b546d6_modern-garage-door-services.jpg").convert("RGB")
scale = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * scale), round(bg.height * scale)))
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
              (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
overlay = Image.new("L", (W, H), 0)
od = ImageDraw.Draw(overlay)
for x in range(W):
    od.line([(x, 0), (x, H)], fill=int(215 - 150 * (x / W)))
dark = Image.new("RGB", (W, H), (12, 17, 8))
bg = Image.composite(dark, bg, overlay.point(lambda v: v))
bg = Image.blend(bg, bg.filter(ImageFilter.GaussianBlur(0)), 0)

d = ImageDraw.Draw(bg)
F = lambda name, size: ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}.ttf", size)
narrow_xl = F("Arial Narrow Bold", 92)
narrow_lg = F("Arial Narrow Bold", 56)
bold_md = F("Arial Bold", 34)
reg_md = F("Arial", 30)
bold_sm = F("Arial Bold", 27)

x = 64
# logo
logo = Image.open(A / "6889f290b8d5feae9f0bcb19_66b2f5077df3a3b06a15a1bd_TMLGarageServices-Logo-web 1ngfui.png").convert("RGBA")
lw = 300
logo = logo.resize((lw, round(logo.height * lw / logo.width)))
pad = Image.new("RGBA", (lw + 36, logo.height + 24), (255, 255, 255, 235))
bg.paste(pad, (x - 18, 46 - 12), pad)
bg.paste(logo, (x, 46), logo)

# headline + phone
d.text((x, 170), "SAME-DAY GARAGE DOOR REPAIR", font=narrow_lg, fill=(255, 255, 255))
d.text((x, 238), "(832) 887-8747", font=narrow_xl, fill=VIS)
d.rectangle([x, 348, x + 560, 356], fill=VIS)

# CTA pill
cta = "CALL NOW — WE ANSWER"
tw = d.textlength(cta, font=bold_md)
d.rounded_rectangle([x, 388, x + tw + 56, 388 + 64], radius=32, fill=OLIVE)
d.text((x + 28, 388 + 14), cta, font=bold_md, fill=(255, 255, 255))

# review line — stars drawn as polygons (system fonts lack the glyph)
import math
def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)
ry = 500
for i in range(5):
    star(x + 16 + i * 38, ry + 17, 16, STAR)
d.text((x + 220, ry + 3), "5.0 · 213 Google reviews", font=bold_sm, fill=(255, 255, 255))
d.text((x, ry + 46), "“Excellent service from start to finish! Fast response,", font=reg_md, fill=(232, 236, 224))
d.text((x, ry + 82), "fair pricing, and high-quality work.”", font=reg_md, fill=(232, 236, 224))

out = SITE / "assets" / "tml-og.jpg"
bg.save(out, "JPEG", quality=88)
print("wrote", out, bg.size)
