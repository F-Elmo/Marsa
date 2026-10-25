"""Animated 'underwater blueprint' diagrams for ep 017 (why propellers cavitate). 1080x1920@30 MP4s.
  python3 engine/v2/cav_anim.py OUTDIR [name ...]        names: wing, boil, bubbles, collapse, pits, signs, causes, fix
  python3 engine/v2/cav_anim.py OUTDIR --still name t     (single PNG for checking)
Look (new for ep 017): deep-teal underwater blueprint with light rays and drifting particles; a blade cross-section in
moving flow lines with a red/blue PRESSURE colour-map, a boiling-point thermometer, bubble growth + implosion micro-jets,
a pitted 'cavitation burn' blade, symptom cards with live gauges, and a cause/fix checklist."""
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
LOWC = (60, 140, 255); HIGHC = (255, 86, 64); GREEN = (70, 210, 130); METAL = (178, 186, 196); BRONZE = (196, 150, 92)
INK = (2, 16, 30)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t
def A(c, a): return tuple(int(v) for v in c[:3]) + (int(255 * clamp(a)),)
def fin(t, t0, d=0.35): return ease((t - t0) / d)
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- background: deep teal water + blueprint grid
def _bg():
    y = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array((7, 58, 82)) * (1 - y) + np.array((2, 18, 34)) * y).repeat(W, 1).astype(np.uint8)
    im = Image.fromarray(arr); d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 54): d.line([(x, 470), (x, 1330)], fill=(120, 220, 240, 13), width=1)
    for yy in range(470, 1331, 54): d.line([(0, yy), (W, yy)], fill=(120, 220, 240, 13), width=1)
    a = np.zeros((H, W), np.uint8); a[1330:1450] = np.linspace(0, 255, 120).astype(np.uint8)[:, None]; a[1450:] = 255
    im.paste(Image.new("RGB", (W, H), (2, 14, 28)), (0, 0), Image.fromarray(a))   # calm caption zone
    return im
BG = _bg()
_rnd = random.Random(17)
PARTS = [(_rnd.uniform(0, W), _rnd.uniform(420, 1330), _rnd.uniform(8, 26), _rnd.choice([1, 2, 2, 3]), _rnd.uniform(0, 6.28)) for _ in range(60)]

def _rays(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(5):
        x = 120 + k * 210 + 60 * math.sin(t * 0.35 + k * 1.7)
        d.polygon([(x - 26, 0), (x + 26, 0), (x + 170, 1330), (x + 40, 1330)], fill=(170, 240, 255, 9 + 5 * (k % 2)))
    return lay.filter(ImageFilter.GaussianBlur(18))
_RAYC = {}
def new(t):
    im = BG.copy(); k = int(t * 6)          # rays update 6x per second (cheap, still smooth enough)
    if k not in _RAYC: _RAYC.clear(); _RAYC[k] = _rays(k / 6)
    im.paste(_RAYC[k], (0, 0), _RAYC[k]); d = ImageDraw.Draw(im, "RGBA")
    for x, y, sp, r, ph in PARTS:
        yy = 470 + ((y - 470 - sp * t) % 860); xx = x + 6 * math.sin(t * 0.8 + ph)
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(210, 245, 255, 60))
    return im, d

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
        f = O(74)
        while f.getlength(line) > 980: f = O(f.size - 4)
        d.text((W / 2, y + 94 + (1 - a) * 30), line, font=f, fill=A(WHITE, a), anchor="mm", stroke_width=4, stroke_fill=A(INK, a))

def label(d, x, y, s, a, col=WHITE, sz=30, anchor="mm"):
    if a > 0.01: d.text((x, y), s, font=M(800, sz), fill=A(col, a), anchor=anchor, stroke_width=3, stroke_fill=A(INK, a))

def card(d, r, a, col=TURQ, fill=(8, 40, 64)):
    if a <= 0.01: return
    x0, y0, x1, y1 = r
    d.rounded_rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], radius=34, outline=A(col, 0.12 * a), width=8)
    d.rounded_rectangle(r, radius=26, fill=A(fill, 0.94 * a), outline=A(col, a), width=4)

def tick(d, cx, cy, a, col=GREEN, s=1.0):
    if a <= 0.01: return
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 30 * s], fill=A(col, a))
    d.line([(cx - 14 * s, cy + 1 * s), (cx - 4 * s, cy + 12 * s), (cx + 15 * s, cy - 11 * s)], fill=A(WHITE, a), width=int(7 * s), joint="curve")

def cross(d, cx, cy, a, col=HIGHC, s=1.0):
    if a <= 0.01: return
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 30 * s], fill=A(col, a))
    for sg in (1, -1): d.line([(cx - 12 * s, cy - 12 * s * sg), (cx + 12 * s, cy + 12 * s * sg)], fill=A(WHITE, a), width=int(7 * s))

# ---------------------------------------------------------------- blade cross-section (NACA 4412-like aerofoil)
FX, FY, CH, AOA = 520, 860, 640, math.radians(7)
def _foil():
    m, p, th = 0.04, 0.4, 0.13; up, lo = [], []
    for i in range(61):
        x = (1 - math.cos(math.pi * i / 60)) / 2
        yt = 5 * th * (0.2969 * math.sqrt(x) - 0.126 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1015 * x ** 4)
        yc = m / p ** 2 * (2 * p * x - x * x) if x < p else m / (1 - p) ** 2 * (1 - 2 * p + 2 * p * x - x * x)
        up.append((x, yc + yt)); lo.append((x, yc - yt))
    def tr(x, y):  # chord-space -> screen; leading edge on the left, nose tipped up by AOA
        X, Y = (x - 0.4) * CH, -y * CH
        c, s = math.cos(AOA), math.sin(AOA)
        return (FX + X * c + Y * s, FY - X * s + Y * c)
    return [tr(*q) for q in up], [tr(*q) for q in lo], tr
UP, LO, TR = _foil()
FOIL = UP + LO[::-1]

def _field():   # pressure colour-map at 1/4 res: blue suction over the back, red stagnation/pressure under the face
    h, w = H // 4, W // 4; yy, xx = np.mgrid[0:h, 0:w] * 4.0
    F = np.zeros((h, w))
    for (cx, cy), amp, sx, sy in [(TR(0.25, 0.16), -1.0, 210, 105), (TR(0.55, 0.12), -0.6, 220, 90),
                                  (TR(0.02, -0.03), 0.9, 70, 70), (TR(0.35, -0.12), 0.65, 260, 80)]:
        F += amp * np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2))
    rgba = np.zeros((h, w, 4), np.uint8)
    neg, pos = np.clip(-F, 0, 1), np.clip(F, 0, 1)
    rgba[..., 0] = (LOWC[0] * neg + HIGHC[0] * pos).clip(0, 255); rgba[..., 1] = (LOWC[1] * neg + HIGHC[1] * pos).clip(0, 255)
    rgba[..., 2] = (LOWC[2] * neg + HIGHC[2] * pos).clip(0, 255); rgba[..., 3] = (np.clip(neg + pos, 0, 1) * 150).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA").resize((W, H), Image.BICUBIC)
FIELD = _field()

def draw_foil(im, d, t, a, field=0.0, draw=1.0, flow=1.0):
    if field > 0.01:
        f = FIELD.copy(); f.putalpha(f.getchannel("A").point(lambda v: int(v * field))); im.paste(f, (0, 0), f)
    # flow lines (relative water flow left -> right), squeezed and faster over the back
    for k in range(-5, 6):
        if k == 0: continue
        y0 = FY + k * 72 + (24 if k > 0 else -24); pts = []
        for x in range(30, W - 29, 20):
            g = math.exp(-((x - (FX - 60)) / 300) ** 2) * math.exp(-(abs(k) - 1) / 3.2)
            dy = -g * 70 if k < 0 else g * 34
            dy -= (x - FX) * math.tan(AOA) * 0.35 * math.exp(-(abs(k) - 1) / 2.5)
            pts.append((x, y0 + dy))
        sp = (300 if k < 0 else 190) * (1.35 if abs(k) <= 2 and k < 0 else 1.0)
        ca = a * flow * (0.55 if abs(k) > 2 else 0.8)
        d.line(pts, fill=A((150, 225, 240), 0.18 * a * flow), width=2)
        off = (t * sp) % 80
        for i in range(len(pts) - 1):
            x = pts[i][0]
            if (x - off) % 80 < 30 and x < pts[-1][0] * draw + 30:
                d.line([pts[i], pts[i + 1]], fill=A(WHITE, ca), width=4)
    if draw > 0.01:
        n = max(2, int(len(FOIL) * draw)); poly = FOIL[:n] if draw < 1 else FOIL
        if draw >= 1:
            d.polygon(poly, fill=A(BRONZE, a)); d.line(UP, fill=A((240, 205, 140), a), width=5); d.line(LO, fill=A((120, 85, 45), a), width=4)
        else:
            d.line(poly, fill=A((240, 205, 140), a), width=5)

def gauge(d, cx, cy, r, val, a, lbl="PRESSURE"):   # val 1=high .. 0=low
    if a <= 0.01: return
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A((6, 30, 50), 0.95 * a), outline=A(TURQ, a), width=5)
    for i in range(9):
        ang = math.radians(210 - i * 30); col = mix(LOWC, HIGHC, i / 8)
        d.line([(cx + (r - 26) * math.cos(ang), cy - (r - 26) * math.sin(ang)), (cx + (r - 10) * math.cos(ang), cy - (r - 10) * math.sin(ang))], fill=A(col, a), width=6)
    ang = math.radians(210 - val * 240)
    d.line([(cx, cy), (cx + (r - 30) * math.cos(ang), cy - (r - 30) * math.sin(ang))], fill=A(WHITE, a), width=7)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=A(GOLD, a))
    label(d, cx - r + 22, cy + r * 0.55, "LOW", a, col=LOWC, sz=22); label(d, cx + r - 24, cy + r * 0.55, "HIGH", a, col=HIGHC, sz=22)
    label(d, cx, cy + r + 30, lbl, a, sz=24)

# ---------------------------------------------------------------- clips (t = seconds from clip start; timed to the voice)
def f_wing(t):   # abs 5.4-11.6  "A propeller blade works like a wing. As it spins, the pressure on its back face drops."
    im, d = new(t); title(d, "HOW IT HAPPENS", "A BLADE WORKS LIKE A WING", t)
    fa = fin(t, 0.2, 0.4)
    draw_foil(im, d, t, fa, field=fin(t, 2.6, 0.8), draw=clamp((t - 0.2) / 0.7), flow=fin(t, 0.6, 0.6))
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 150, 1060, "WATER FLOW", fin(t, 0.9), col=(170, 235, 250), sz=26)
    d.polygon([(258, 1052), (258, 1068), (282, 1060)], fill=A((170, 235, 250), fin(t, 0.9)))
    pill(d, 540, 600, "BACK  =  LOW PRESSURE", M(800, 30), LOWC, WHITE, fin(t, 3.0))
    pill(d, 540, 1110, "FACE  =  HIGH PRESSURE", M(800, 30), HIGHC, WHITE, fin(t, 3.4))
    gauge(d, 905, 1240, 92, 1.0 - 0.85 * fin(t, 4.1, 1.4), fin(t, 3.7), "ON THE BACK")
    return im

def f_boil(t):   # abs 11.6-15.4  "Drop pressure low enough, and water boils, even when it's cool."
    im, d = new(t); title(d, "LOW PRESSURE", "WATER BOILS - COLD", t, col=TURQ)
    a = fin(t, 0.0, 0.3); drop = fin(t, 0.15, 1.6)
    # pressure column (left)
    x0, x1, yt, yb = 120, 210, 560, 1230
    d.rounded_rectangle([x0, yt, x1, yb], radius=40, fill=A((6, 30, 50), a), outline=A(TURQ, a), width=4)
    lv = lerp(0.92, 0.12, drop); yl = yb - (yb - yt - 20) * lv
    d.rounded_rectangle([x0 + 12, yl, x1 - 12, yb - 12], radius=30, fill=A(mix(LOWC, HIGHC, lv), a))
    label(d, 165, yb + 44, "PRESSURE", a, sz=26)
    d.polygon([(165, 520 + 6 * math.sin(t * 6)), (145, 490 + 6 * math.sin(t * 6)), (185, 490 + 6 * math.sin(t * 6))], fill=A(LOWC, a * fin(t, 0.4)))
    # thermometer (right): boiling point slides down to the sea temperature
    tx, ty0, ty1 = 930, 560, 1180
    d.rounded_rectangle([tx - 34, ty0, tx + 34, ty1], radius=34, fill=A((235, 245, 250), a)); d.ellipse([tx - 60, ty1 - 30, tx + 60, ty1 + 90], fill=A((235, 245, 250), a))
    sea = 1040; d.rounded_rectangle([tx - 18, sea, tx + 18, ty1 + 10], radius=18, fill=A(HIGHC, a)); d.ellipse([tx - 44, ty1 - 14, tx + 44, ty1 + 74], fill=A(HIGHC, a))
    label(d, tx - 74, sea + 34, "SEA WATER", a, col=(255, 200, 190), sz=24, anchor="rm")
    bp = lerp(600, sea, fin(t, 0.3, 1.6))
    d.line([(tx - 64, bp), (tx + 64, bp)], fill=A(GOLD, a), width=8)
    label(d, tx - 74, bp - 40, "BOILING", a, col=GOLD, sz=24, anchor="rm"); label(d, tx - 74, bp - 12, "POINT", a, col=GOLD, sz=24, anchor="rm")
    # tank of sea water (centre) that starts to boil once the lines meet
    bx0, by0, bx1, by1 = 300, 640, 700, 1180
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=30, outline=A((200, 240, 250), a), width=5)
    d.rounded_rectangle([bx0 + 8, by0 + 70, bx1 - 8, by1 - 8], radius=24, fill=A((30, 140, 190), 0.75 * a))
    boil = fin(t, 1.8, 0.5); rr = random.Random(5)
    for i in range(46):
        x = rr.uniform(bx0 + 40, bx1 - 40); ph = rr.uniform(0, 1); sp = rr.uniform(0.6, 1.2); r0 = rr.uniform(6, 20)
        k = ((t - 1.8) * sp + ph) % 1.0
        if t < 1.8 + ph * 0.6: continue
        y = lerp(by1 - 30, by0 + 90, k); r = r0 * (0.4 + k)
        d.ellipse([x - r, y - r, x + r, y + r], outline=A(WHITE, 0.9 * boil), width=3, fill=A((220, 245, 255), 0.25 * boil))
    pill(d, 500, 1260, "BOILS WITHOUT HEAT", M(800, 30), GOLD, NAVY, fin(t, 2.0))
    return im

def _bubbles(d, t, t0, a, ncap=40):
    rr = random.Random(11)
    for i in range(ncap):
        tb = t0 + rr.uniform(0, 3.4); s0 = rr.uniform(0.06, 0.22); life = rr.uniform(0.9, 1.4); rmax = rr.uniform(9, 22); lift = rr.uniform(4, 30)
        k = (t - tb) / life
        if k < 0 or k > 1: continue
        s = s0 + 0.5 * k                                   # drifts aft along the back
        x, y = TR(s, 0.0)                                  # chord point, then up to the surface
        ux, uy = UP[min(60, int(60 * (1 - math.cos(math.pi * 0)) / 2))]
        idx = min(range(61), key=lambda j: abs(UP[j][0] - x)); sx, sy = UP[idx]
        r = rmax * (math.sin(math.pi * min(1, k / 0.85)) if k < 0.85 else 0) + (2 if k < 0.85 else 0)
        if k > 0.85: r = rmax * 0.15 * (1 - (k - 0.85) / 0.15)
        cy = sy - r - lift * k
        d.ellipse([sx - r, cy - r, sx + r, cy + r], fill=A((225, 245, 255), 0.35 * a), outline=A(WHITE, 0.95 * a), width=3)

def f_bubbles(t):   # abs 15.4-19.5  "Tiny vapour bubbles form on the blade. That's cavitation."
    im, d = new(t); title(d, "LOW PRESSURE", "VAPOUR BUBBLES FORM", t, col=TURQ)
    draw_foil(im, d, t + 6.2, 1.0, field=1.0)
    d = ImageDraw.Draw(im, "RGBA"); _bubbles(d, t, 0.2, fin(t, 0.2))
    pill(d, 540, 1120, "THIS IS CAVITATION", M(800, 36), GOLD, NAVY, fin(t, 2.4), h=66)
    label(d, 790, 640, "BUBBLES OF", fin(t, 0.9), col=ICE, sz=28); label(d, 790, 676, "WATER VAPOUR", fin(t, 0.9), col=ICE, sz=28)
    return im
ICE = (180, 235, 255)

SURF = 1150
def _metal(d, a, pits):
    d.rectangle([0, SURF, W, 1330], fill=A((120, 128, 140), a))
    for i in range(12): d.line([(0, SURF + 8 + i * 15), (W, SURF + 8 + i * 15)], fill=A((150, 158, 170), 0.35 * a), width=2)
    d.line([(0, SURF), (W, SURF)], fill=A((225, 230, 238), a), width=6)
    for (x, r, age) in pits:
        d.chord([x - r, SURF - r, x + r, SURF + r], 0, 180, fill=A((46, 50, 58), a))
        d.arc([x - r, SURF - r, x + r, SURF + r], 0, 180, fill=A((20, 22, 28), a), width=3)
    label(d, 540, 1265, "BLADE SURFACE (MAGNIFIED)", a, col=(235, 240, 245), sz=26)

def f_collapse(t):   # abs 19.5-24.6  "Then the bubbles reach higher pressure and collapse, violently, right against the metal."
    im, d = new(t); title(d, "THE DAMAGE", "BUBBLES COLLAPSE", t, col=HIGHC)
    a = fin(t, 0.0, 0.3)
    grad = Image.new("RGBA", (W, 1), 0)
    for x in range(W): grad.putpixel((x, 0), A(mix(LOWC, HIGHC, (x - 200) / 600), 0.22 * a))
    grad = grad.resize((W, SURF - 520)); im.paste(grad, (0, 520), grad); d = ImageDraw.Draw(im, "RGBA")
    label(d, 200, 560, "LOW PRESSURE", a, col=ICE, sz=28); label(d, 850, 560, "HIGHER PRESSURE", a, col=(255, 190, 180), sz=28)
    d.line([(330, 610), (760, 610)], fill=A(WHITE, 0.7 * a), width=4); d.polygon([(760, 598), (760, 622), (786, 610)], fill=A(WHITE, 0.7 * a))
    pits = []; events = [0.25 + 0.95 * i for i in range(6)]
    for i, t0 in enumerate(events):
        cx = 690 + (i % 3 - 1) * 150 + (i // 3) * 60          # collapse x
        tc = t0 + 1.55                                         # collapse moment (first ~1.8 s = 'collapse, violently')
        if t >= tc + 0.25: pits.append((cx, 22 + (i % 2) * 8, t - tc))
    _metal(d, a, pits)
    for i, t0 in enumerate(events):
        if t < t0: continue
        cx = 690 + (i % 3 - 1) * 150 + (i // 3) * 60; tc = t0 + 1.55
        if t < tc:   # grows in low pressure, drifts toward high pressure, sinking onto the surface
            k = (t - t0) / 1.55; x = lerp(130, cx, ease(k)); r = 70 * math.sin(math.pi * min(1, k * 1.25) / 2) if k < 0.8 else 70 * (1 - (k - 0.8) * 1.6)
            y = SURF - r - lerp(140, 6, k)
            d.ellipse([x - r, y - r, x + r, y + r], fill=A((225, 245, 255), 0.3 * a), outline=A(WHITE, a), width=4)
        elif t < tc + 0.3:   # micro-jet + shock ring
            k = (t - tc) / 0.3
            d.line([(cx, SURF - 60 + 50 * k), (cx, SURF - 2)], fill=A(WHITE, a * (1 - k)), width=10)
            rr = 20 + 110 * k
            d.arc([cx - rr, SURF - rr, cx + rr, SURF + rr], 180, 360, fill=A((255, 240, 200), a * (1 - k)), width=6)
            for j in range(8):
                ang = math.radians(195 + j * 21)
                d.line([(cx + 30 * math.cos(ang), SURF + 30 * math.sin(ang)), (cx + (40 + 70 * k) * math.cos(ang), SURF + (40 + 70 * k) * math.sin(ang))], fill=A(GOLD, a * (1 - k)), width=5)
    pill(d, 540, 760, "IMPLOSION: A MICRO-JET HITS THE METAL", M(800, 28), GOLD, NAVY, fin(t, 1.9))
    return im

def _blade_pts(cx=520, base=1250, top=560):
    pts_l, pts_r = [], []
    for i in range(41):
        u = i / 40; y = lerp(base, top, u)
        w = 250 * math.sin(math.pi * (0.12 + 0.88 * u)) ** 0.7 + 40 * (1 - u)
        sk = 90 * u * u
        pts_l.append((cx + sk - w * 0.55, y)); pts_r.append((cx + sk + w * 0.45, y))
    return pts_l + pts_r[::-1]
BLADE = _blade_pts()

def f_pits(t):   # abs 26.8-30.7  "Millions of tiny hammer blows eat pits into the blade. Mechanics call it cavitation burn."
    im, d = new(t); title(d, "THE DAMAGE", "CAVITATION BURN", t, col=HIGHC)
    a = fin(t, 0.0, 0.3)
    d.ellipse([430, 1170, 610, 1330], fill=A((150, 158, 168), a))
    d.polygon(BLADE, fill=A((190, 196, 204), a)); d.line(BLADE + [BLADE[0]], fill=A((235, 240, 246), a), width=5)
    for i in range(10):   # brushed shine
        y = 640 + i * 58; d.line([(400 + i * 8, y), (640 + i * 10, y - 20)], fill=A(WHITE, 0.10 * a), width=6)
    n = int(420 * ease(t / 2.6)); rr = random.Random(3)
    for i in range(n):
        u = rr.uniform(0.45, 0.95); y = lerp(1250, 560, u); w = 250 * math.sin(math.pi * (0.12 + 0.88 * u)) ** 0.7
        x = 520 + 90 * u * u - w * 0.55 + rr.uniform(0.04, 0.42) * w
        r = rr.choice([2, 3, 3, 4, 5, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=A((60, 62, 70), a)); d.arc([x - r, y - r, x + r, y + r], 200, 330, fill=A(WHITE, 0.5 * a), width=1)
    cnt = int(1_000_000 * ease(t / 2.6) ** 2)
    label(d, 880, 640, f"{cnt:,}", a, col=GOLD, sz=46); label(d, 880, 690, "TINY HAMMER", a, sz=24); label(d, 880, 718, "BLOWS", a, sz=24)
    # magnifier inset
    ma = fin(t, 0.6); mx, my, mr = 880, 960, 150
    if ma > 0.01:
        lay = Image.new("RGBA", (2 * mr, 2 * mr), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rectangle([0, 0, 2 * mr, mr + 10], fill=A((20, 70, 100), 1)); ld.rectangle([0, mr + 10, 2 * mr, 2 * mr], fill=A((130, 136, 148), 1))
        for j, (px, pr) in enumerate([(40, 22), (95, 14), (150, 30), (210, 18), (262, 24)]):
            if t > 0.8 + j * 0.25: ld.chord([px - pr, mr + 10 - pr, px + pr, mr + 10 + pr], 0, 180, fill=A((40, 42, 50), 1))
        m = Image.new("L", (2 * mr, 2 * mr), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * mr - 1, 2 * mr - 1], fill=int(255 * ma)); im.paste(lay, (mx - mr, my - mr), m)
        d = ImageDraw.Draw(im, "RGBA"); d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=A(GOLD, ma), width=7)
        d.line([(mx - 106, my + 106), (mx - 170, my + 190)], fill=A(GOLD, ma), width=16)
        label(d, mx, my + mr + 34, "PITS", ma, sz=26)
    pill(d, 540, 1300, "CAVITATION BURN", M(800, 36), HIGHC, WHITE, fin(t, 1.8), h=66)
    return im

def f_signs(t):   # abs 30.7-35.8  "You feel vibration, hear a rumble, and lose top speed at the same RPM."
    im, d = new(t); title(d, "THE SIGNS", "WHAT YOU NOTICE", t)
    rows = [(0.45, "VIBRATION", "felt through the hull"), (1.75, "A RUMBLE", "like gravel in the prop"), (2.9, "LESS SPEED", "at the same RPM")]
    for i, (t0, h1, h2) in enumerate(rows):
        a = fin(t, t0, 0.35); y0 = 540 + i * 262; sl = (1 - a) * 80
        card(d, (70 + sl, y0, 1010 + sl, y0 + 226), a)
        ix, iy = 210 + sl, y0 + 113
        if i == 0:   # shaking hull
            j = 7 * math.sin(t * 55) * a
            d.polygon([(ix - 95 + j, iy - 20), (ix + 95 + j, iy - 20), (ix + 60 + j, iy + 40), (ix - 70 + j, iy + 40)], fill=A(WHITE, a))
            d.rectangle([ix - 40 + j, iy - 55, ix + 30 + j, iy - 20], fill=A(WHITE, a))
            for s in (-1, 1): d.line([(ix + s * 118, iy - 30), (ix + s * 130, iy - 10), (ix + s * 118, iy + 10), (ix + s * 130, iy + 30)], fill=A(GOLD, a), width=5)
        elif i == 1:   # sound waves
            d.polygon([(ix - 80, iy - 26), (ix - 50, iy - 26), (ix - 10, iy - 60), (ix - 10, iy + 60), (ix - 50, iy + 26), (ix - 80, iy + 26)], fill=A(WHITE, a))
            for k in range(3):
                rr = 30 + ((t * 70 + k * 30) % 90)
                d.arc([ix - 10 - rr, iy - rr, ix - 10 + rr, iy + rr], -45, 45, fill=A(GOLD, a * (1 - (rr - 30) / 90)), width=6)
        else:   # two mini dials: RPM steady, speed sinking
            for k, (lbl, val) in enumerate([("RPM", 0.78 + 0.01 * math.sin(t * 9)), ("SPEED", 0.8 - 0.45 * fin(t, 3.3, 1.4))]):
                gx = ix - 62 + k * 124; r = 54
                d.ellipse([gx - r, iy - r, gx + r, iy + r], outline=A(WHITE, a), width=4)
                ang = math.radians(210 - val * 240); col = WHITE if k == 0 else HIGHC
                d.line([(gx, iy), (gx + 40 * math.cos(ang), iy - 40 * math.sin(ang))], fill=A(col, a), width=6)
                label(d, gx, iy + r + 18, lbl, a, sz=20)
        if a < 0.02: continue
        d.text((370 + sl, y0 + 82), h1, font=O(64), fill=A(WHITE, a), anchor="lm")
        d.text((372 + sl, y0 + 150), h2.upper(), font=M(700, 28), fill=A((170, 225, 240), a), anchor="lm")
    return im

def _mini_prop(d, cx, cy, s, a, ang, nb=3, nick=False, growth=False, cup=False):
    for b in range(nb):
        th = ang + b * 2 * math.pi / nb; pts = []
        for i in range(13):
            u = i / 12; w = 0.32 * math.sin(math.pi * u) + 0.05
            r = 0.2 + 0.8 * u
            pts.append((cx + s * (r * math.cos(th) - w * math.sin(th) * 0.9), cy + s * (r * math.sin(th) + w * math.cos(th) * 0.9)))
        for i in range(12, -1, -1):
            u = i / 12; r = 0.2 + 0.8 * u
            pts.append((cx + s * r * math.cos(th) + s * 0.04 * math.sin(th), cy + s * r * math.sin(th) - s * 0.04 * math.cos(th)))
        d.polygon(pts, fill=A(BRONZE, a), outline=A((245, 215, 150), a))
        if cup: d.line(pts[10:13], fill=A(GOLD, a), width=6)
        if nick and b == 0:
            px, py = cx + s * 0.8 * math.cos(th + 0.15), cy + s * 0.8 * math.sin(th + 0.15)
            d.polygon([(px, py), (px + 22 * math.cos(th + 1.9), py + 22 * math.sin(th + 1.9)), (px + 18 * math.cos(th + 0.6), py + 18 * math.sin(th + 0.6))], fill=A((8, 40, 64), a))
        if growth:
            rr = random.Random(b)
            for _ in range(26):
                u = rr.uniform(0.3, 0.95); off = rr.uniform(-0.18, 0.2)
                gx = cx + s * (u * math.cos(th) - off * math.sin(th)); gy = cy + s * (u * math.sin(th) + off * math.cos(th)); g = rr.randint(4, 9)
                d.ellipse([gx - g, gy - g, gx + g, gy + g], fill=A(GREEN, a * 0.9))
    d.ellipse([cx - s * 0.22, cy - s * 0.22, cx + s * 0.22, cy + s * 0.22], fill=A((150, 115, 70), a))

def f_causes(t):   # abs 35.8-38.6 (t 0-2.8) and 40.3-41.8 (t 4.5-6.0)  "Common causes: nicked or bent blades, marine growth, or the wrong pitch for your boat."
    im, d = new(t); title(d, "THE CAUSES", "WHY IT HAPPENS", t)
    rows = [(1.15, "NICKED OR BENT", "BLADES", dict(nick=True)), (2.55, "MARINE", "GROWTH", dict(growth=True)), (4.55, "WRONG PITCH", "FOR YOUR BOAT", {})]
    for i, (t0, h1, h2, kw) in enumerate(rows):
        a = fin(t, t0, 0.35); y0 = 540 + i * 262; sl = (1 - a) * 80
        card(d, (70 + sl, y0, 1010 + sl, y0 + 226), a, col=HIGHC)
        _mini_prop(d, 205 + sl, y0 + 113, 92, a, t * 0.6 + i, **kw)
        if i == 2:   # pitch arrows: twisting angle
            for k, ang in enumerate((25, 45)):
                r = math.radians(ang); col = GREEN if k == 0 else HIGHC
                d.line([(860 + sl, y0 + 170), (860 + sl + 110 * math.cos(r), y0 + 170 - 110 * math.sin(r))], fill=A(col, a), width=6)
            d.line([(840 + sl, y0 + 170), (990 + sl, y0 + 170)], fill=A(WHITE, a), width=3)
        if a < 0.02: continue
        d.text((340 + sl, y0 + 82), h1, font=O(60), fill=A(WHITE, a), anchor="lm")
        d.text((342 + sl, y0 + 152), h2, font=M(800, 34), fill=A((255, 190, 180), a), anchor="lm")
    return im

def f_fix(t):   # abs 43.6-52.4  "...have the prop checked by a specialist. And if a clean, undamaged prop still cavitates, a different prop design can solve it."
    im, d = new(t); title(d, "THE FIX", "STOP THE RUMBLE", t, col=GREEN)
    items = [(0.25, "KEEP BLADES SMOOTH & CLEAN"), (1.6, "PROP CHECKED BY A SPECIALIST"), (6.0, "RIGHT PROP DESIGN FOR THE BOAT")]
    card(d, (70, 520, 1010, 900), fin(t, 0.1), col=GREEN)
    for i, (t0, s) in enumerate(items):
        a = fin(t, t0, 0.3); y = 580 + i * 112
        f = M(800, 34)
        while f.getlength(s) > 760: f = M(800, f.size - 2)
        if a > 0.01: tick(d, 140, y + 8, a, s=0.9 + 0.2 * (1 - a)); d.text((196, y + 8), s, font=f, fill=A(WHITE, a), anchor="lm")
    # 'still cavitating?' -> different designs cycle in, then the right one is ticked
    qa = fin(t, 3.0, 0.4)
    label(d, 540, 960, "CLEAN PROP STILL CAVITATING?", qa, col=GOLD, sz=34)
    designs = [("3-BLADE", 3, False), ("4-BLADE", 4, False), ("CUPPED", 4, True)]
    for k, (nm, nb, cup) in enumerate(designs):
        a = fin(t, 3.6 + k * 0.6, 0.35) * qa; cx = 220 + k * 320
        card(d, (cx - 135, 1010, cx + 135, 1300), a, col=TURQ if k < 2 else GOLD)
        _mini_prop(d, cx, 1135, 95, a, t * 1.4 + k, nb=nb, cup=cup)
        label(d, cx, 1265, nm, a, sz=28)
    tick(d, 860 + 125, 1030, fin(t, 6.1, 0.3), col=GREEN, s=0.9)
    return im

CLIPS = {"wing": (f_wing, 6.4), "boil": (f_boil, 4.0), "bubbles": (f_bubbles, 4.3), "collapse": (f_collapse, 5.3),
         "pits": (f_pits, 4.1), "signs": (f_signs, 5.3), "causes": (f_causes, 6.2), "fix": (f_fix, 9.0)}

def render(outdir, name):
    fn, dur = CLIPS[name]; out = os.path.join(outdir, f"cav_{name}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)): p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait(); print("->", out)

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == "--still":
        nm, tt = sys.argv[3], float(sys.argv[4]); CLIPS[nm][0](tt).convert("RGB").save(os.path.join(outdir, f"still_{nm}_{tt}.png"))
    else:
        for nm in (sys.argv[2:] or CLIPS): render(outdir, nm)
