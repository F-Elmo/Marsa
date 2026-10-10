"""Illustration for episode 010 (pre-departure checklist): fuel 'rule of thirds' tank.
New look: cream nautical-chart paper with depth contours and a compass rose (previous: blueprint, amber, dusk,
teal underwater, violet studio, thermal, paper-cut). Run from repo root: python3 episodes/art/010_diagrams.py"""
import sys, math; sys.path.insert(0, "engine")
from diagram import *

def chart_canvas():
    arr = vgrad([(0, (244, 236, 214)), (1, (230, 220, 194))])
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    for k in range(9):   # wavy depth contours
        y0 = 120 + k * 210
        d.line([(x, y0 + 40 * math.sin(x / 170 + k) + 18 * math.sin(x / 61 + 2 * k)) for x in range(-10, W + 20, 12)],
               fill=(70, 120, 160, 60), width=3)
    for i, (x, y, s) in enumerate([(130, 1460, "12"), (930, 1510, "18"), (180, 300, "9"), (900, 380, "15"), (520, 1580, "21")]):
        d.text((x, y), s, font=F(600, 30), fill=(70, 100, 130, 120), anchor="mm")
    cx, cy, r = 880, 1700, 120  # compass rose (bottom right, faint, outside action area)
    for a in range(0, 360, 45):
        L = r if a % 90 == 0 else r * 0.6; t = math.radians(a)
        d.polygon([(cx, cy), (cx + L * math.sin(t) + 14 * math.cos(t), cy - L * math.cos(t) + 14 * math.sin(t)), (cx + L * math.sin(t), cy - L * math.cos(t))], fill=(9, 24, 54, 70))
    d.ellipse([cx - r * 0.75, cy - r * 0.75, cx + r * 0.75, cy + r * 0.75], outline=(9, 24, 54, 70), width=3)
    return im, d

im, d = chart_canvas()
x0, x1, y0, y1 = 330, 750, 640, 1300; h3 = (y1 - y0) / 3
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0 + 18, y0 + 24, x1 + 18, y1 + 24], 50, fill=(0, 0, 0, 80))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(im, "RGBA")
d.rounded_rectangle([x0, y0, x1, y1], 50, fill=(250, 250, 250, 255))
cols = [GOLD, TURQ, CORAL]
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16], 38, fill=255)
fill = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fill)
for i, c in enumerate(cols): fd.rectangle([x0, y0 + 16 + i * (h3 - 10.7), x1, y0 + 16 + (i + 1) * (h3 - 10.7)], fill=c + (255,))
fill.putalpha(Image.fromarray(np.minimum(np.array(fill.getchannel("A")), np.array(mask)))); im.alpha_composite(fill)
d = ImageDraw.Draw(im, "RGBA")
for i in (1, 2):
    y = y0 + 16 + i * (h3 - 10.7); d.line([(x0 + 16, y), (x1 - 16, y)], fill=(255, 255, 255, 255), width=8)
d.rounded_rectangle([x0, y0, x1, y1], 50, outline=NAVY + (255,), width=12)
d.rounded_rectangle([490, 590, 590, 646], 12, fill=NAVY + (255,))          # filler cap
# icons in each band: arrow out, arrow back, shield
cx = (x0 + x1) / 2
def arrow(yc, right=True):
    s = 1 if right else -1
    d.line([(cx - 80 * s, yc), (cx + 60 * s, yc)], fill=WHITE + (255,), width=22)
    d.polygon([(cx + 100 * s, yc), (cx + 50 * s, yc - 42), (cx + 50 * s, yc + 42)], fill=WHITE + (255,))
arrow(y0 + 16 + 0.5 * (h3 - 10.7), True); arrow(y0 + 16 + 1.5 * (h3 - 10.7), False)
yc = y0 + 16 + 2.5 * (h3 - 10.7)
d.polygon([(cx, yc - 70), (cx + 60, yc - 45), (cx + 52, yc + 20), (cx, yc + 70), (cx - 52, yc + 20), (cx - 60, yc - 45)], fill=WHITE + (255,))
d.line([(cx - 24, yc + 2), (cx - 4, yc + 24), (cx + 30, yc - 22)], fill=CORAL + (255,), width=12, joint="curve")
print(save(im, "ep010-thirds"), "band centres y:", [round(y0 + 16 + (i + .5) * (h3 - 10.7)) for i in range(3)])
