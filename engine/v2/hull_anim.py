"""Animated 'materials lab' diagrams for ep 018 (fibreglass vs aluminium hulls). 1080x1920@30 MP4s.
  python3 engine/v2/hull_anim.py OUTDIR [name ...]     names: vs, layup, gpros, gcons, weld, dent, acons, verdict, cta
  python3 engine/v2/hull_anim.py OUTDIR --still name t  (single PNG for checking)
Look (new for ep 018): dark charcoal-navy workbench with a fine dot grid and a warm spotlight; side A = amber/cream
fibreglass laminate (woven glass mat + resin), side B = brushed-silver aluminium plate with glowing weld seams.
Mechanisms shown: laminate lay-up into a mould, weight scale, impact crack vs dent, water seeping into the laminate
and raising osmosis blisters, noise waves in a chop, sun heating a metal deck, galvanic current to a sacrificial anode."""
import math, subprocess, sys, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fonts") + "/"
_fc = {}
def M(wt, sz):
    k = ("m", wt, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + f"montserrat-latin-{wt}-normal.woff", sz)
    return _fc[k]
def O(sz):
    k = ("o", sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + "oswald-latin-700-normal.woff", sz)
    return _fc[k]
NAVY = (9, 24, 54); GOLD = (214, 172, 86); TURQ = (18, 196, 204); WHITE = (255, 255, 255)
AMBER = (232, 176, 84); CREAM = (246, 232, 200); RESIN = (214, 150, 60); SILVER = (196, 204, 214); STEEL = (120, 132, 148)
RED = (240, 84, 70); GREEN = (70, 205, 125); INK = (6, 10, 20); SEA = (24, 120, 160)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t
def A(c, a): return tuple(int(v) for v in c[:3]) + (int(255 * clamp(a)),)
def fin(t, t0, d=0.35): return ease((t - t0) / d)
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- background: charcoal workbench, dot grid, spotlight
def _bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.hypot((xx - W / 2) / 760, (yy - 860) / 820), 0, 1) ** 1.6
    base = np.array((14, 18, 30), np.float32); warm = np.array((52, 48, 52), np.float32)
    arr = base + (warm - base) * g[..., None]
    im = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(im, "RGBA")
    for x in range(27, W, 54):
        for y in range(440, 1340, 54): d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(220, 210, 190, 34))
    a = np.zeros((H, W), np.uint8); a[1330:1450] = np.linspace(0, 255, 120).astype(np.uint8)[:, None]; a[1450:] = 255
    im.paste(Image.new("RGB", (W, H), (8, 10, 18)), (0, 0), Image.fromarray(a))     # calm caption zone
    a2 = np.zeros((H, W), np.uint8); a2[:300] = 255; a2[300:420] = np.linspace(255, 0, 120).astype(np.uint8)[:, None]
    im.paste(Image.new("RGB", (W, H), (8, 10, 18)), (0, 0), Image.fromarray(a2))    # calm logo zone
    return im
BG = _bg()
_rnd = random.Random(18)
DUST = [(_rnd.uniform(0, W), _rnd.uniform(430, 1330), _rnd.uniform(4, 14), _rnd.choice([1, 1, 2]), _rnd.uniform(0, 6.28)) for _ in range(45)]
def new(t):
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    for x, y, sp, r, ph in DUST:
        yy = 440 + ((y - 440 + sp * t) % 890); xx = x + 8 * math.sin(t * 0.6 + ph)
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 230, 190, 40))
    return im, d

def pill(d, cx, cy, s, f, bg, fg, a=1.0, padx=26, h=None):
    if a <= 0.01: return
    tw = f.getlength(s); h = h or int(f.size * 1.75)
    cx = clamp(cx, 40 + tw / 2 + padx, W - 40 - tw / 2 - padx)
    d.rounded_rectangle([cx - tw / 2 - padx, cy - h / 2, cx + tw / 2 + padx, cy + h / 2], radius=h // 2, fill=A(bg, 0.96 * a))
    d.text((cx, cy + 1), s, font=f, fill=A(fg, a), anchor="mm")
def title(d, tag, line, t, col=GOLD, y=470):
    a = fin(t, 0, 0.4)
    pill(d, W / 2, y, tag, M(800, 32), col, NAVY, a, h=58)
    if line:
        f = O(70)
        while f.getlength(line) > 980: f = O(f.size - 4)
        d.text((W / 2, y + 88 + (1 - a) * 30), line, font=f, fill=A(WHITE, a), anchor="mm", stroke_width=4, stroke_fill=A(INK, a))
def label(d, x, y, s, a, col=WHITE, sz=32, anchor="mm"):
    if a > 0.01: d.text((x, y), s, font=M(800, sz), fill=A(col, a), anchor=anchor, stroke_width=4, stroke_fill=A(INK, a))
def card(d, r, a, col=GOLD, fill=(20, 24, 38)):
    if a <= 0.01: return
    x0, y0, x1, y1 = r
    d.rounded_rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], radius=34, outline=A(col, 0.14 * a), width=8)
    d.rounded_rectangle(r, radius=26, fill=A(fill, 0.94 * a), outline=A(col, a), width=4)
def tick(d, cx, cy, a, col=GREEN, s=1.0):
    if a <= 0.01: return
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 30 * s], fill=A(col, a))
    d.line([(cx - 14 * s, cy + 1 * s), (cx - 4 * s, cy + 12 * s), (cx + 15 * s, cy - 11 * s)], fill=A(WHITE, a), width=int(7 * s), joint="curve")
def cross(d, cx, cy, a, col=RED, s=1.0):
    if a <= 0.01: return
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 30 * s], fill=A(col, a))
    for sg in (1, -1): d.line([(cx - 12 * s, cy - 12 * s * sg), (cx + 12 * s, cy + 12 * s * sg)], fill=A(WHITE, a), width=int(7 * s))
def badge(d, cx, cy, letter, col, a, r=46):
    if a <= 0.01: return
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A(col, a), outline=A(WHITE, a), width=4)
    d.text((cx, cy + 2), letter, font=O(int(r * 1.3)), fill=A(NAVY, a), anchor="mm")

# ---------------------------------------------------------------- hull cross-section (V-hull, transom view)
def hull_pts(cx, cy, s=1.0, deadrise=0.34):
    w, h = 300 * s, 230 * s
    return [(cx - w, cy - h * 0.55), (cx - w * 0.96, cy + h * 0.05), (cx - w * 0.55, cy + h * 0.30 - deadrise * 10 * s),
            (cx, cy + h * 0.55), (cx + w * 0.55, cy + h * 0.30 - deadrise * 10 * s), (cx + w * 0.96, cy + h * 0.05), (cx + w, cy - h * 0.55)]
def hull_glass(d, cx, cy, s, a, cut=1.0):
    p = hull_pts(cx, cy, s); d.line(p, fill=A(AMBER, a), width=int(26 * s), joint="curve")
    d.line(p, fill=A(CREAM, a), width=int(8 * s), joint="curve")
    for i in range(len(p) - 1):   # woven texture dots
        (x0, y0), (x1, y1) = p[i], p[i + 1]
        for k in range(6):
            u = (k + 0.5) / 6; d.ellipse([lerp(x0, x1, u) - 3, lerp(y0, y1, u) - 3, lerp(x0, x1, u) + 3, lerp(y0, y1, u) + 3], fill=A(RESIN, a))
def hull_alu(d, cx, cy, s, a, seams=1.0, glow=0.0):
    p = hull_pts(cx, cy, s, deadrise=0.1)
    d.line(p, fill=A(STEEL, a), width=int(22 * s), joint="curve"); d.line(p, fill=A(SILVER, a), width=int(10 * s), joint="curve")
    for i in (1, 3, 5):
        x, y = p[i]; r = 11 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=A(mix(SILVER, (255, 200, 90), glow), a * seams))
def water(d, y, a, t, amp=6, col=SEA):
    pts = [(x, y + amp * math.sin(x / 70 + t * 2.2)) for x in range(-20, W + 40, 20)]
    d.polygon(pts + [(W + 40, 1330), (-20, 1330)], fill=A(col, 0.55 * a))
    d.line(pts, fill=A((150, 220, 240), 0.9 * a), width=4)

# ---------------------------------------------------------------- clips
def f_vs(t):     # hook support "Fibreglass or aluminium. Which hull would you own in the Red Sea?"
    im, d = new(t); a = fin(t, 0.0, 0.4); b = fin(t, 0.35, 0.4)
    d.line([(540, 640), (540, 1290)], fill=A(WHITE, 0.25 * a), width=3)
    hull_glass(d, 270, 980 + (1 - a) * 60, 0.72, a); hull_alu(d, 810, 980 + (1 - b) * 60, 0.72, b, glow=0.5 + 0.5 * math.sin(t * 5))
    badge(d, 270, 760, "A", GOLD, a); badge(d, 810, 760, "B", TURQ, b)
    label(d, 270, 1190, "FIBREGLASS", a, AMBER, 38); label(d, 810, 1190, "ALUMINIUM", b, SILVER, 38)
    v = fin(t, 0.8, 0.3); r = 58 * (0.6 + 0.4 * v)
    d.ellipse([540 - r, 760 - r, 540 + r, 760 + r], fill=A(RED, v), outline=A(WHITE, v), width=5)
    d.text((540, 762), "VS", font=O(int(r * 0.95)), fill=A(WHITE, v), anchor="mm")
    return im

def f_layup(t):  # "Fibreglass is glass fibres locked in hard resin, moulded into almost any shape."  (5.9 s)
    im, d = new(t); title(d, "A · FIBREGLASS", "GLASS + RESIN", t, GOLD)
    # 1) woven glass mat (0-1.8 s)
    a1 = fin(t, 0.2, 0.5); cx, cy, ww, hh = 540, 830, 640, 210
    sh = ease((t - 3.3) / 1.2)   # morph flat sheet -> curved hull
    def sheet_y(x, layer):
        u = (x - (cx - ww / 2)) / ww; bend = 230 * sh * (1 - (2 * u - 1) ** 2)
        return cy + layer * 22 + bend
    if a1 > 0.01:
        for layer in range(3):
            la = a1 * fin(t, 0.2 + layer * 0.35, 0.4)
            pts = [(x, sheet_y(x, layer)) for x in range(cx - ww // 2, cx + ww // 2 + 1, 16)]
            d.line(pts, fill=A(CREAM, la), width=16)
            for i, (x, y) in enumerate(pts):
                if i % 2 == 0: d.line([(x - 6, y - 7), (x + 6, y + 7)], fill=A((170, 160, 140), la), width=2)
                else: d.line([(x - 6, y + 7), (x + 6, y - 7)], fill=A((170, 160, 140), la), width=2)
        label(d, cx - ww / 2 - 10, cy - 70, "GLASS-FIBRE MAT", a1 * (1 - sh), CREAM, 30, "lm")
    # 2) resin pours and soaks (1.8-3.3 s)
    r = ease((t - 1.8) / 1.3)
    if r > 0.01:
        for k in range(5):
            x = cx - 240 + k * 120; yb = sheet_y(x, 0) - 26
            ytop = 600; ycur = lerp(ytop, yb, clamp(r * 1.6 - k * 0.12))
            if r < 0.95: d.line([(x, ytop), (x, ycur)], fill=A(RESIN, 0.85 * (1 - sh)), width=10)
            d.ellipse([x - 8, ycur - 8, x + 8, ycur + 8], fill=A(RESIN, 0.85 * (1 - sh)))
        pts = [(x, sheet_y(x, 1)) for x in range(cx - ww // 2, cx + ww // 2 + 1, 16)]
        d.line(pts, fill=A(AMBER, 0.75 * r), width=int(64 * r) or 1, joint="curve")
        label(d, cx + ww / 2 + 10, cy - 70, "+ RESIN", r * (1 - sh), AMBER, 34, "rm")
    # 3) moulded into a curved hull (3.3-5.9 s)
    if sh > 0.01:
        mp = [(x, sheet_y(x, 2) + 40) for x in range(cx - ww // 2 - 40, cx + ww // 2 + 41, 16)]
        d.line(mp, fill=A((90, 96, 110), sh), width=22, joint="curve")
        label(d, cx - ww / 2 - 40, sheet_y(cx - ww / 2, 2) - 50, "MOULD", fin(t, 4.3, 0.4), (190, 196, 210), 32, "lm")
        label(d, cx, 1225, "ALMOST ANY SHAPE", fin(t, 4.4, 0.4), GOLD, 46)
    return im

def f_gpros(t):  # "Sleek curves, a quiet ride, and it can't rust."  (3.0 s)
    im, d = new(t); title(d, "A · FIBREGLASS", "WHY MOST YACHTS USE IT", t, GOLD)
    items = [("SLEEK CURVES", 0.25), ("QUIET RIDE", 1.05), ("CAN'T RUST", 1.85)]
    card(d, (120, 650, 960, 1240), fin(t, 0.05, 0.3), GOLD)
    for i, (s, t0) in enumerate(items):
        y = 760 + i * 170; a = fin(t, t0, 0.3)
        tick(d, 220, y, a, s=1.2 if a < 1 else 1.0); label(d, 290, y, s, a, WHITE, 54, "lm")
    return im

def f_gcons(t):  # "The catch? It's heavier, and a hard hit can crack it. Over years, water can also seep in and cause blisters." (7.3 s)
    im, d = new(t); title(d, "A · FIBREGLASS", "THE CATCH", t, RED)
    ph1 = clamp(1 - fin(t, 2.0, 0.3)); ph2 = fin(t, 2.0, 0.3) * clamp(1 - fin(t, 3.9, 0.3)); ph3 = fin(t, 3.9, 0.3)
    if ph1 > 0.01:   # balance scale: fibreglass sample heavier
        tilt = 0.16 * ease((t - 0.5) / 0.8); cx, cy = 540, 830
        d.polygon([(cx - 40, 1180), (cx + 40, 1180), (cx, 860)], fill=A((90, 96, 110), ph1))
        dx, dy = 300 * math.cos(tilt), 300 * math.sin(tilt)
        L, R = (cx - dx, cy + dy), (cx + dx, cy - dy)
        d.line([L, R], fill=A(SILVER, ph1), width=12)
        for (px, py), col, lab in ((L, AMBER, "A"), (R, SILVER, "B")):
            d.line([(px, py), (px, py + 120)], fill=A(SILVER, ph1), width=4)
            d.rounded_rectangle([px - 95, py + 120, px + 95, py + 140], radius=8, fill=A((90, 96, 110), ph1))
            hgt = 110 if lab == "A" else 70
            d.rounded_rectangle([px - 70, py + 120 - hgt, px + 70, py + 118], radius=10, fill=A(col, ph1))
            d.text((px, py + 120 - hgt / 2), lab, font=O(52), fill=A(NAVY, ph1), anchor="mm")
        label(d, 540, 1240, "HEAVIER", fin(t, 0.9, 0.3) * ph1, AMBER, 56)
    if ph2 > 0.01:   # impact -> crack
        y0 = 940; d.rectangle([140, y0, 940, y0 + 70], fill=A(AMBER, ph2)); d.rectangle([140, y0, 940, y0 + 14], fill=A(CREAM, ph2))
        rk = ease((t - 2.2) / 0.5); ry = lerp(620, y0 - 70, rk)
        d.polygon([(470, ry), (560, ry - 40), (630, ry + 10), (600, ry + 70), (500, ry + 66)], fill=A((110, 100, 92), ph2))
        c = ease((t - 2.7) / 0.6)
        if c > 0:
            rnd = random.Random(3)
            for k in range(7):
                ang = math.pi * (0.1 + 0.8 * k / 6); ln = c * rnd.uniform(90, 200); x, y = 550, y0 + 6; pts = [(x, y)]
                for s in range(5):
                    x += math.cos(ang) * ln / 5 + rnd.uniform(-10, 10); y += abs(math.sin(ang)) * ln / 12 + rnd.uniform(0, 6); pts.append((x, y))
                d.line(pts, fill=A(INK, ph2), width=5)
            fl = clamp(1 - (t - 2.7) / 0.3); d.ellipse([550 - 90, y0 - 90, 550 + 90, y0 + 90], outline=A(WHITE, fl * ph2), width=6)
        label(d, 540, 1160, "A HARD HIT CAN CRACK IT", fin(t, 2.8, 0.3) * ph2, RED, 48)
    if ph3 > 0.01:   # magnified laminate: water seeps -> osmosis blisters
        x0, x1, y0 = 120, 960, 790
        d.rectangle([x0, 640, x1, y0], fill=A(SEA, 0.6 * ph3)); label(d, 150, 680, "SEA WATER", ph3, (190, 235, 250), 34, "lm")
        d.rectangle([x0, y0, x1, y0 + 26], fill=A(CREAM, ph3)); label(d, 150, y0 + 62, "GELCOAT (OUTER SKIN)", ph3, CREAM, 30, "lm")
        d.rectangle([x0, y0 + 26, x1, y0 + 330], fill=A(AMBER, ph3))
        for yy in range(y0 + 50, y0 + 330, 40): d.line([(x0, yy), (x1, yy)], fill=A(RESIN, ph3), width=3)
        label(d, 540, y0 + 210, "GLASS + RESIN LAMINATE", ph3, WHITE, 34)
        tt = t - 3.9; rnd = random.Random(7)
        for k in range(14):
            x = rnd.uniform(x0 + 40, x1 - 40); st = rnd.uniform(0, 1.2); u = clamp((tt - st) / 1.4)
            if 0 < u < 1: d.ellipse([x - 7, lerp(700, y0 + 60, u) - 7, x + 7, lerp(700, y0 + 60, u) + 7], fill=A((140, 215, 245), ph3))
        for k, bx in enumerate((300, 520, 760)):
            g = ease((tt - 1.3 - k * 0.3) / 1.0); r = 46 * g
            if r > 1:
                d.chord([bx - r, y0 - r * 0.9, bx + r, y0 + r * 0.9], 180, 360, fill=A(CREAM, ph3), outline=A((200, 180, 140), ph3), width=3)
                d.ellipse([bx - r * 0.6, y0 + 6, bx + r * 0.6, y0 + 26 + r * 0.3], fill=A(SEA, 0.8 * ph3))
        label(d, 540, 1200, "OSMOSIS BLISTERS", fin(t, 5.0, 0.3) * ph3, AMBER, 54)
        label(d, 540, 1262, "(OVER MANY YEARS)", fin(t, 5.2, 0.3) * ph3, CREAM, 30)
    return im

def f_weld(t):   # "...welded together. It's lighter, so it needs less power." (3.8 s, follows welding footage)
    im, d = new(t); title(d, "B · ALUMINIUM", "WELDED METAL PLATES", t, TURQ)
    ph1 = clamp(1 - fin(t, 1.7, 0.3)); ph2 = fin(t, 1.7, 0.3)
    if ph1 > 0.01:
        sl = ease(t / 0.7); y0 = 820
        d.rectangle([140 - (1 - sl) * 300, y0, 538, y0 + 120], fill=A(SILVER, ph1)); d.rectangle([542, y0, 940 + (1 - sl) * 300, y0 + 120], fill=A(SILVER, ph1))
        for x in range(150, 940, 18): d.line([(x, y0 + 4), (x + 30, y0 + 116)], fill=A((230, 236, 244), 0.25 * ph1), width=2)
        w = ease((t - 0.7) / 0.9); yw = y0 + 120 * w
        d.line([(540, y0), (540, yw)], fill=A((255, 196, 90), ph1), width=14)
        if 0 < w < 1:
            rnd = random.Random(int(t * 30))
            for k in range(16):
                ang = rnd.uniform(0, 6.28); ln = rnd.uniform(20, 90)
                d.line([(540, yw), (540 + math.cos(ang) * ln, yw + math.sin(ang) * ln)], fill=A((255, 230, 150), ph1), width=3)
            d.ellipse([540 - 30, yw - 30, 540 + 30, yw + 30], fill=A((255, 250, 220), 0.9 * ph1))
        label(d, 540, 1080, "WELD SEAM", fin(t, 1.0, 0.3) * ph1, GOLD, 40)
    if ph2 > 0.01:   # lighter -> less power: two hulls on water, B rides higher, smaller engine gauge
        tt = t - 1.7
        water(d, 1000, ph2, t)
        hull_glass(d, 290, 960, 0.5, ph2); hull_alu(d, 790, 925, 0.5, ph2)
        badge(d, 290, 760, "A", GOLD, ph2, 38); badge(d, 790, 760, "B", TURQ, ph2, 38)
        f = fin(tt, 0.3, 0.4)
        d.polygon([(790 - 40, 700), (790 + 40, 700), (790, 650)], fill=A(GREEN, f))
        label(d, 790, 1180, "LIGHTER", f, TURQ, 52); label(d, 790, 1240, "LESS POWER NEEDED", fin(tt, 0.9, 0.4), WHITE, 32)
    return im

def f_dent(t):   # "And it's tough. A rock often leaves a dent, not a crack." (3.7 s)
    im, d = new(t); title(d, "B · ALUMINIUM", "TOUGH", t, TURQ)
    y0 = 960; hit = ease((t - 0.9) / 0.35); dent = hit * 46
    pts_top = [(x, y0 + dent * math.exp(-((x - 540) / 90) ** 2)) for x in range(140, 941, 10)]
    pts_bot = [(x, y + 60) for x, y in pts_top[::-1]]
    d.polygon(pts_top + pts_bot, fill=A(SILVER, 1))
    d.line(pts_top, fill=A((240, 244, 250), 1), width=4)
    for x in range(160, 940, 22): d.line([(x, y0 + 8 + dent * math.exp(-((x - 540) / 90) ** 2)), (x + 18, y0 + 52 + dent * math.exp(-((x - 540) / 90) ** 2))], fill=A((150, 160, 172), 0.5), width=2)
    rk = ease(t / 0.9); bounce = 60 * ease((t - 1.25) / 0.6)
    ry = lerp(600, y0 - 72, rk) - bounce
    d.polygon([(470, ry), (560, ry - 40), (630, ry + 10), (600, ry + 70), (500, ry + 66)], fill=A((110, 100, 92), 1))
    fl = clamp(1 - (t - 1.2) / 0.3) if t > 1.2 else 0
    d.ellipse([540 - 100, y0 - 80, 540 + 100, y0 + 120], outline=A(WHITE, fl), width=6)
    a = fin(t, 1.6, 0.3)
    tick(d, 330, 1180, a); label(d, 380, 1180, "DENT", a, WHITE, 50, "lm")
    b = fin(t, 2.1, 0.3)
    cross(d, 650, 1180, b, RED); label(d, 700, 1180, "CRACK", b, (200, 200, 210), 50, "lm")
    if b > 0.5: d.line([(690, 1182), (880, 1182)], fill=A(RED, b), width=6)
    return im

def f_acons(t):  # "But it's noisier in a chop, it gets hot in our sun, and in salt water it needs anodes and correct wiring to stop corrosion." (8.7 s)
    im, d = new(t); title(d, "B · ALUMINIUM", "THE CATCH", t, RED)
    ph1 = clamp(1 - fin(t, 1.6, 0.3)); ph2 = fin(t, 1.6, 0.3) * clamp(1 - fin(t, 3.2, 0.3)); ph3 = fin(t, 3.2, 0.3)
    if ph1 > 0.01:   # chop slaps the hull -> sound waves
        water(d, 1010, ph1, t * 2.0, amp=26)
        bob = 18 * math.sin(t * 7); hull_alu(d, 540, 930 + bob, 0.62, ph1)
        for k in range(3):
            ph = (t * 1.6 + k / 3) % 1
            for sgn in (-1, 1):
                d.arc([540 + sgn * 230 - 60 - ph * 150, 900 - 60 - ph * 150, 540 + sgn * 230 + 60 + ph * 150, 900 + 60 + ph * 150],
                      (-50 if sgn > 0 else 130), (50 if sgn > 0 else 230), fill=A(GOLD, ph1 * (1 - ph)), width=7)
        label(d, 540, 1220, "NOISIER IN A CHOP", fin(t, 0.3, 0.3) * ph1, GOLD, 52)
    if ph2 > 0.01:   # sun heats the metal deck
        tt = t - 1.6; cx, cy = 300, 760
        for k in range(12):
            ang = k * math.pi / 6 + tt * 0.6
            d.line([(cx + math.cos(ang) * 95, cy + math.sin(ang) * 95), (cx + math.cos(ang) * 140, cy + math.sin(ang) * 140)], fill=A(GOLD, ph2), width=9)
        d.ellipse([cx - 75, cy - 75, cx + 75, cy + 75], fill=A((255, 206, 90), ph2))
        heat = ease(tt / 1.3)
        d.rounded_rectangle([140, 1010, 940, 1070], radius=10, fill=A(mix(SILVER, (255, 120, 60), heat * 0.8), ph2))
        for k in range(5):
            x = 260 + k * 140; o = (tt * 60 + k * 20) % 60
            d.line([(x, 990 - o), (x + 14, 960 - o), (x - 6, 930 - o), (x + 8, 900 - o)], fill=A((255, 160, 90), ph2 * heat), width=5, joint="curve")
        tx = 760; d.rounded_rectangle([tx - 22, 660, tx + 22, 900], radius=22, outline=A(WHITE, ph2), width=6)
        lvl = lerp(860, 690, heat); d.rounded_rectangle([tx - 10, lvl, tx + 10, 890], radius=10, fill=A(RED, ph2))
        d.ellipse([tx - 36, 870, tx + 36, 942], fill=A(RED, ph2))
        label(d, 540, 1200, "HOT IN OUR SUN", fin(tt, 0.3, 0.3) * ph2, (255, 170, 90), 54)
    if ph3 > 0.01:   # galvanic corrosion: needs anodes + correct wiring
        tt = t - 3.2
        d.rectangle([120, 940, 960, 1290], fill=A(SEA, 0.55 * ph3)); label(d, 870, 1260, "SALT WATER", ph3, (170, 230, 250), 24)
        d.rectangle([180, 900, 600, 960], fill=A(SILVER, ph3)); label(d, 390, 870, "HULL", ph3, SILVER, 30)
        an = fin(tt, 0.6, 0.4)
        d.rounded_rectangle([700, 990, 860, 1060], radius=14, fill=A((150, 156, 150), an)); label(d, 780, 1095, "ANODE", an, GOLD, 30)
        d.line([(600, 930), (780, 930), (780, 990)], fill=A(GOLD, an), width=6)
        # current dots flowing hull -> anode through the water
        if an > 0.5:
            for k in range(8):
                u = ((tt * 0.6) + k / 8) % 1; x = lerp(560, 760, u); y = 990 + 40 * math.sin(u * math.pi)
                d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=A((255, 220, 120), ph3))
        # wiring
        wr = fin(tt, 2.0, 0.4)
        d.line([(260, 900), (260, 790), (430, 790)], fill=A(GREEN, wr), width=6); d.rounded_rectangle([430, 760, 560, 820], radius=10, fill=A(GREEN, wr))
        d.text((495, 791), "WIRING", font=M(800, 24), fill=A(NAVY, wr), anchor="mm")
        tick(d, 610, 790, wr, GREEN, 0.8)
        label(d, 540, 640, "NEEDS ANODES +", fin(tt, 0.7, 0.3), WHITE, 46)
        label(d, 540, 700, "CORRECT WIRING", fin(tt, 2.0, 0.3), GREEN, 46)
        label(d, 540, 1200, "TO STOP CORROSION", fin(tt, 3.4, 0.3), GOLD, 50)
    return im

def f_verdict(t):  # "For cruising comfort, most owners pick fibreglass. For workboats, tenders and rocky shallows, aluminium shines." (7.8 s)
    im, d = new(t); title(d, "THE VERDICT", None, t, GOLD, y=470)
    rows = [("SHAPE & FINISH", "A"), ("QUIET RIDE", "A"), ("NO CORROSION", "A"), ("LIGHT WEIGHT", "B"), ("TAKES KNOCKS", "B")]
    card(d, (90, 540, 990, 1060), fin(t, 0.0, 0.3), GOLD)
    badge(d, 700, 595, "A", GOLD, fin(t, 0.1, 0.3), 32); badge(d, 880, 595, "B", TURQ, fin(t, 0.1, 0.3), 32)
    for i, (s, win) in enumerate(rows):
        y = 680 + i * 82; a = fin(t, 0.2 + i * 0.25, 0.3)
        label(d, 130, y, s, a, WHITE, 34, "lm")
        if win == "A": tick(d, 700, y, a, GOLD, 0.8)
        else: tick(d, 880, y, a, TURQ, 0.8)
        if i < len(rows) - 1: d.line([(130, y + 41), (950, y + 41)], fill=A(WHITE, 0.12 * a), width=2)
    a1 = fin(t, 2.2, 0.4)
    d.rounded_rectangle([90, 1090, 535, 1290], radius=22, fill=A((60, 46, 20), 0.95 * a1), outline=A(GOLD, a1), width=4)
    label(d, 312, 1140, "CRUISING", a1, WHITE, 34); label(d, 312, 1185, "COMFORT", a1, WHITE, 34)
    badge(d, 312, 1250, "A", GOLD, a1, 30)
    a2 = fin(t, 4.4, 0.4)
    d.rounded_rectangle([545, 1090, 990, 1290], radius=22, fill=A((12, 52, 60), 0.95 * a2), outline=A(TURQ, a2), width=4)
    label(d, 767, 1130, "WORKBOATS,", a2, WHITE, 28); label(d, 767, 1166, "TENDERS,", a2, WHITE, 28); label(d, 767, 1202, "ROCKY SHALLOWS", a2, WHITE, 28)
    badge(d, 767, 1253, "B", TURQ, a2, 28)
    return im

def f_cta(t):    # "Which would you own, A or B? Tell us in the comments." (3.4 s)
    im, d = new(t)
    a = fin(t, 0.0, 0.35); b = fin(t, 0.25, 0.35)
    label(d, 540, 640, "WHICH WOULD", a, WHITE, 74); label(d, 540, 730, "YOU OWN?", a, WHITE, 74)
    pulse = 1 + 0.06 * math.sin(t * 6)
    badge(d, 330, 950, "A", GOLD, a, int(110 * pulse)); badge(d, 750, 950, "B", TURQ, b, int(110 * (2 - pulse)))
    label(d, 330, 1100, "FIBREGLASS", a, AMBER, 36); label(d, 750, 1100, "ALUMINIUM", b, SILVER, 36)
    pill(d, 540, 1230, "COMMENT  A  OR  B", M(800, 40), GOLD, NAVY, fin(t, 0.9, 0.35), h=80)
    return im

CLIPS = {"vs": (f_vs, 2.5), "layup": (f_layup, 6.4), "gpros": (f_gpros, 3.5), "gcons": (f_gcons, 7.8), "weld": (f_weld, 4.3),
         "dent": (f_dent, 4.2), "acons": (f_acons, 9.2), "verdict": (f_verdict, 8.3), "cta": (f_cta, 3.9)}

def render(outdir, name):
    fn, dur = CLIPS[name]; out = os.path.join(outdir, f"hull_{name}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)): p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait(); print("->", out)

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == "--still":
        nm = sys.argv[3]
        for tt in sys.argv[4:]: CLIPS[nm][0](float(tt)).convert("RGB").save(os.path.join(outdir, f"still_{nm}_{tt}.png"))
    else:
        for nm in (sys.argv[2:] or CLIPS): render(outdir, nm)
