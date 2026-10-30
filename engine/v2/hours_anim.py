"""Animated 'carbon helm console' diagrams for ep 019 (why boat engines count hours, not kilometres). 1080x1920@30 MP4s.
  python3 engine/v2/hours_anim.py OUTDIR [name ...]     names: wheels, current, dock, meter, service, worked, sitting, compare, check, cta
  python3 engine/v2/hours_anim.py OUTDIR --still name t [t ...]
Look (new for ep 019): dark carbon-fibre helm panel with a fine weave, chrome-bezel instruments with amber backlight,
mechanical rolling-digit hour meter and odometer, tachometer needle. Side-view scenes on a dusk sea strip inside a
rounded 'screen'. Mechanisms shown: wheel turns = distance vs. boat with no wheels; prop working hard against a current
while the distance counter barely moves; idling at the dock (hours tick, km stay 0); ignition ON/OFF drives the hour
meter; service timeline every ~100 h; wear bar; years passing -> old fuel / dry seals / corrosion; low-hours-no-records
vs high-hours-full-records; buyer checklist; comment CTA."""
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
def O(sz, wt=700):
    k = ("o", wt, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + f"oswald-latin-{wt}-normal.woff", sz)
    return _fc[k]
NAVY = (9, 24, 54); GOLD = (214, 172, 86); TURQ = (18, 196, 204); WHITE = (255, 255, 255)
AMBER = (255, 176, 64); RED = (240, 84, 70); GREEN = (70, 205, 125); INK = (5, 8, 14); CHROME = (190, 198, 210)
SEA1 = (14, 70, 110); SEA2 = (8, 34, 62); RUST = (170, 88, 40)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t
def A(c, a): return tuple(int(v) for v in c[:3]) + (int(255 * clamp(a)),)
def fin(t, t0, d=0.35): return ease((t - t0) / d)
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))

# ------------------------------------------------------------- background: carbon-fibre helm panel with amber glow
def _bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    weave = (((xx // 9 + yy // 9) % 2) * 0.5 + ((xx + yy) % 18 < 9) * 0.5)          # 2x2 twill look
    g = np.clip(1 - np.hypot((xx - W / 2) / 820, (yy - 880) / 760), 0, 1) ** 1.4
    base = np.array((11, 14, 20), np.float32); hi = np.array((34, 38, 48), np.float32)
    arr = base + (hi - base) * g[..., None] + (weave[..., None] * 7 - 3.5) * (0.4 + g[..., None])
    arr += np.array((26, 14, 0), np.float32) * (g[..., None] ** 3)                  # warm amber backlight
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    a = np.zeros((H, W), np.uint8); a[1330:1450] = np.linspace(0, 255, 120).astype(np.uint8)[:, None]; a[1450:] = 255
    im.paste(Image.new("RGB", (W, H), (7, 9, 14)), (0, 0), Image.fromarray(a))      # calm caption zone
    a2 = np.zeros((H, W), np.uint8); a2[:300] = 255; a2[300:420] = np.linspace(255, 0, 120).astype(np.uint8)[:, None]
    im.paste(Image.new("RGB", (W, H), (7, 9, 14)), (0, 0), Image.fromarray(a2))     # calm logo zone
    d = ImageDraw.Draw(im, "RGBA")
    for x in (60, W - 60):                                                           # panel screws
        for y in (450, 1290):
            d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(70, 76, 88, 255), outline=(20, 22, 28, 255), width=2)
            d.line([(x - 6, y - 6), (x + 6, y + 6)], fill=(28, 30, 36, 255), width=3)
    return im
BG = _bg()
def new(t):
    im = BG.copy(); return im, ImageDraw.Draw(im, "RGBA")

def pill(d, cx, cy, s, f, bg, fg, a=1.0, padx=26, h=None):
    if a <= 0.01: return
    tw = f.getlength(s); h = h or int(f.size * 1.75)
    cx = clamp(cx, 40 + tw / 2 + padx, W - 40 - tw / 2 - padx)
    d.rounded_rectangle([cx - tw / 2 - padx, cy - h / 2, cx + tw / 2 + padx, cy + h / 2], radius=h // 2, fill=A(bg, 0.96 * a))
    d.text((cx, cy + 1), s, font=f, fill=A(fg, a), anchor="mm")
def title(d, tag, line, t, col=AMBER, y=470):
    a = fin(t, 0, 0.4)
    pill(d, W / 2, y, tag, M(800, 32), col, INK, a, h=58)
    if line:
        f = O(68)
        while f.getlength(line) > 980: f = O(f.size - 4)
        d.text((W / 2, y + 86 + (1 - a) * 30), line, font=f, fill=A(WHITE, a), anchor="mm", stroke_width=4, stroke_fill=A(INK, a))
def label(d, x, y, s, a, col=WHITE, sz=32, anchor="mm"):
    if a > 0.01: d.text((x, y), s, font=M(800, sz), fill=A(col, a), anchor=anchor, stroke_width=4, stroke_fill=A(INK, a))
def tick(d, cx, cy, a, col=GREEN, s=1.0):
    if a <= 0.01: return
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 30 * s], fill=A(col, a))
    d.line([(cx - 14 * s, cy + 1 * s), (cx - 4 * s, cy + 12 * s), (cx + 15 * s, cy - 11 * s)], fill=A(WHITE, a), width=int(7 * s), joint="curve")
def cross(d, cx, cy, a, s=1.0):
    if a <= 0.01: return
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 30 * s], fill=A(RED, a))
    for sx in (-1, 1): d.line([(cx - 12 * s, cy - 12 * s * sx), (cx + 12 * s, cy + 12 * s * sx)], fill=A(WHITE, a), width=int(7 * s))
def panel(d, r, a, col=AMBER, fill=(16, 19, 26)):
    if a <= 0.01: return
    x0, y0, x1, y1 = r
    d.rounded_rectangle([x0 - 7, y0 - 7, x1 + 7, y1 + 7], radius=32, outline=A(col, 0.16 * a), width=7)
    d.rounded_rectangle(r, radius=26, fill=A(fill, 0.95 * a), outline=A(col, a), width=4)

# ------------------------------------------------------------- instruments
_DIG = {}
def _digit_strip(sz, fg, bg):
    k = (sz, fg, bg)
    if k not in _DIG:
        f = O(sz, 700); cw, ch = int(sz * 0.62), int(sz * 1.08)
        im = Image.new("RGBA", (cw, ch * 11), bg + (255,)); dd = ImageDraw.Draw(im)
        for i in range(11): dd.text((cw / 2, ch * i + ch / 2), str(i % 10), font=f, fill=fg, anchor="mm")
        _DIG[k] = (im, cw, ch)
    return _DIG[k]
def counter(im, d, cx, cy, value, ndig, sz=78, tenths=True, a=1.0, unit=None, ucol=AMBER):
    """Mechanical rolling-digit counter (odometer style). value in whole units; last wheel shows tenths if tenths."""
    if a <= 0.01: return
    v = value * (10 if tenths else 1)
    wh, ww = [], 0
    for i in range(ndig):
        red = tenths and i == 0
        strip, cw, ch = _digit_strip(sz, (255, 255, 255) if not red else (20, 12, 0), (20, 22, 28) if not red else AMBER)
        p = v / 10 ** i; dig = int(p) % 10
        if i == 0: fr = p - int(p)
        else:
            low = v % 10 ** i; fr = clamp(low - (10 ** i - 1))
        wh.append((strip, cw, ch, dig, fr)); ww += cw + 6
    x = cx + ww / 2; ch = wh[0][2]; y0 = cy - ch / 2
    d.rounded_rectangle([cx - ww / 2 - 22, y0 - 18, cx + ww / 2 + 16, y0 + ch + 18], radius=14, fill=A((40, 44, 52), a), outline=A(CHROME, a), width=5)
    for strip, cw, ch2, dig, fr in wh:
        x -= cw + 6
        crop = strip.crop((0, int((dig + fr) * ch2), cw, int((dig + fr) * ch2) + ch2))
        if a < 1: crop.putalpha(crop.getchannel("A").point(lambda q: int(q * a)))
        im.paste(crop, (int(x), int(y0)), crop)
    # glass shine + shading
    d.rectangle([cx - ww / 2 - 12, y0, cx + ww / 2 + 6, y0 + ch * 0.18], fill=A((0, 0, 0), 0.35 * a))
    d.rectangle([cx - ww / 2 - 12, y0 + ch * 0.82, cx + ww / 2 + 6, y0 + ch], fill=A((0, 0, 0), 0.35 * a))
    if unit: label(d, cx, y0 + ch + 58, unit, a, ucol, 34)

def tacho(d, cx, cy, r, rpm, a=1.0, lab="RPM x1000"):
    if a <= 0.01: return
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=A(CHROME, a))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A((14, 16, 22), a))
    d.ellipse([cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], outline=A(AMBER, 0.18 * a), width=10)
    for i in range(7):
        ang = math.radians(225 - i * 45); x1, y1 = cx + (r - 22) * math.cos(ang), cy - (r - 22) * math.sin(ang)
        x2, y2 = cx + (r - 46) * math.cos(ang), cy - (r - 46) * math.sin(ang)
        d.line([(x1, y1), (x2, y2)], fill=A(RED if i >= 5 else WHITE, a), width=5)
        tx, ty = cx + (r - 72) * math.cos(ang), cy - (r - 72) * math.sin(ang)
        d.text((tx, ty), str(i), font=M(800, int(r * 0.16)), fill=A(WHITE, a), anchor="mm")
    ang = math.radians(225 - clamp(rpm / 6) * 270)
    d.line([(cx - 20 * math.cos(ang), cy + 20 * math.sin(ang)), (cx + (r - 34) * math.cos(ang), cy - (r - 34) * math.sin(ang))], fill=A(AMBER, a), width=8)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=A(CHROME, a))
    d.text((cx, cy + r * 0.5), lab, font=M(700, int(r * 0.11)), fill=A((200, 200, 200), a), anchor="mm")

# ------------------------------------------------------------- side-view boat on a sea strip
def screen(d, r, a=1.0):
    x0, y0, x1, y1 = r
    d.rounded_rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], radius=30, fill=A((30, 34, 42), a), outline=A(CHROME, 0.7 * a), width=4)
    for i in range(y1 - y0):
        u = i / (y1 - y0); d.line([(x0, y0 + i), (x1, y0 + i)], fill=A(mix((40, 60, 96), (240, 150, 80), u ** 2), a))
def sea(d, x0, x1, ywl, y1, t, a=1.0, speed=60):
    pts = [(x0, y1)]
    for x in range(x0, x1 + 1, 12): pts.append((x, ywl + 7 * math.sin(x / 46 + t * 2.2) + 3 * math.sin(x / 19 - t * 3.1)))
    pts.append((x1, y1)); d.polygon(pts, fill=A(SEA1, a))
    for k in range(5):
        y = ywl + 40 + k * 34
        for j in range(6):
            x = x0 + ((j * 170 + k * 60 - t * speed) % (x1 - x0))
            d.line([(x, y), (x + 60, y)], fill=A((120, 190, 230), 0.25 * a), width=3)
def boat(d, cx, ywl, t, a=1.0, rpm=0.5, s=1.0, rope=False, xmin=100):
    """Motor yacht side view facing right; stern at left with prop under the hull."""
    L = 420 * s
    hull = [(cx - L / 2, ywl - 50 * s), (cx + L / 2 + 40 * s, ywl - 64 * s), (cx + L / 2 - 30 * s, ywl + 24 * s), (cx - L / 2 + 10 * s, ywl + 30 * s)]
    d.polygon(hull, fill=A((246, 246, 250), a))
    d.polygon([(cx - L / 2 + 6 * s, ywl - 2 * s), (cx + L / 2 + 8 * s, ywl - 18 * s), (cx + L / 2 - 26 * s, ywl + 22 * s), (cx - L / 2 + 10 * s, ywl + 30 * s)], fill=A(NAVY, a))
    d.line([(cx - L / 2, ywl - 30 * s), (cx + L / 2 + 22 * s, ywl - 44 * s)], fill=A(GOLD, a), width=int(5 * s))
    d.polygon([(cx - L / 2 + 70 * s, ywl - 50 * s), (cx - L / 2 + 100 * s, ywl - 120 * s), (cx + 80 * s, ywl - 124 * s), (cx + 150 * s, ywl - 56 * s)], fill=A((236, 238, 244), a))
    d.polygon([(cx - L / 2 + 112 * s, ywl - 108 * s), (cx + 70 * s, ywl - 110 * s), (cx + 118 * s, ywl - 64 * s), (cx - L / 2 + 104 * s, ywl - 64 * s)], fill=A((40, 70, 100), a))
    # shaft + prop
    px, py = cx - L / 2 + 50 * s, ywl + 52 * s
    d.line([(cx - L / 2 + 120 * s, ywl + 26 * s), (px, py)], fill=A(CHROME, a), width=int(6 * s))
    ph = t * (6 + 30 * rpm)
    for k in range(3):
        h = 34 * s * abs(math.cos(ph + k * 2.094))
        d.ellipse([px - 8 * s, py - h, px + 8 * s, py + h], fill=A(GOLD, a))
    d.ellipse([px - 7 * s, py - 7 * s, px + 7 * s, py + 7 * s], fill=A(CHROME, a))
    # prop wash
    for k in range(int(4 + 10 * rpm)):
        u = ((t * (1 + 3 * rpm)) + k / (4 + 10 * rpm)) % 1
        x = px - 30 * s - u * 260 * s * (0.4 + rpm); y = py + 10 * s * math.sin(u * 9 + k)
        r = (4 + 10 * u) * s
        if x - r > xmin: d.ellipse([x - r, y - r, x + r, y + r], fill=A(WHITE, (0.55 - 0.5 * u) * a))
    # exhaust puffs
    for k in range(3):
        u = (t * 0.8 + k / 3) % 1; x = cx - L / 2 - 10 * s - 50 * u * s; y = ywl - 40 * s - 70 * u * s; r = (10 + 30 * u) * s
        if x - r > xmin: d.ellipse([x - r, y - r, x + r, y + r], fill=A((200, 200, 205), (0.35 - 0.33 * u) * a * (0.4 + rpm)))
    if rope: d.line([(cx + L / 2 + 30 * s, ywl - 58 * s), (cx + L / 2 + 120 * s, ywl - 10 * s)], fill=A((220, 200, 150), a), width=int(5 * s))

# ============================================================= clips
def f_wheels(t):   # "Because a boat has no wheels touching the road." (0.2 - 2.7)
    im, d = new(t); title(d, "1 · NO ROAD, NO WHEELS", None, t)
    # CAR: wheel turning on a road, odometer counting
    a = fin(t, 0.0, 0.35)
    panel(d, (70, 540, 1010, 880), a, TURQ)
    label(d, 120, 585, "CAR", a, TURQ, 36, "lm")
    d.rectangle([110, 820, 600, 834], fill=A((90, 94, 104), a))
    for k in range(7):
        x = 110 + ((k * 80 - t * 160) % 490); d.rectangle([x, 825, x + 40, 829], fill=A((240, 220, 120), a))
    wx, wy, wr = 330, 740, 76
    d.ellipse([wx - wr, wy - wr, wx + wr, wy + wr], fill=A((22, 24, 28), a)); d.ellipse([wx - 46, wy - 46, wx + 46, wy + 46], fill=A(CHROME, a))
    for k in range(5):
        ang = -t * 4 + k * 1.2566; d.line([(wx, wy), (wx + 40 * math.cos(ang), wy + 40 * math.sin(ang))], fill=A((70, 74, 84), a), width=8)
    label(d, 600, 590, "WHEEL TURNS = DISTANCE", fin(t, 0.4, 0.3), WHITE, 28)
    counter(im, d, 800, 700, 48213 + t * 2.2, 6, 62, True, a, "KM", TURQ)
    # BOAT: no wheels
    b = fin(t, 0.9, 0.35)
    panel(d, (70, 920, 1010, 1290), b, AMBER)
    label(d, 120, 965, "BOAT", b, AMBER, 36, "lm")
    if b > 0.01:
        sea(d, 90, 990, 1180, 1270, t, b); boat(d, 420, 1180, t, b, 0.5, 0.75)
        label(d, 790, 1060, "NO WHEELS.", fin(t, 1.3, 0.3), WHITE, 42)
        label(d, 790, 1112, "NO ROAD.", fin(t, 1.6, 0.3), AMBER, 42)
    return im

def f_current(t):  # "...the engine works hard, but the boat barely moves." (works hard 0.9, barely moves 2.7)
    im, d = new(t); title(d, "INTO A STRONG CURRENT", None, t, RED)
    screen(d, (90, 560, 990, 990), 1)
    sea(d, 90, 990, 850, 990, t, 1, speed=420)
    bx = 520 + 6 * math.sin(t * 1.3) + 10 * t
    boat(d, bx, 850, t, 1, 1.0, 0.95)
    for k in range(6):                                       # current arrows flowing left (against the boat)
        y = 905 + (k % 3) * 28; x = 990 - ((t * 330 + k * 150) % 900)
        if x - 86 < 100: continue
        d.line([(x, y), (x - 70, y)], fill=A((170, 230, 255), 0.85), width=6)
        d.polygon([(x - 86, y), (x - 66, y - 12), (x - 66, y + 12)], fill=A((170, 230, 255), 0.85))
    label(d, 270, 610, "CURRENT", fin(t, 0.3, 0.3), (170, 230, 255), 34)
    tacho(d, 290, 1135, 128, lerp(0.8, 5.2, fin(t, 0.4, 1.0)) + 0.08 * math.sin(t * 20), fin(t, 0.2, 0.3))
    label(d, 290, 1300, "WORKING HARD", fin(t, 1.0, 0.3), RED, 34)
    c = fin(t, 1.6, 0.35)
    panel(d, (520, 1035, 1000, 1280), c, TURQ)
    label(d, 760, 1075, "DISTANCE MADE", c, TURQ, 30)
    counter(im, d, 760, 1160, 0.2 + 0.05 * t, 4, 66, True, c, None)
    label(d, 760, 1250, "BARELY MOVES", fin(t, 2.6, 0.3), WHITE, 32)
    return im

def f_dock(t):     # "Idling at the dock, it runs and goes nowhere. Distance would lie." (lie 1.6)
    im, d = new(t); title(d, "IDLING AT THE DOCK", None, t, AMBER)
    screen(d, (90, 560, 990, 960), 1)
    d.rectangle([800, 820, 990, 860], fill=A((120, 92, 60), 1)); d.rectangle([800, 860, 990, 960], fill=A((70, 52, 34), 1))
    for x in (830, 930): d.rectangle([x, 760, x + 22, 960], fill=A((90, 68, 44), 1))
    sea(d, 90, 990, 850, 960, t, 1, speed=25)
    boat(d, 520, 850, t, 1, 0.15, 0.95, rope=True)
    a = fin(t, 0.3, 0.35)
    panel(d, (80, 1010, 530, 1290), a, TURQ); label(d, 305, 1050, "DISTANCE", a, TURQ, 30)
    counter(im, d, 305, 1150, 0.0, 4, 64, True, a, None)
    label(d, 305, 1245, "0 KM", a, WHITE, 34)
    b = fin(t, 0.6, 0.35)
    panel(d, (550, 1010, 1000, 1290), b, AMBER); label(d, 775, 1050, "ENGINE HOURS", b, AMBER, 30)
    counter(im, d, 775, 1150, 412.3 + t * 0.9, 5, 60, True, b, None)
    label(d, 775, 1245, "STILL COUNTING", b, WHITE, 30)
    c = fin(t, 1.6, 0.3)
    if c > 0.01:
        d.line([(110, 1150), (500, 1150)], fill=A(RED, c), width=8)
        pill(d, 305, 1150, "DISTANCE LIES", M(800, 34), RED, WHITE, c, h=64)
    return im

def f_meter(t):    # "So an hour meter simply counts every minute the engine is running." (hour meter 0.7, every minute 1.9)
    im, d = new(t); title(d, "THE HOUR METER", None, t)
    on = t > 1.0 and not (2.75 < t < 3.35)
    a = fin(t, 0.2, 0.4)
    # big meter with rolling digits; only runs when the engine is ON
    run = 0.0
    for k in range(int(t * 30)):
        tt = k / 30
        if tt > 1.0 and not (2.75 < tt < 3.35): run += 1 / 30
    d.ellipse([540 - 290, 830 - 290, 540 + 290, 830 + 290], fill=A(CHROME, a))
    d.ellipse([540 - 270, 830 - 270, 540 + 270, 830 + 270], fill=A((14, 16, 22), a))
    d.ellipse([540 - 252, 830 - 252, 540 + 252, 830 + 252], outline=A(AMBER, (0.35 if on else 0.08) * a), width=12)
    d.text((540, 670), "HOURS", font=M(800, 40), fill=A(AMBER, a), anchor="mm")
    counter(im, d, 540, 820, 1287.4 + run * 2.0, 6, 88, True, a, None)
    # hourglass icon (counts time, not distance)
    hx, hy = 540, 990; ga = a
    d.polygon([(hx - 26, hy - 40), (hx + 26, hy - 40), (hx, hy)], outline=A(WHITE, ga), width=4)
    d.polygon([(hx - 26, hy + 40), (hx + 26, hy + 40), (hx, hy)], outline=A(WHITE, ga), width=4)
    sand = (run * 0.5) % 1
    d.polygon([(hx - 20 * (1 - sand), hy - 34 + 34 * sand), (hx + 20 * (1 - sand), hy - 34 + 34 * sand), (hx, hy - 2)], fill=A(AMBER, ga))
    d.polygon([(hx - 20 * sand, hy + 36 - 30 * sand), (hx + 20 * sand, hy + 36 - 30 * sand), (hx + 22, hy + 36), (hx - 22, hy + 36)], fill=A(AMBER, ga))
    # ignition switch
    b = fin(t, 0.6, 0.35)
    pill(d, 330, 1260, "ENGINE ON", M(800, 36), GREEN if on else (60, 64, 72), WHITE if on else (150, 150, 150), b, h=74)
    pill(d, 750, 1260, "ENGINE OFF", M(800, 36), RED if (not on and t > 1.0) else (60, 64, 72), WHITE if (not on and t > 1.0) else (150, 150, 150), b, h=74)
    label(d, 540, 1170, "COUNTS ONLY WHILE IT RUNS", fin(t, 1.9, 0.3), WHITE, 38)
    return im

def f_service(t):  # "Many outboards, for example, need an oil change about every hundred hours." (oil 2.6, hundred 3.9)
    im, d = new(t); title(d, "2 · SERVICE BY THE HOUR", None, t, GOLD)
    a = fin(t, 0.0, 0.35)
    panel(d, (70, 560, 1010, 1290), a, GOLD)
    label(d, 540, 615, "MANY OUTBOARDS: OIL CHANGE", a, WHITE, 36)
    label(d, 540, 665, "ABOUT EVERY 100 HOURS", fin(t, 3.6, 0.35), GOLD, 40)
    x0, x1, y = 140, 940, 980
    d.rounded_rectangle([x0, y - 14, x1, y + 14], radius=14, fill=A((40, 44, 52), a))
    hrs = lerp(0, 400, ease(clamp((t - 0.4) / 4.2)))
    d.rounded_rectangle([x0, y - 14, x0 + (x1 - x0) * hrs / 400, y + 14], radius=14, fill=A(GOLD, a))
    for k in range(5):
        x = x0 + (x1 - x0) * k / 4
        d.line([(x, y + 22), (x, y + 44)], fill=A(WHITE, a), width=4)
        label(d, x, y + 80, f"{k * 100} h", a, WHITE, 30)
        if k > 0:
            p = clamp((hrs - k * 100 + 12) / 14)
            if p > 0:
                s = 1 + 0.25 * math.sin(clamp(p) * math.pi)
                dx, dy = x, y - 115                                         # oil drop icon
                d.ellipse([dx - 32 * s, dy - 10 * s, dx + 32 * s, dy + 54 * s], fill=A(AMBER, p))
                d.polygon([(dx - 29 * s, dy + 10 * s), (dx + 29 * s, dy + 10 * s), (dx, dy - 52 * s)], fill=A(AMBER, p))
                d.ellipse([dx - 12 * s, dy + 12 * s, dx - 2 * s, dy + 30 * s], fill=A(WHITE, 0.6 * p))
                label(d, x, y - 200, "OIL", p, AMBER, 28)
    counter(im, d, 540, 1160, hrs, 5, 60, True, a, "ENGINE HOURS")
    return im

def f_worked(t):   # "...hours show how hard the engine has worked." (hours 0.3, worked 1.1)
    im, d = new(t); title(d, "BUYING USED?", None, t, TURQ)
    a = fin(t, 0.0, 0.35)
    panel(d, (90, 560, 990, 1290), a, TURQ)
    label(d, 540, 620, "HOURS = HOW HARD IT WORKED", fin(t, 0.6, 0.3), WHITE, 38)
    counter(im, d, 540, 770, lerp(0, 1350, ease(clamp(t / 2.3))), 5, 72, False, a, None)
    label(d, 540, 870, "ENGINE HOURS", a, TURQ, 30)
    # wear bar
    w = ease(clamp(t / 2.3))
    x0, x1, y = 170, 910, 1010
    for i in range(60):
        u = i / 60
        if u <= w: d.rectangle([x0 + (x1 - x0) * u, y - 28, x0 + (x1 - x0) * (u + 1 / 60) - 2, y + 28], fill=A(mix(GREEN, mix(AMBER, RED, (u - 0.5) * 2), u * 2), a))
    d.rounded_rectangle([x0 - 8, y - 36, x1 + 8, y + 36], radius=12, outline=A(CHROME, a), width=4)
    label(d, x0, y + 80, "LIGHT USE", a, GREEN, 28, "lm"); label(d, x1, y + 80, "HEAVY USE", a, RED, 28, "rm")
    label(d, 540, 1200, "LIKE MILEAGE ON A CAR", fin(t, 1.4, 0.3), GOLD, 38)
    return im

def f_sitting(t):  # "An engine that sits for years can suffer old fuel, dry seals and corrosion." (fuel 2.7, seals 3.7, corrosion 4.4)
    im, d = new(t); title(d, "3 · THE CATCH", "LOW HOURS? NOT ALWAYS GOOD", t, RED)
    a = fin(t, 0.1, 0.35)
    # calendar flipping years
    panel(d, (90, 640, 450, 960), a, CHROME)
    yr = 2019 + int(clamp(t / 2.2) * 6)
    d.rectangle([90, 640, 450, 715], fill=A(RED, a)); label(d, 270, 678, "SITTING UNUSED", a, WHITE, 26)
    d.text((270, 840), str(min(yr, 2025)), font=O(110), fill=A(WHITE, a), anchor="mm")
    fl = (t * 2.7) % 1 if t < 2.2 else 0
    if fl > 0: d.polygon([(100, 725), (440, 725), (440, 725 + 220 * (1 - fl)), (100, 725 + 220 * (1 - fl))], fill=A((230, 230, 235), 0.25 * a))
    # engine block icon getting old
    age = clamp(t / 4.6)
    ex, ey = 740, 800
    col = mix((150, 158, 170), (120, 96, 80), age)
    d.rounded_rectangle([ex - 200, ey - 120, ex + 200, ey + 140], radius=22, fill=A(col, a))
    d.rounded_rectangle([ex - 170, ey - 170, ex + 170, ey - 110], radius=12, fill=A(mix((90, 96, 110), (100, 70, 50), age), a))
    for k in range(4): d.rectangle([ex - 150 + k * 82, ey - 98, ex - 96 + k * 82, ey - 50], fill=A((50, 54, 62), a))
    rnd = random.Random(19)
    for k in range(int(28 * fin(t, 4.3, 0.8))):
        x = ex + rnd.uniform(-190, 190); y = ey + rnd.uniform(-110, 130); r = rnd.uniform(6, 16)
        d.ellipse([x - r, y - r, x + r, y + r], fill=A(RUST, 0.85 * a))
    label(d, ex, ey + 20, "ENGINE", a, (30, 32, 38), 40)
    # problems list
    items = [("OLD FUEL", 2.6), ("DRY SEALS", 3.6), ("CORROSION", 4.3)]
    for i, (s, t0) in enumerate(items):
        y = 1050 + i * 80; b = fin(t, t0, 0.3)
        cross(d, 170, y, b, 0.8); label(d, 220, y, s, b, WHITE, 40, "lm")
    return im

def f_compare(t):  # "A busy engine with full service records is often the safer buy." (records 1.3, safer 3.3)
    im, d = new(t); title(d, "WHICH IS THE SAFER BUY?", None, t, GOLD)
    a = fin(t, 0.1, 0.35); b = fin(t, 0.6, 0.35)
    panel(d, (70, 560, 525, 1170), a, RED); panel(d, (555, 560, 1010, 1170), b, GREEN)
    label(d, 297, 620, "LOW HOURS", a, WHITE, 36); label(d, 782, 620, "HIGH HOURS", b, WHITE, 36)
    counter(im, d, 297, 730, 350, 4, 60, False, a, None); counter(im, d, 782, 730, 1400, 4, 60, False, b, None)
    rows_a = ["NO RECORDS", "SAT FOR YEARS"]; rows_b = ["FULL SERVICE", "RECORDS"]
    for i, s in enumerate(rows_a):
        aa = fin(t, 0.5 + i * 0.3, 0.3); cross(d, 120, 870 + i * 90, aa, 0.7); label(d, 160, 870 + i * 90, s, aa, WHITE, 28, "lm")
    bb = fin(t, 1.3, 0.3)
    tick(d, 605, 870, bb, GREEN, 0.7); label(d, 645, 870, "FULL SERVICE", bb, WHITE, 28, "lm")
    label(d, 645, 908, "RECORDS", bb, WHITE, 28, "lm")
    tick(d, 605, 960, fin(t, 1.8, 0.3), GREEN, 0.7); label(d, 645, 960, "USED OFTEN", fin(t, 1.8, 0.3), WHITE, 28, "lm")
    s = fin(t, 3.1, 0.35)
    if s > 0.01:
        sc = 1 + 0.15 * (1 - s)
        pill(d, 782, 1090, "SAFER BUY", M(800, int(40 * sc)), GREEN, WHITE, s, h=int(76 * sc))
        d.rectangle([80, 570, 515, 1160], fill=A((0, 0, 0), 0.35 * s))
    return im

def f_check(t):    # "So always ask why the hours are low, and ask to see the service history." (low 0.5, history 2.4)
    im, d = new(t); title(d, "BEFORE YOU BUY, ASK:", None, t, TURQ)
    a = fin(t, 0.0, 0.35)
    panel(d, (90, 590, 990, 1220), a, TURQ, fill=(232, 234, 238))
    for i in range(7): d.line([(150, 700 + i * 72), (930, 700 + i * 72)], fill=A((180, 200, 220), a), width=2)
    items = [("WHY ARE THE", "HOURS LOW?", 0.4), ("CAN I SEE THE", "SERVICE HISTORY?", 2.3)]
    for i, (l1, l2, t0) in enumerate(items):
        y = 760 + i * 250; b = fin(t, t0, 0.3)
        d.rounded_rectangle([150, y - 50, 250, y + 50], radius=14, outline=A(NAVY, a), width=6)
        if b > 0.01:
            d.line([(170, y), (195, y + 28), (240, y - 34)], fill=A(GREEN, b), width=12, joint="curve")
        d.text((290, y - 28), l1, font=M(800, 44), fill=A(NAVY, fin(t, t0 - 0.2, 0.3)), anchor="lm")
        d.text((290, y + 28), l2, font=M(800, 44), fill=A(NAVY, fin(t, t0 - 0.2, 0.3)), anchor="lm")
    return im

def f_cta(t):      # "How many hours are on your engine? Tell us in the comments."
    im, d = new(t)
    a = fin(t, 0.0, 0.35)
    label(d, 540, 560, "HOW MANY HOURS", a, WHITE, 70); label(d, 540, 650, "ON YOUR ENGINE?", a, AMBER, 70)
    d.ellipse([540 - 230, 930 - 230, 540 + 230, 930 + 230], fill=A(CHROME, fin(t, 0.2, 0.35)))
    d.ellipse([540 - 212, 930 - 212, 540 + 212, 930 + 212], fill=A((14, 16, 22), fin(t, 0.2, 0.35)))
    d.text((540, 820), "HOURS", font=M(800, 34), fill=A(AMBER, fin(t, 0.2, 0.35)), anchor="mm")
    b = fin(t, 0.3, 0.35)
    if b > 0.01:
        cw = 74; x = 540 - 2.5 * cw
        d.rounded_rectangle([x - 14, 880, x + 5 * cw + 8, 990], radius=12, fill=A((40, 44, 52), b), outline=A(CHROME, b), width=5)
        for k in range(5):
            ch = "?" if (int(t * 6) + k) % 3 else str((int(t * 9) + k * 3) % 10)
            d.rectangle([x + k * cw, 888, x + k * cw + cw - 6, 982], fill=A((20, 22, 28), b))
            d.text((x + k * cw + cw / 2 - 3, 935), ch, font=O(70), fill=A(WHITE, b), anchor="mm")
    pill(d, 540, 1240, "COMMENT YOUR HOURS", M(800, 40), AMBER, INK, fin(t, 0.9, 0.35), h=82)
    return im

CLIPS = {"wheels": (f_wheels, 3.2), "current": (f_current, 4.1), "dock": (f_dock, 3.2), "meter": (f_meter, 4.5),
         "service": (f_service, 5.5), "worked": (f_worked, 3.3), "sitting": (f_sitting, 5.8), "compare": (f_compare, 4.7),
         "check": (f_check, 4.1), "cta": (f_cta, 4.3)}

def render(outdir, name):
    fn, dur = CLIPS[name]; out = os.path.join(outdir, f"hrs_{name}.mp4")
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
