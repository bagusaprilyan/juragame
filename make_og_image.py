#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buat og-image.png (1200x630) + favicon.ico untuk juragame.com pakai PIL."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 630
img = Image.new("RGB", (W, H), "#020617")
d = ImageDraw.Draw(img)

# ── Gradient background (indigo → pink, gelap) ──
for y in range(H):
    t = y / H
    r = int(2 + (10 - 2) * t)
    g = int(6 + (4 - 6) * t)
    b = int(23 + (40 - 23) * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# ── Glow bulat (indigo kiri-atas, pink kanan-bawah) ──
def glow(cx, cy, rad, color, alpha_max=70):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 40
    for i in range(steps, 0, -1):
        rr = int(rad * i / steps)
        a = int(alpha_max * (1 - i / steps) ** 1.5)
        ld.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    return layer

img = img.convert("RGBA")
img = Image.alpha_composite(img, glow(180, 90, 520, (99, 102, 241)))
img = Image.alpha_composite(img, glow(1050, 580, 460, (236, 72, 153)))
img = Image.alpha_composite(img, glow(760, 200, 300, (139, 92, 246), 45))
d = ImageDraw.Draw(img)

# ── Font ──
def font(sz, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()

f_logo  = font(88, True)
f_h1    = font(62, True)
f_sub   = font(30, False)
f_badge = font(22, True)

# ── Badge "PORTAL GAME GRATIS" ──
bx, by = 80, 92
badge_txt = "PORTAL GAME GRATIS"
tb = d.textbbox((0, 0), badge_txt, font=f_badge)
pad_x, pad_y = 20, 12
bw, bh = tb[2] - tb[0] + pad_x * 2, tb[3] - tb[1] + pad_y * 2
d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2,
                    fill=(99, 102, 241, 220))
d.text((bx + pad_x, by + pad_y - 2), badge_txt, font=f_badge, fill="#ffffff")

# ── Logo "Jura Game" ──
d.text((80, 160), "Jura Game", font=f_logo, fill="#818cf8")

# ── Judul utama (2 baris) ──
d.text((80, 300), "Mainkan Game HTML5", font=f_h1, fill="#ffffff")
d.text((80, 378), "Gratis di Browser", font=f_h1, fill="#f0abfc")

# ── Subjudul ──
d.text((80, 480), "Ratusan game casual seru — tanpa install, tanpa ribet.", font=f_sub, fill="#cbd5e1")

# ── Garis aksen ──
d.rounded_rectangle([80, 540, 300, 548], radius=4, fill=(236, 72, 153))

# ── Simpan ──
img = img.convert("RGB")
img.save("og-image.png", "PNG", optimize=True)
print(f"  ✅ og-image.png  {os.path.getsize('og-image.png')} bytes ({W}x{H})")

# ── Favicon.ico (multi-size) ──
ico = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
di = ImageDraw.Draw(ico)
for y in range(64):
    t = y / 64
    di.line([(0, y), (64, y)], fill=(int(99 + (236-99)*t), int(102 + (72-102)*t), int(241 + (153-241)*t), 255))
di.rounded_rectangle([0, 0, 63, 63], radius=14, outline=(0, 0, 0, 0))
f_ico = font(46, True)
ti = di.textbbox((0, 0), "J", font=f_ico)
di.text(((64 - (ti[2]-ti[0])) / 2 - ti[0], (64 - (ti[3]-ti[1])) / 2 - ti[1] - 3), "J", font=f_ico, fill="#ffffff")
ico.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print(f"  ✅ favicon.ico   {os.path.getsize('favicon.ico')} bytes")
