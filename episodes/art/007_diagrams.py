"""Illustrations for episode 007 (lithium vs AGM batteries). Run from repo root: python3 episodes/art/007_diagrams.py
New look for this episode: night-at-anchor indigo/violet with stars and a moon, warm cabin lights, and glowing
'studio' cut-away batteries (previous episodes: blueprint, amber heat, dusk, deep teal underwater)."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

LEAD = (126, 132, 146); LEAD_D = (80, 86, 100); MAT = (236, 236, 226); CASE_A = (34, 36, 44); CASE_L = (238, 242, 246)
CELL = (40, 110, 210); CELL_L = (110, 170, 245); PCB = (20, 120, 70); WARM = (255, 200, 120); VIOLET = (120, 90, 220)

def night_canvas(seed=1, sea_y=None, moon=True):
    stops = [(0, (14, 10, 46)), (0.45, (30, 22, 84)), (1, (8, 10, 34))]
    if sea_y: stops = [(0, (12, 10, 44)), (sea_y / H * 0.999, (54, 40, 120)), (sea_y / H, (16, 24, 70)), (1, (4, 8, 26))]
    im = Image.fromarray(vgrad(stops).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay); rnd = random.Random(seed)
    top = sea_y or H
    for k in range(160):
        x = rnd.uniform(0, W); y = rnd.uniform(0, top - 20); r = rnd.choice([1, 1, 1.5, 2, 2.5])
        g.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(90, 230)))
    im.alpha_composite(lay)
    if moon:
        def m(gg): gg.ellipse([800, 150, 920, 270], fill=(250, 244, 220, 255))
        glow(im, m, radius=26)
        d = ImageDraw.Draw(im, "RGBA"); d.ellipse([826, 150, 946, 262], fill=(16, 12, 50, 255))  # crescent
    return im, ImageDraw.Draw(im, "RGBA")

def studio_canvas(seed=2, hue=(0, 0, 0)):
    """Dark violet studio backdrop with a soft spotlight and a floor reflection line."""
    im, d = night_canvas(seed=seed, moon=False)
    spot = Image.new("RGBA", (W, H), (0, 0, 0, 0)); s = ImageDraw.Draw(spot)
    s.ellipse([40, 520, 1040, 1420], fill=(120 + hue[0], 100 + hue[1], 220 + hue[2], 90))
    im.alpha_composite(spot.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 1290, W, H], fill=(8, 6, 26, 150))
    d.line([(0, 1290), (W, 1290)], fill=(160, 140, 255, 90), width=3)
    return im, d

def battery(im, b, kind="agm", cut=True, level=None, scale=1.0):
    """Big 12V battery. b=(x0,y0,x1,y1) body box. kind 'agm' (black case, lead plates + glass mats)
    or 'lfp' (white case, 4 blue prismatic cells + green BMS board). level=None|fraction fill gauge."""
    x0, y0, x1, y1 = b; d = ImageDraw.Draw(im, "RGBA")
    case = CASE_A if kind == "agm" else CASE_L; rim = (90, 96, 110) if kind == "agm" else (170, 180, 196)
    # glow behind
    def gl(g): g.rounded_rectangle([x0 - 10, y0 - 50, x1 + 10, y1 + 10], radius=40, outline=((GOLD_L if kind == "agm" else TURQ) + (200,)), width=14)
    glow(im, gl, radius=26); d = ImageDraw.Draw(im, "RGBA")
    # terminals
    tw = 70 * scale
    for (tx, col) in ((x0 + (x1 - x0) * 0.2, (210, 40, 40)), (x0 + (x1 - x0) * 0.8, (30, 30, 34))):
        d.rounded_rectangle([tx - tw / 2, y0 - 46 * scale, tx + tw / 2, y0 + 4], radius=10, fill=(200, 160, 70, 255))
        d.rounded_rectangle([tx - tw / 2 - 10, y0 - 14 * scale, tx + tw / 2 + 10, y0 + 6], radius=8, fill=col + (255,))
    d.text((x0 + (x1 - x0) * 0.2, y0 - 70 * scale), "+", font=F(800, int(54 * scale)), fill=(255, 120, 110, 255), anchor="mm")
    d.text((x0 + (x1 - x0) * 0.8, y0 - 70 * scale), "–", font=F(800, int(54 * scale)), fill=(220, 225, 235, 255), anchor="mm")
    # lid + body
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(30 * scale), fill=case + (255,), outline=rim + (255,), width=5)
    d.rectangle([x0 + 6, y0 + 50 * scale, x1 - 6, y0 + 58 * scale], fill=rim + (255,))
    ix0, iy0, ix1, iy1 = x0 + 34 * scale, y0 + 84 * scale, x1 - 34 * scale, y1 - 34 * scale
    if level is not None:
        d.rounded_rectangle([ix0, iy0, ix1, iy1], radius=16, fill=(12, 12, 30, 255))
        h = iy1 - iy0; ytop = iy1 - h * level
        col = GOLD if kind == "agm" else TURQ
        d.rounded_rectangle([ix0 + 8, ytop, ix1 - 8, iy1 - 8], radius=12, fill=col + (255,))
        if kind == "agm":  # lower half = keep in reserve (hatched coral)
            ym = iy1 - h * 0.5
            rw, rh = int(ix1 - ix0 - 16), int(iy1 - 8 - ym)
            tile = Image.new("RGBA", (rw, rh), (120, 40, 44, 255)); td = ImageDraw.Draw(tile)
            for k in range(-rh // 34 - 2, rw // 34 + 2):
                xa = k * 34; td.line([(xa, rh), (xa + rh, 0)], fill=CORAL + (150,), width=8)
            im.alpha_composite(tile, (int(ix0 + 8), int(ym))); d = ImageDraw.Draw(im, "RGBA")
            d.line([(ix0 - 16, ym), (ix1 + 16, ym)], fill=WHITE + (255,), width=6)
        else:
            yr = iy1 - h * 0.08
            d.rectangle([ix0 + 8, yr, ix1 - 8, iy1 - 8], fill=(10, 90, 110, 255))
        return {"top": [int((ix0 + ix1) / 2), int(ytop + 40)], "half": [int((ix0 + ix1) / 2), int(iy1 - h * 0.5)],
                "bottom": [int((ix0 + ix1) / 2), int(iy1 - 60)], "body": [int((x0 + x1) / 2), int((y0 + y1) / 2)]}
    if not cut:
        return {"body": [int((x0 + x1) / 2), int((y0 + y1) / 2)]}
    d.rounded_rectangle([ix0, iy0, ix1, iy1], radius=16, fill=(16, 16, 26, 255))
    if kind == "agm":
        n = 13; step = (ix1 - ix0) / n
        for i in range(n):
            xa = ix0 + i * step
            d.rectangle([xa + 4, iy0 + 18, xa + step * 0.52, iy1 - 14], fill=LEAD + (255,))
            for yy in range(int(iy0 + 30), int(iy1 - 20), 26):  # plate grid
                d.line([(xa + 4, yy), (xa + step * 0.52, yy)], fill=LEAD_D + (255,), width=3)
            d.rectangle([xa + step * 0.56, iy0 + 10, xa + step * 0.96, iy1 - 8], fill=MAT + (255,))
            for yy in range(int(iy0 + 16), int(iy1 - 10), 9):  # glass-fibre texture
                d.line([(xa + step * 0.58, yy), (xa + step * 0.94, yy + 4)], fill=(200, 200, 186, 255), width=1)
        d.rectangle([ix0, iy0, ix1, iy0 + 16], fill=LEAD_D + (255,))
        return {"plates": [int(ix0 + step * 3.25), int((iy0 + iy1) / 2)], "mats": [int(ix0 + step * 9.75), int((iy0 + iy1) / 2 + 40)],
                "case": [int(x1 - 12), int(y1 - 120)], "terminal": [int(x0 + (x1 - x0) * 0.2), int(y0 - 24)]}
    # lfp: 4 cells + BMS board
    bh = 92 * scale
    d.rounded_rectangle([ix0 + 10, iy0 + 10, ix1 - 10, iy0 + 10 + bh], radius=10, fill=PCB + (255,))
    for k in range(12):
        xx = ix0 + 40 + k * (ix1 - ix0 - 80) / 11
        d.line([(xx, iy0 + 20), (xx, iy0 + bh)], fill=(90, 200, 130, 200), width=3)
    cx = (ix0 + ix1) / 2; d.rectangle([cx - 60, iy0 + 28, cx + 60, iy0 + bh - 8], fill=(20, 22, 26, 255))
    d.text((cx, iy0 + 10 + bh / 2), "BMS", font=F(800, int(30 * scale)), fill=(230, 255, 240, 255), anchor="mm")
    n = 4; gap = 14; cw = (ix1 - ix0 - gap * (n + 1)) / n; cy0 = iy0 + bh + 30
    for i in range(n):
        xa = ix0 + gap + i * (cw + gap)
        d.rounded_rectangle([xa, cy0, xa + cw, iy1 - 12], radius=12, fill=CELL + (255,))
        d.rectangle([xa + 10, cy0 + 12, xa + 24, iy1 - 24], fill=CELL_L + (160,))
        d.text((xa + cw / 2, (cy0 + iy1) / 2), "3.2V", font=F(800, int(34 * scale)), fill=WHITE + (255,), anchor="mm")
        if i < n - 1: d.rectangle([xa + cw - 20, cy0 - 14, xa + cw + gap + 20, cy0 + 4], fill=(200, 160, 70, 255))
    return {"bms": [int(cx), int(iy0 + 10 + bh / 2)], "cells": [int(ix0 + gap + cw * 1.5 + gap), int((cy0 + iy1) / 2 + 60)],
            "case": [int(x1 - 12), int(y1 - 120)], "terminal": [int(x0 + (x1 - x0) * 0.8), int(y0 - 24)]}

pts = {}
# 1) hook: yacht at anchor at night, cut-away battery compartment glowing (one dark AGM, one white lithium)
WL = 1060
im, d = night_canvas(seed=4, sea_y=WL)
info = yacht_profile(im, waterline=WL, x0=40, x1=1040)
d = ImageDraw.Draw(im, "RGBA")
# darken yacht for night, then warm windows
night = Image.new("RGBA", (W, H), (10, 10, 50, 0)); nd = ImageDraw.Draw(night)
nd.rectangle([0, 600, W, WL + 120], fill=(14, 12, 60, 80)); im.alpha_composite(night)
d = ImageDraw.Draw(im, "RGBA")
def win(g):
    for (a, b2, c, e) in ((330, 885, 610, 920), (640, 882, 860, 918)): g.rounded_rectangle([a, b2, c, e], radius=8, fill=WARM + (230,))
glow(im, win, radius=16)
# reflections of moon + lights on water
d = ImageDraw.Draw(im, "RGBA")
for k in range(12):
    y = WL + 150 + k * 34; w = 50 + k * 12
    d.line([(860 - w / 2 + 14 * math.sin(k * 1.7) + t, y + 3 * math.sin(t / 30)) for t in range(0, int(w), 10)], fill=(250, 240, 210, 120 - k * 8), width=5)
    d.line([(470 - w / 3 + 10 * math.cos(k * 1.3) + t, y + 14) for t in range(0, int(w * 2 / 3), 10)], fill=WARM + (100 - k * 7,), width=5)
# cut-away compartment below deck
d.rounded_rectangle([300, 960, 820, 1250], radius=30, fill=(10, 8, 30, 235), outline=GOLD_L + (255,), width=5)
pa = battery(im, (340, 1060, 560, 1220), "agm", cut=False, scale=0.5)
pl = battery(im, (600, 1060, 780, 1220), "lfp", cut=False, scale=0.5)
d = ImageDraw.Draw(im, "RGBA")
for (bx, by, col) in ((450, 1140, GOLD_L), (690, 1140, TURQ)):
    d.text((bx, by), "AGM" if col == GOLD_L else "LFP", font=F(800, 40), fill=(col if col == TURQ else (240, 210, 140)) + (255,), anchor="mm")
# anchor chain
d.line([(140, 1010), (90, 1500)], fill=(150, 150, 180, 200), width=6)
pts["ep007-hook"] = {"agm": [450, 1140], "lithium": [690, 1140], "yacht": [540, 880]}
save(im, "ep007-hook")

# 2) AGM cut-away (studio)
im, d = studio_canvas(seed=5, hue=(40, 10, -80))
pts["ep007-agm"] = battery(im, (170, 760, 910, 1250), "agm"); save(im, "ep007-agm")
# 3) AGM usable level (half)
im, d = studio_canvas(seed=6, hue=(40, 10, -80))
pts["ep007-agm-level"] = battery(im, (300, 720, 780, 1260), "agm", level=1.0); save(im, "ep007-agm-level")
# 4) Lithium cut-away
im, d = studio_canvas(seed=7, hue=(-60, 40, 0))
pts["ep007-lfp"] = battery(im, (170, 760, 910, 1250), "lfp"); save(im, "ep007-lfp")
# 5) Lithium usable level
im, d = studio_canvas(seed=8, hue=(-60, 40, 0))
pts["ep007-lfp-level"] = battery(im, (300, 720, 780, 1260), "lfp", level=0.92); save(im, "ep007-lfp-level")

# 6) weight: balance scale, heavy AGM down left, light lithium up right
im, d = studio_canvas(seed=9)
cx, cy = 540, 760; tilt = math.radians(12)
L = 380; lx, ly = cx - L * math.cos(tilt), cy + L * math.sin(tilt); rx, ry = cx + L * math.cos(tilt), cy - L * math.sin(tilt)
d.polygon([(cx - 90, 1270), (cx + 90, 1270), (cx + 16, cy + 10), (cx - 16, cy + 10)], fill=(190, 160, 90, 255))
d.rounded_rectangle([cx - 160, 1262, cx + 160, 1290], radius=10, fill=(150, 120, 60, 255))
d.line([(lx, ly), (rx, ry)], fill=GOLD_L + (255,), width=16); d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=GOLD + (255,))
for (px, py) in ((lx, ly), (rx, ry)):
    d.line([(px, py), (px - 120, py + 200)], fill=(220, 200, 150, 255), width=4); d.line([(px, py), (px + 120, py + 200)], fill=(220, 200, 150, 255), width=4)
    d.rounded_rectangle([px - 150, py + 196, px + 150, py + 214], radius=8, fill=GOLD + (255,))
battery(im, (lx - 120, ly + 30 + 20, lx + 120, ly + 196), "agm", cut=False, scale=0.5)
battery(im, (rx - 85, ry + 90, rx + 85, ry + 196), "lfp", cut=False, scale=0.45)
d = ImageDraw.Draw(im, "RGBA")
d.text((lx, ly + 130), "AGM", font=F(800, 46), fill=(240, 210, 140, 255), anchor="mm")
d.text((rx, ry + 148), "LFP", font=F(800, 38), fill=(18, 150, 170, 255), anchor="mm")
d.polygon([(lx, ly + 330), (lx - 30, ly + 280), (lx + 30, ly + 280)], fill=CORAL + (255,))
d.polygon([(rx, ry + 230), (rx - 26, ry + 274), (rx + 26, ry + 274)], fill=TURQ + (255,))
pts["ep007-scale"] = {"agm": [int(lx), int(ly + 130)], "lithium": [int(rx), int(ry + 148)], "pivot": [cx, cy]}
save(im, "ep007-scale")

# 7) charging system: alternator -> protection/DC-DC -> lithium bank <- shore charger, BMS
im, d = studio_canvas(seed=10, hue=(-40, 20, 20))
def node(xy, label, col, sub=None):
    box(d, xy, label, color=col, fill=(14, 12, 46, 230), fs=30)
    if sub: d.text(((xy[0] + xy[2]) / 2, xy[3] + 30), sub, font=F(600, 24), fill=(200, 205, 230, 255), anchor="mm")
alt = (80, 700, 420, 820); prot = (600, 700, 1000, 820); shore = (80, 1100, 420, 1220)
batt_b = (600, 990, 940, 1230)
battery(im, batt_b, "lfp", cut=False, scale=0.6)
d = ImageDraw.Draw(im, "RGBA")
def wires(g):
    g.line([(420, 760), (600, 760)], fill=GOLD_L + (255,), width=12)
    g.line([(800, 820), (800, 940)], fill=TURQ + (255,), width=12)
    g.line([(420, 1160), (520, 1160), (520, 1110), (600, 1110)], fill=TURQ + (255,), width=12, joint="curve")
glow(im, wires, radius=10); d = ImageDraw.Draw(im, "RGBA")
node(alt, "ALTERNATOR", GOLD_L); node(prot, "PROTECTION", CORAL); node(shore, "LITHIUM CHARGER", TURQ)
for (x, y, ang) in ((510, 760, 0), (800, 880, 90), (560, 1110, 0)):
    a = math.radians(ang); s = 22
    d.polygon([(x + s * math.cos(a), y + s * math.sin(a)), (x + s * math.cos(a + 2.5), y + s * math.sin(a + 2.5)), (x + s * math.cos(a - 2.5), y + s * math.sin(a - 2.5))], fill=WHITE + (255,))
d.text((770, 1120), "LFP", font=F(800, 54), fill=(18, 150, 170, 255), anchor="mm")
d.rounded_rectangle([660, 1170, 880, 1212], radius=10, fill=PCB + (255,)); d.text((770, 1191), "BMS", font=F(800, 26), fill=WHITE + (255,), anchor="mm")
pts["ep007-charge"] = {"alternator": [250, 760], "protection": [800, 760], "charger": [250, 1160], "battery": [770, 1120], "bms": [770, 1191]}
save(im, "ep007-charge")

# 8) CTA background: blurred, darkened hook
im = Image.open("assets/photos/ep007-hook.jpg").convert("RGBA").filter(ImageFilter.GaussianBlur(14))
im.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 30, 110))); save(im, "ep007-cta")
import json; print(json.dumps(pts))
