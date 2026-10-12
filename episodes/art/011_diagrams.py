"""Illustration for episode 011 (single vs twin engines): top-down 'spin in place' with twin engines.
New look: chalkboard (slate-green board, hand-drawn chalk strokes) - previous looks: blueprint, amber, dusk,
teal underwater, violet studio, thermal, paper-cut, cream nautical chart. Run from repo root:
python3 episodes/art/011_diagrams.py"""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

random.seed(11)
CHALK = (240, 242, 236); CH_TURQ = (120, 226, 230); CH_CORAL = (255, 150, 135); CH_GOLD = (250, 214, 140)

def board():
    arr = vgrad([(0, (34, 52, 46)), (0.5, (40, 62, 54)), (1, (28, 44, 40))])
    arr += np.random.default_rng(3).normal(0, 5, arr.shape)              # board grain
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    sm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); s = ImageDraw.Draw(sm)  # old erased smudges
    for _ in range(14):
        x, y = random.randint(-100, W), random.randint(0, H); w = random.randint(250, 600)
        s.ellipse([x, y, x + w, y + random.randint(60, 160)], fill=(220, 230, 220, 14))
    im.alpha_composite(sm.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(im, "RGBA")                                       # wooden frame edge at the bottom (chalk tray)
    d.rectangle([0, H - 70, W, H], fill=(96, 66, 40, 255)); d.rectangle([0, H - 70, W, H - 62], fill=(130, 92, 58, 255))
    return im

def chalk_line(lay, pts, col=CHALK, w=9, passes=4, jit=2.2):
    d = ImageDraw.Draw(lay)
    for p in range(passes):
        q = [(x + random.uniform(-jit, jit), y + random.uniform(-jit, jit)) for x, y in pts]
        d.line(q, fill=col + (random.randint(120, 190),), width=max(2, w - p * 2), joint="curve")

def chalk_poly(lay, pts, col=CHALK, w=9):
    chalk_line(lay, pts + [pts[0]], col, w)

def chalk_fill(lay, pts, col, a=70):
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(m).polygon(pts, fill=col + (a,))
    lay.alpha_composite(m)

def grain(lay):  # break up strokes like chalk on a rough board
    a = np.array(lay); noise = np.random.default_rng(7).random(a.shape[:2])
    a[..., 3] = (a[..., 3] * np.clip(noise * 1.6, 0.25, 1.0)).astype(np.uint8)
    return Image.fromarray(a)

def arrow(lay, x0, y0, x1, y1, col, w=12, head=34):
    chalk_line(lay, [(x0, y0), (x1, y1)], col, w)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (2.6, -2.6):
        chalk_line(lay, [(x1, y1), (x1 + head * math.cos(ang + s), y1 + head * math.sin(ang + s))], col, w)

def hull_pts(cx, top, bot, half):
    pts = []
    for i in range(0, 41):                     # bow curve (pointed) -> straight sides -> square transom
        t = i / 40; y = top + t * (bot - top) * 0.55
        x = half * math.sin(t * math.pi / 2) ** 0.6
        pts.append((cx + x, y))
    pts += [(cx + half, bot), (cx - half, bot)]
    for i in range(40, -1, -1):
        t = i / 40; y = top + t * (bot - top) * 0.55
        pts.append((cx - half * math.sin(t * math.pi / 2) ** 0.6, y))
    return pts

def spin():
    im = board(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, top, bot, half = 540, 660, 1220, 150
    hp = hull_pts(cx, top, bot, half)
    chalk_fill(lay, hp, (230, 236, 230), 38); chalk_poly(lay, hp, CHALK, 10)
    chalk_poly(lay, [(cx - 80, 900), (cx + 80, 900), (cx + 80, 1010), (cx - 80, 1010)], CHALK, 6)   # console
    chalk_line(lay, [(cx - 60, 880), (cx, 840), (cx + 60, 880)], CHALK, 5)                           # windscreen
    for ex in (cx - 70, cx + 70):                                                                      # twin engines on transom
        chalk_poly(lay, [(ex - 32, bot - 6), (ex + 32, bot - 6), (ex + 26, bot + 62), (ex - 26, bot + 62)], CH_GOLD, 7)
    arrow(lay, cx - 70, bot + 60, cx - 70, bot - 190, CH_TURQ, 14, 40)       # port engine: FORWARD thrust (pushes boat ahead)
    arrow(lay, cx + 70, bot - 190, cx + 70, bot + 60, CH_CORAL, 14, 40)      # starboard engine: REVERSE
    # rotation arc around the boat (clockwise from above: bow swings to starboard, toward the reversed engine)
    R = 360; c0 = (cx, 940); arc = [(c0[0] + R * math.cos(math.radians(a)), c0[1] + R * 1.05 * math.sin(math.radians(a))) for a in range(-150, -40, 3)]
    chalk_line(lay, arc, CHALK, 11)
    xe, ye = arc[-1]; xp, yp = arc[-3]; ang = math.atan2(ye - yp, xe - xp)
    for s in (2.6, -2.6): chalk_line(lay, [(xe, ye), (xe + 44 * math.cos(ang + s), ye + 44 * math.sin(ang + s))], CHALK, 11)
    arc2 = [(c0[0] + R * math.cos(math.radians(a)), c0[1] + R * 1.05 * math.sin(math.radians(a))) for a in range(30, 140, 3)]
    chalk_line(lay, arc2, CHALK, 11)
    xe, ye = arc2[-1]; xp, yp = arc2[-3]; ang = math.atan2(ye - yp, xe - xp)
    for s in (2.6, -2.6): chalk_line(lay, [(xe, ye), (xe + 44 * math.cos(ang + s), ye + 44 * math.sin(ang + s))], CHALK, 11)
    lay = grain(lay); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6)))
    print(save(im, "ep011-spin"), "points: fwd", (cx - 70, bot - 120), "rev", (cx + 70, bot - 60), "bow", (cx, top + 10))

def single_vs_twin():
    """Two small top-view sterns side by side: one engine (A) vs two engines (B)."""
    im = board(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for cx, n, col in ((300, 1, CH_GOLD), (780, 2, CH_TURQ)):
        top, bot, half = 700, 1190, 125
        hp = hull_pts(cx, top, bot, half); chalk_fill(lay, hp, (230, 236, 230), 34); chalk_poly(lay, hp, CHALK, 9)
        chalk_poly(lay, [(cx - 60, 920), (cx + 60, 920), (cx + 60, 1010), (cx - 60, 1010)], CHALK, 5)
        xs = [cx] if n == 1 else [cx - 58, cx + 58]
        for ex in xs:
            chalk_poly(lay, [(ex - 30, bot - 6), (ex + 30, bot - 6), (ex + 24, bot + 58), (ex - 24, bot + 58)], col, 7)
            chalk_line(lay, [(ex, bot + 70), (ex, bot + 120)], col, 7)
    lay = grain(lay); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6)))
    print(save(im, "ep011-ab"), "engines A", (300, 1220), "B", (722, 1220), (838, 1220))

spin(); single_vs_twin()
