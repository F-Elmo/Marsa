"""Animated 'power schematic' diagrams for ep 016 (generator vs lithium house bank). 1080x1920@30 MP4s.
  python3 engine/v2/power_anim.py OUTDIR [name ...]        names: gen, soot, lith, ac, verdict
  python3 engine/v2/power_anim.py OUTDIR --still name t     (single PNG for checking)
Look (new for ep 016): night-sky schematic board - glowing component boxes joined by wires with moving energy dashes."""
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
CORAL = (240, 90, 80); AMBER = (245, 170, 40); GREEN = (60, 205, 130); ICE = (170, 230, 255); SOOT = (25, 25, 28)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def fin(t, t0, d=0.35): return ease((t - t0) / d)

# ---------------------------------------------------------------- background: night sky + faint schematic grid
def _bg():
    y = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array((10, 20, 50)) * (1 - y) + np.array((3, 9, 24)) * y).repeat(W, 1).astype(np.uint8)
    im = Image.fromarray(arr); d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 60): d.line([(x, 480), (x, 1330)], fill=(60, 120, 180, 18), width=1)
    for yy in range(480, 1331, 60): d.line([(0, yy), (W, yy)], fill=(60, 120, 180, 18), width=1)
    rnd = random.Random(16)
    for _ in range(70):
        x, yy, r = rnd.randint(0, W), rnd.randint(260, 1300), rnd.choice([1, 1, 2])
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=(220, 235, 255, rnd.randint(40, 120)))
    a = np.zeros((H, W), np.uint8); a[1330:1450] = np.linspace(0, 255, 120).astype(np.uint8)[:, None]; a[1450:] = 255
    im.paste(Image.new("RGB", (W, H), (3, 9, 24)), (0, 0), Image.fromarray(a))   # calm caption zone
    return im
BG = _bg()

def new(): im = BG.copy(); return im, ImageDraw.Draw(im, "RGBA")

def pill(d, cx, cy, s, f, bg, fg, a=1.0, padx=26, h=None):
    if a <= 0.01: return
    tw = f.getlength(s); h = h or int(f.size * 1.75)
    cx = clamp(cx, 40 + tw / 2 + padx, W - 40 - tw / 2 - padx)
    d.rounded_rectangle([cx - tw / 2 - padx, cy - h / 2, cx + tw / 2 + padx, cy + h / 2], radius=h // 2, fill=A(bg, 0.96 * a))
    d.text((cx, cy + 1), s, font=f, fill=A(fg, a), anchor="mm")

def title(d, tag, line, t, col=GOLD, y=330):
    a = fin(t, 0, 0.4)
    pill(d, W / 2, y, tag, M(800, 32), col, NAVY, a, h=58)
    if line:
        f = O(70)
        while f.getlength(line) > 980: f = O(f.size - 4)
        d.text((W / 2, y + 92 + (1 - a) * 30), line, font=f, fill=A(WHITE, a), anchor="mm", stroke_width=4, stroke_fill=A((3, 9, 24), a))

def box(d, r, col, a, fill=(12, 30, 66), rad=22, w=5):
    if a <= 0.01: return
    x0, y0, x1, y1 = r
    for k in (14, 8):  # glow
        d.rounded_rectangle([x0 - k, y0 - k, x1 + k, y1 + k], radius=rad + k, outline=A(col, 0.07 * a), width=k)
    d.rounded_rectangle(r, radius=rad, fill=A(fill, 0.95 * a), outline=A(col, a), width=w)

def label(d, x, y, s, a, col=WHITE, sz=30, anchor="mm"):
    if a > 0.01: d.text((x, y), s, font=M(800, sz), fill=A(col, a), anchor=anchor, stroke_width=3, stroke_fill=A((3, 9, 24), a))

def path_pts(pts, n):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; L = sum(seg); out = []
    for k in range(n):
        s = L * k / n; i = 0
        while i < len(seg) - 1 and s > seg[i]: s -= seg[i]; i += 1
        f = s / seg[i] if seg[i] else 0
        out.append((lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)))
    return out, L

def wire(d, pts, t, col, a, flow=1.0, speed=220, gap=46, grow=1.0):
    """Wire drawn (grow 0..1 of its length), with energy dashes moving along it when flow>0."""
    if a <= 0.01: return
    seg_pts, L = path_pts(pts, 400)
    upto = max(2, int(len(seg_pts) * clamp(grow)))
    d.line(seg_pts[:upto], fill=A((40, 70, 110), a), width=12, joint="curve")
    d.line(seg_pts[:upto], fill=A(col, 0.35 * a), width=4, joint="curve")
    if flow > 0.01 and grow >= 1:
        off = (t * speed) % gap; s = off
        while s < L:
            p = seg_pts[int(s / L * 399)]
            d.ellipse([p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8], fill=A(col, flow * a))
            s += gap

def sound_arcs(d, cx, cy, t, a, col=AMBER, n=3, rmax=150, side=0):
    for k in range(n):
        ph = ((t * 0.9 + k / n) % 1.0); r = 40 + ph * rmax; al = a * (1 - ph) * 0.8
        d.arc([cx - r, cy - r, cx + r, cy + r], side - 40, side + 40, fill=A(col, al), width=6)

def puffs(d, x, y, t, a, dark=0.0):
    for k in range(5):
        ph = (t * 0.6 + k / 5) % 1.0; r = 14 + ph * 46
        g = int(lerp(150, 60, dark))
        d.ellipse([x - r - ph * 40, y - r - ph * 160, x + r - ph * 40, y + r - ph * 160], fill=(g, g, g + 8, int(a * 110 * (1 - ph))))

# ---------------------------------------------------------------- component icons
def generator(d, r, t, a, spin=1.0):
    x0, y0, x1, y1 = r
    box(d, r, GOLD, a)
    if a <= 0.01: return
    # engine block (left) with cooling fins
    ex1 = x0 + (x1 - x0) * 0.55
    d.rounded_rectangle([x0 + 28, y0 + 50, ex1, y1 - 40], radius=12, fill=A((70, 84, 104), a), outline=A((150, 170, 195), a), width=3)
    for k in range(5):
        yy = y0 + 70 + k * ((y1 - y0 - 130) / 4)
        d.line([(x0 + 40, yy), (ex1 - 12, yy)], fill=A((40, 52, 70), a), width=6)
    # flywheel + alternator drum (right)
    cx, cy, R = (ex1 + x1) / 2 + 6, (y0 + y1) / 2 + 5, (x1 - ex1) * 0.36
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=A((30, 50, 84), a), outline=A(GOLD, a), width=5)
    ang = t * 9 * spin
    for k in range(3):
        th = ang + k * 2 * math.pi / 3
        d.line([(cx, cy), (cx + R * 0.85 * math.cos(th), cy + R * 0.85 * math.sin(th))], fill=A(GOLD, a), width=7)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=A(WHITE, a))
    # shaking a little while running
    return (cx, cy)

def battery_bank(d, r, t, a, level, col=TURQ):
    x0, y0, x1, y1 = r
    box(d, r, col, a)
    if a <= 0.01: return
    n = 4; gw = (x1 - x0 - 50) / n
    for k in range(n):
        cx0 = x0 + 25 + k * gw + 6; cx1 = cx0 + gw - 12; cy0 = y0 + 60; cy1 = y1 - 30
        d.rounded_rectangle([cx0 + (cx1 - cx0) * 0.3, cy0 - 14, cx1 - (cx1 - cx0) * 0.3, cy0], radius=4, fill=A((150, 170, 195), a))
        d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=8, outline=A((150, 170, 195), a), width=3, fill=A((8, 20, 44), a))
        lv = clamp(level); fy = cy1 - 6 - (cy1 - cy0 - 12) * lv
        c = col if lv > 0.25 else CORAL
        if lv > 0.01: d.rounded_rectangle([cx0 + 6, fy, cx1 - 6, cy1 - 6], radius=5, fill=A(c, 0.9 * a))
    label(d, (x0 + x1) / 2, y0 + 30, f"{int(round(clamp(level) * 100))}%", a, col=WHITE, sz=28)

def inverter(d, r, t, a, morph):
    x0, y0, x1, y1 = r
    box(d, r, ICE, a)
    if a <= 0.01: return
    cy = (y0 + y1) / 2 + 14; xm = (x0 + x1) / 2
    d.line([(x0 + 22, cy), (xm - 12, cy)], fill=A(TURQ, a), width=6)                      # DC: flat line
    pts = [(xm + 12 + i, cy - 34 * morph * math.sin((i / (x1 - 22 - xm - 12)) * 4 * math.pi + t * 6)) for i in range(0, int(x1 - 22 - xm - 12), 3)]
    d.line(pts, fill=A(GOLD, a), width=6)                                                    # AC: sine
    label(d, (x0 + xm) / 2, y0 + 30, "DC", a, col=TURQ, sz=24); label(d, (xm + x1) / 2, y0 + 30, "AC", a, col=GOLD, sz=24)

def ac_unit(d, cx, cy, t, a, on, s=1.0):
    if a <= 0.01: return
    w, h = 190 * s, 96 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=14, fill=A((230, 238, 246), a), outline=A(ICE, a), width=4)
    for k in range(3): d.line([(cx - w / 2 + 22, cy + 6 + k * 13 * s), (cx + w / 2 - 22, cy + 6 + k * 13 * s)], fill=A((120, 140, 165), a), width=3)
    d.ellipse([cx + w / 2 - 34, cy - h / 2 + 14, cx + w / 2 - 22, cy - h / 2 + 26], fill=A(GREEN if on > 0.5 else (120, 120, 120), a))
    if on > 0.01:
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1.0; yy = cy + h / 2 + 12 + ph * 80 * s
            pts = [(cx - w / 2 + 20 + i, yy + 7 * math.sin(i / 18 + t * 4)) for i in range(0, int(w - 40), 4)]
            d.line(pts, fill=A(ICE, on * a * (1 - ph)), width=5)

def fridge(d, cx, cy, a, on):
    if a <= 0.01: return
    d.rounded_rectangle([cx - 55, cy - 85, cx + 55, cy + 85], radius=12, fill=A((230, 238, 246), a), outline=A(ICE, a), width=4)
    d.line([(cx - 55, cy - 20), (cx + 55, cy - 20)], fill=A((120, 140, 165), a), width=4)
    d.line([(cx + 35, cy - 60), (cx + 35, cy - 35)], fill=A((90, 110, 140), a), width=6)
    d.line([(cx + 35, cy), (cx + 35, cy + 45)], fill=A((90, 110, 140), a), width=6)
    if on > 0.01: label(d, cx - 12, cy - 52, "*", a * on, col=TURQ, sz=40)

def bulb(d, cx, cy, a, on):
    if a <= 0.01: return
    for k in range(4, 0, -1):
        r = 40 + k * 16; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A(AMBER, 0.06 * on * a))
    c = tuple(int(lerp(x, y, on)) for x, y in zip((120, 120, 130), (255, 214, 120)))
    d.ellipse([cx - 42, cy - 46, cx + 42, cy + 38], fill=A(c, a))
    d.rectangle([cx - 20, cy + 34, cx + 20, cy + 66], fill=A((170, 180, 195), a))

def fan(d, cx, cy, t, a, on):
    if a <= 0.01: return
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=A(ICE, a), width=4, fill=A((12, 30, 66), a))
    ang = t * 12 * on
    for k in range(3):
        th = ang + k * 2 * math.pi / 3
        pts = [(cx, cy), (cx + 58 * math.cos(th - 0.35), cy + 58 * math.sin(th - 0.35)), (cx + 58 * math.cos(th + 0.25), cy + 58 * math.sin(th + 0.25))]
        d.polygon(pts, fill=A(WHITE, a))
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=A(GOLD, a))

def moon(d, cx, cy, a):
    if a <= 0.01: return
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=A((245, 236, 200), a))
    d.ellipse([cx - 22, cy - 58, cx + 66, cy + 30], fill=A((10, 20, 50), a))

def sun(d, cx, cy, a):
    if a <= 0.01: return
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=A((255, 170, 80), a))
    for k in range(8):
        th = k * math.pi / 4
        d.line([(cx + 60 * math.cos(th), cy + 60 * math.sin(th)), (cx + 80 * math.cos(th), cy + 80 * math.sin(th))], fill=A((255, 170, 80), a), width=6)

# ---------------------------------------------------------------- clips
def f_gen(t):
    im, d = new(); title(d, "A: GENERATOR", "POWER ON DEMAND", t)
    a = fin(t, 0.3, 0.5); run = fin(t, 0.9, 0.6)
    shake = 3 * run * math.sin(t * 60)
    G = (90, 700 + shake, 520, 960 + shake)
    puffs(d, 150, 680, t, a * run)
    generator(d, G, t, a, spin=run)
    sound_arcs(d, 520, 830, t, a * run, side=0); sound_arcs(d, 90, 830, t, a * run, side=180)
    label(d, 210, 1000, "DIESEL ENGINE", fin(t, 1.4), col=GOLD, sz=30)
    label(d, 420, 645, "ALTERNATOR", fin(t, 2.4), col=GOLD, sz=30)
    d.line([(420, 668), (420, 712)], fill=A(GOLD, fin(t, 2.4)), width=3)
    # wires to loads
    flow = fin(t, 4.0, 0.4); grow = fin(t, 3.4, 0.6)
    bus = [(520, 830), (640, 830)]
    wire(d, bus, t, GOLD, a, flow, grow=grow)
    loads = [(860, 600), (860, 830), (860, 1080)]
    for k, (lx, ly) in enumerate(loads):
        wire(d, [(640, 830), (640, ly), (lx - 120, ly)], t, GOLD, a, flow, grow=grow)
    on = [fin(t, 4.4 + 0.4 * k) for k in range(3)]
    ac_unit(d, 860, 580, t, a, on[0]); fridge(d, 860, 830, a, on[1]); bulb(d, 860, 1070, a, on[2])
    pill(d, 540, 1240, "AIR-CON  •  FRIDGE  •  LIGHTS", M(800, 30), GOLD, NAVY, fin(t, 5.4), h=60)
    return im

def f_soot(t):
    im, d = new(); title(d, "LIGHT LOAD FOR HOURS", "WHAT IT DOES INSIDE", t, col=CORAL)
    a = fin(t, 0.2, 0.4)
    # load gauge (no number - qualitative)
    gx, gy, R = 270, 780, 170
    if a > 0.01:
        d.arc([gx - R, gy - R, gx + R, gy + R], 180, 252, fill=A(CORAL, a), width=26)
        d.arc([gx - R, gy - R, gx + R, gy + R], 252, 324, fill=A(AMBER, a), width=26)
        d.arc([gx - R, gy - R, gx + R, gy + R], 324, 360, fill=A(GREEN, a), width=26)
        th = math.radians(lerp(250, 205, ease((t - 0.3) / 1.2)) + 2 * math.sin(t * 8))
        d.line([(gx, gy), (gx + (R - 30) * math.cos(th), gy + (R - 30) * math.sin(th))], fill=A(WHITE, a), width=9)
        d.ellipse([gx - 16, gy - 16, gx + 16, gy + 16], fill=A(WHITE, a))
        label(d, gx, gy + 50, "LOAD: LOW", a, col=CORAL, sz=32)
    # cylinder cutaway
    cx0, cx1, ctop, cbot = 600, 900, 560, 1180
    if a > 0.01:
        d.rectangle([cx0 - 26, ctop, cx0, cbot], fill=A((120, 135, 155), a)); d.rectangle([cx1, ctop, cx1 + 26, cbot], fill=A((120, 135, 155), a))
        d.rectangle([cx0 - 26, ctop - 30, cx1 + 26, ctop], fill=A((120, 135, 155), a))
        d.polygon([(750 - 14, ctop - 30), (750 + 14, ctop - 30), (750 + 6, ctop + 22), (750 - 6, ctop + 22)], fill=A(GOLD, a))  # injector
        py = lerp(760, 960, 0.5 + 0.5 * math.sin(t * 5))
        d.rounded_rectangle([cx0 + 4, py, cx1 - 4, py + 110], radius=8, fill=A((170, 180, 196), a))
        d.line([(750, py + 110), (750, cbot + 40)], fill=A((150, 160, 176), a), width=26)
        # fuel spray each cycle; part stays unburned (amber droplets that linger)
        ph = (t * 5 / (2 * math.pi)) % 1.0
        rnd = random.Random(int(t * 5 / (2 * math.pi)))
        for k in range(16):
            ang = math.radians(rnd.uniform(55, 125)); dist = 30 + ph * rnd.uniform(80, 160)
            x, y = 750 + dist * math.cos(ang), ctop + 22 + dist * math.sin(ang)
            if y < py - 6: d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=A(AMBER, a * (1 - ph * 0.6)))
        # soot accumulates on walls/top over the clip
        acc = clamp((t - 0.8) / 3.4); rs = random.Random(7)
        for k in range(int(90 * acc)):
            side = rs.random()
            if side < 0.4: x, y = cx0 + rs.uniform(2, 18), rs.uniform(ctop + 4, 900)
            elif side < 0.8: x, y = cx1 - rs.uniform(2, 18), rs.uniform(ctop + 4, 900)
            else: x, y = rs.uniform(cx0 + 4, cx1 - 4), ctop + rs.uniform(2, 16)
            r = rs.uniform(4, 9); d.ellipse([x - r, y - r, x + r, y + r], fill=A(SOOT, a * 0.95))
        # wet unburned fuel streaks in the exhaust port
        d.rectangle([cx1 + 26, ctop + 20, cx1 + 150, ctop + 80], fill=A((90, 100, 115), a))
        for k in range(int(6 * acc)):
            x = cx1 + 40 + k * 18; d.line([(x, ctop + 80), (x, ctop + 80 + 18 + 10 * math.sin(k))], fill=A((60, 45, 20), a), width=7)
    label(d, 750, 1240, "UNBURNED FUEL + SOOT", fin(t, 1.4), col=AMBER, sz=40)
    return im

def f_lith(t):
    im, d = new()
    p2 = fin(t, 4.9, 0.5)  # phase 2: lead-acid vs lithium usable capacity
    title(d, "B: LITHIUM", "SILENT STORED POWER" if p2 < 0.5 else "LIGHTER  •  MORE USABLE", t if p2 < 0.5 else 1.0, col=TURQ)
    a1 = fin(t, 0.2, 0.5) * (1 - p2)
    moon(d, 120, 590, a1); label(d, 240, 580, "z z z", a1 * (0.6 + 0.4 * math.sin(t * 3)), col=ICE, sz=34)
    battery_bank(d, (60, 700, 400, 1000), t, a1, 1.0 - 0.04 * clamp(t / 5))
    inv = (450, 760, 690, 940); morph = fin(t, 1.0, 1.0)
    wire(d, [(400, 850), (450, 850)], t, TURQ, a1, fin(t, 0.8), grow=fin(t, 0.5, 0.4))
    inverter(d, inv, t, a1, morph)
    label(d, 570, 990, "INVERTER", fin(t, 0.9) * a1, col=ICE, sz=30)
    grow = fin(t, 1.6, 0.6); flow = fin(t, 2.1)
    for ly in (640, 850, 1080):
        wire(d, [(690, 850), (760, 850), (760, ly), (850, ly)], t, GOLD, a1, flow, grow=grow)
    on = [fin(t, 2.3 + 0.35 * k) for k in range(3)]
    fridge(d, 940, 640, a1, on[0]); bulb(d, 940, 845, a1, on[1]); fan(d, 940, 1090, t, a1, on[2])
    label(d, 230, 1050, "HOUSE BANK", a1, col=TURQ, sz=30)
    # phase 2 bars
    if p2 > 0.01:
        for k, (name, col, use, txt) in enumerate([("LEAD-ACID", GOLD, 0.5, "USE ~50%"), ("LITHIUM", TURQ, 0.9, "USE MOST OF IT")]):
            y0 = 640 + k * 300; x0, x1 = 120, 960
            label(d, x0, y0 - 40, name, p2, col=WHITE, sz=36, anchor="lm")
            d.rounded_rectangle([x0, y0, x1, y0 + 110], radius=20, outline=A(col, p2), width=5, fill=A((8, 20, 44), p2))
            fill = ease((t - 5.2 - 0.4 * k) / 1.0) * use
            if fill > 0.01: d.rounded_rectangle([x0 + 10, y0 + 10, x0 + 10 + (x1 - x0 - 20) * fill, y0 + 100], radius=14, fill=A(col, 0.9 * p2))
            if k == 0:
                xm = x0 + 10 + (x1 - x0 - 20) * 0.5
                for yy in range(int(y0 - 10), int(y0 + 120), 18): d.line([(xm, yy), (xm, yy + 9)], fill=A(CORAL, p2), width=5)
            label(d, x1, y0 + 150, txt, p2 * fin(t, 5.6 + 0.4 * k), col=col, sz=34, anchor="rm")
        pill(d, 540, 1230, "MUCH LIGHTER THAN LEAD-ACID", M(800, 30), TURQ, NAVY, fin(t, 6.6), h=60)
    return im

def f_ac(t):
    im, d = new(); title(d, "THE AIR-CON PROBLEM", "ONE UNIT, ALL NIGHT", t, col=CORAL)
    a = fin(t, 0.2, 0.4)
    ac_unit(d, 300, 620, t, a, 1.0, s=1.3)
    label(d, 300, 520, "16,000 BTU AIR-CON", a, col=ICE, sz=30)
    pill(d, 300, 800, "~1,200 W", M(800, 44), GOLD, NAVY, fin(t, 4.5), h=80)
    # clock: 8 hours sweep
    cx, cy, R = 800, 650, 130; ca = fin(t, 5.9)
    if ca > 0.01:
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=A((12, 30, 66), ca), outline=A(WHITE, ca), width=6)
        sweep = 240 * ease((t - 6.1) / 1.6)  # 8 of 12 hours
        if sweep > 1: d.pieslice([cx - R + 14, cy - R + 14, cx + R - 14, cy + R - 14], -90, -90 + sweep, fill=A(GOLD, 0.55 * ca))
        for k in range(12):
            th = math.radians(k * 30 - 90); d.line([(cx + (R - 22) * math.cos(th), cy + (R - 22) * math.sin(th)), (cx + (R - 8) * math.cos(th), cy + (R - 8) * math.sin(th))], fill=A(WHITE, ca), width=4)
        th = math.radians(-90 + sweep); d.line([(cx, cy), (cx + (R - 30) * math.cos(th), cy + (R - 30) * math.sin(th))], fill=A(WHITE, ca), width=8)
        label(d, cx, cy + R + 40, "8 HOURS", ca, col=WHITE, sz=34)
    # energy meter fills while the battery drains
    e = ease((t - 6.1) / 1.6); ea = fin(t, 5.9)
    x0, x1, y0 = 110, 970, 960
    if ea > 0.01:
        d.rounded_rectangle([x0, y0, x1, y0 + 100], radius=20, outline=A(GOLD, ea), width=5, fill=A((8, 20, 44), ea))
        if e > 0.01: d.rounded_rectangle([x0 + 10, y0 + 10, x0 + 10 + (x1 - x0 - 20) * e, y0 + 90], radius=14, fill=A(GOLD, 0.9 * ea))
        label(d, (x0 + x1) / 2, y0 + 50, f"{1.2 * 8 * e:.1f} kWh", ea, col=WHITE, sz=46)
        label(d, 540, y0 + 150, "1.2 kW  ×  8 h  =  9.6 kWh", ea * fin(t, 7.4), col=GOLD, sz=40)
    pill(d, 540, 1250, "THAT'S A VERY BIG BANK", M(800, 34), CORAL, WHITE, fin(t, 8.0), h=68)
    return im

def f_verdict(t):
    im, d = new(); title(d, "THE VERDICT", "USE BOTH", t, col=GREEN)
    a = fin(t, 0.1, 0.4); cur = 0.5 * clamp((t - 0.3) / 3.6) + 0.5 * clamp((t - 3.9) / 2.8)   # evening until ~3.9 s (abs ~50.4, 'then let the batteries...'), then night
    x0, x1, ty = 90, 990, 1140
    if a > 0.01:
        d.rounded_rectangle([x0, ty - 18, (x0 + x1) / 2, ty + 18], radius=18, fill=A((120, 70, 40), a))
        d.rounded_rectangle([(x0 + x1) / 2, ty - 18, x1, ty + 18], radius=18, fill=A((30, 50, 110), a))
        cx = lerp(x0 + 20, x1 - 20, cur); d.ellipse([cx - 24, ty - 24, cx + 24, ty + 24], fill=A(WHITE, a))
        label(d, (x0 + (x0 + x1) / 2) / 2, ty + 62, "EVENING", a, col=(255, 190, 120), sz=32)
        label(d, ((x0 + x1) / 2 + x1) / 2, ty + 62, "NIGHT", a, col=ICE, sz=32)
    ev = cur < 0.5
    sun(d, 880, 560, a * (1 - fin(cur, 0.45, 0.1))); moon(d, 880, 560, a * fin(cur, 0.45, 0.1))
    # generator (left) runs in the evening, stops at night
    ga = a; run = 1.0 if ev else max(0.0, 1 - (cur - 0.5) * 8)
    generator(d, (80, 690, 430, 900), t, ga, spin=run)
    sound_arcs(d, 430, 795, t, ga * run, side=0); puffs(d, 130, 680, t, ga * run)
    label(d, 255, 940, "GENERATOR " + ("ON" if run > 0.5 else "OFF"), ga, col=GOLD if run > 0.5 else (150, 160, 180), sz=30)
    # battery charges during evening, carries the night
    lvl = lerp(0.35, 1.0, ease(cur / 0.5)) if ev else lerp(1.0, 0.55, (cur - 0.5) / 0.5)
    battery_bank(d, (650, 690, 1000, 900), t, a, lvl)
    wire(d, [(430, 760), (650, 760)], t, GOLD, a, flow=run, grow=1.0)
    label(d, 825, 940, "CHARGING" if ev else "QUIET NIGHT", a, col=TURQ, sz=30)
    ac_unit(d, 540, 1000, t, a, 1.0, s=0.8)
    return im

CLIPS = {"gen": (f_gen, 9.0), "soot": (f_soot, 4.6), "lith": (f_lith, 9.2), "ac": (f_ac, 10.6), "verdict": (f_verdict, 6.9)}

def render(outdir, name):
    fn, dur = CLIPS[name]; out = os.path.join(outdir, f"power_{name}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)): p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait(); print("->", out)

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == "--still":
        nm, tt = sys.argv[3], float(sys.argv[4]); CLIPS[nm][0](tt).convert("RGB").save(os.path.join(outdir, f"still_{nm}_{tt}.png"))
    else:
        for nm in (sys.argv[2:] or CLIPS): render(outdir, nm)
