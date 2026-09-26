"""Helpers to draw fresh illustrated 'photos' (1080x1920) when no real photo fits a topic.
Import from an episode script, draw, then save into assets/photos/<name>.jpg and register it in index.json.

    import sys; sys.path.insert(0, "engine"); from diagram import *
    im, d = canvas("sea")            # "sea" | "engine" | "blueprint" | "sky"
    yacht_profile(im, waterline=820)  # side view yacht, bow left, x 60..1020
    box(d, (600, 760, 740, 840), "ENGINE"); pipe(d, [(740, 800), (900, 900)], TURQ, flow=True)
    save(im, "ep002-cooling")        # -> assets/photos/ep002-cooling.jpg
Keep the top 560px and bottom 560px calm: the engine draws the header there and cards at the bottom.
Put the interesting part between y=620 and y=1300 so labels can point at it.
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
NAVY = (9, 24, 54); GOLD = (196, 156, 74); GOLD_L = (236, 200, 120)
TURQ = (18, 196, 204); WHITE = (255, 255, 255); CORAL = (240, 96, 84); STEEL = (170, 182, 196)
F = lambda wt, sz: ImageFont.truetype(os.path.join(ROOT, "assets/fonts/montserrat-latin-%d-normal.woff" % wt), sz)

def vgrad(stops, h=H, w=W):
    ys = np.linspace(0, 1, h)[:, None]; out = np.zeros((h, w, 3))
    for c in range(3): out[:, :, c] = np.interp(ys, [s[0] for s in stops], [s[1][c] for s in stops])
    return out

def canvas(kind="sea", waterline=820):
    if kind == "sea":
        arr = vgrad([(0, (40, 120, 190)), (waterline / H * 0.999, (150, 210, 235)), (waterline / H, (20, 170, 190)), (0.7, (8, 110, 150)), (1, (4, 40, 80))])
    elif kind == "engine":
        arr = vgrad([(0, (60, 70, 84)), (0.5, (120, 132, 146)), (1, (40, 46, 56))])
    elif kind == "blueprint":
        arr = vgrad([(0, (8, 40, 90)), (1, (4, 20, 50))])
    else:
        arr = vgrad([(0, (60, 150, 225)), (1, (190, 230, 250))])
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    if kind == "blueprint":
        for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(120, 180, 255, 35), width=1)
        for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(120, 180, 255, 35), width=1)
    if kind == "sea":  # light rays underwater
        rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); r = ImageDraw.Draw(rays)
        for x0 in (140, 380, 640, 900):
            r.polygon([(x0 - 30, waterline), (x0 + 30, waterline), (x0 + 160, H), (x0 - 40, H)], fill=(200, 245, 255, 40))
        im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(20)))
    return im, ImageDraw.Draw(im, "RGBA")

def yacht_profile(im, waterline=820, x0=60, x1=1020, tint_under=True):
    """Clean white motor-yacht side profile, bow at left. Returns dict of useful points."""
    sx = (x1 - x0) / 960.0; P = lambda pts: [(x0 + (x - 60) * sx, y - 800 + waterline) for x, y in pts]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon(P([(55, 648), (120, 740), (230, 830), (380, 878), (560, 886), (1002, 884), (1002, 692)]), fill=(245, 247, 250, 255))
    d.polygon(P([(190, 800), (230, 830), (380, 878), (560, 886), (1002, 884), (1002, 800)]), fill=(24, 36, 58, 255))
    d.line(P([(185, 796), (1002, 796)]), fill=NAVY + (255,), width=9)
    d.line(P([(88, 694), (1002, 704)]), fill=GOLD + (255,), width=4)
    for x in (470, 560, 650): d.rounded_rectangle(P([(x, 728), (x + 70, 744)]), radius=8, fill=(26, 38, 56, 255))
    d.polygon(P([(250, 690), (380, 600), (880, 596), (900, 606), (920, 692)]), fill=(250, 251, 252, 255))
    d.polygon(P([(300, 676), (395, 614), (600, 612), (600, 676)]), fill=(28, 44, 66, 255))
    d.polygon(P([(630, 614), (860, 612), (872, 676), (630, 676)]), fill=(28, 44, 66, 255))
    d.polygon(P([(430, 596), (470, 560), (820, 560), (840, 596)]), fill=(245, 247, 250, 255))
    d.polygon(P([(480, 520), (500, 508), (800, 508), (812, 520)]), fill=(245, 247, 250, 255))
    if tint_under:
        a = np.array(lay); below = np.zeros(a.shape[:2], bool); below[int(waterline):] = True
        m = below & (a[..., 3] > 0); a[m, :3] = (a[m, :3] * 0.6 + np.array([14, 90, 120]) * 0.4).astype(np.uint8)
        lay = Image.fromarray(a)
    im.alpha_composite(lay)
    Q = lambda x, y: P([(x, y)])[0]
    return {"bow": Q(70, 660), "stern": Q(1000, 760), "engine_room": Q(680, 810), "keel": Q(560, 884),
            "flybridge": Q(640, 560), "saloon": Q(560, 640), "transom": Q(1000, 840), "waterline_y": waterline}

def box(d, xy, label="", color=GOLD_L, fill=(9, 24, 54, 200), fs=26):
    d.rounded_rectangle(xy, radius=14, fill=fill, outline=color + (255,), width=4)
    if label: d.text(((xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2), label, font=F(800, fs), fill=WHITE + (255,), anchor="mm")

def pipe(d, pts, color=TURQ, width=14, flow=True):
    d.line(pts, fill=color + (255,), width=width, joint="curve")
    if flow:
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            mx, my = (xa + xb) / 2, (ya + yb) / 2; ang = math.atan2(yb - ya, xb - xa); s = width * 1.6
            tip = (mx + s * math.cos(ang), my + s * math.sin(ang))
            l = (mx + s * math.cos(ang + 2.5), my + s * math.sin(ang + 2.5)); r = (mx + s * math.cos(ang - 2.5), my + s * math.sin(ang - 2.5))
            d.polygon([tip, l, r], fill=WHITE + (255,))

def glow(im, draw_fn, radius=8):
    """draw_fn(d) on a separate layer, then composite with a soft glow (nice for 'energy' / flow lines)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(lay)); g = lay.filter(ImageFilter.GaussianBlur(radius))
    im.alpha_composite(g); im.alpha_composite(lay)

def save(im, name):
    path = os.path.join(ROOT, "assets/photos", name + ".jpg"); im.convert("RGB").save(path, quality=92); return path
