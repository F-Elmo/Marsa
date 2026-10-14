"""Illustrations for episode 012 (trim tabs explained).
New look: engineer's graph-paper sketch (warm white squared paper, navy felt-tip outlines, highlighter fills)
- previous looks: blueprint, amber, dusk, teal underwater, violet studio, thermal, paper-cut, cream nautical chart,
chalkboard. Run from repo root: python3 episodes/art/012_diagrams.py"""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

random.seed(12)
INKC = (22, 38, 84); HL_TURQ = (64, 206, 214); HL_CORAL = (246, 108, 92); HL_GOLD = (244, 200, 92); HULL = (250, 252, 255)

def paper():
    arr = vgrad([(0, (250, 248, 241)), (1, (241, 238, 228))])
    arr += np.random.default_rng(5).normal(0, 2.2, arr.shape)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 30): d.line([(x, 0), (x, H)], fill=(110, 160, 200, 70 if x % 150 else 130), width=1)
    for y in range(0, H, 30): d.line([(0, y), (W, y)], fill=(110, 160, 200, 70 if y % 150 else 130), width=1)
    d.line([(90, 0), (90, H)], fill=(230, 120, 120, 120), width=3)              # margin line
    return im

def pen(lay, pts, col=INKC, w=8, passes=2, jit=1.2, closed=False):
    d = ImageDraw.Draw(lay)
    if closed: pts = pts + [pts[0]]
    for p in range(passes):
        q = [(x + random.uniform(-jit, jit), y + random.uniform(-jit, jit)) for x, y in pts]
        d.line(q, fill=col + (235 if p == 0 else 120,), width=w if p == 0 else max(2, w // 2), joint="curve")

def marker_fill(lay, pts, col, a=110):
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(m).polygon(pts, fill=col + (a,))
    lay.alpha_composite(m)

def arrow(lay, pts, col, w=14, head=40):
    pen(lay, pts, col, w, passes=1)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]; ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + head * 0.4 * math.cos(ang), y1 + head * 0.4 * math.sin(ang))
    l = (x1 + head * math.cos(ang + 2.6), y1 + head * math.sin(ang + 2.6)); r = (x1 + head * math.cos(ang - 2.6), y1 + head * math.sin(ang - 2.6))
    ImageDraw.Draw(lay).polygon([tip, l, r], fill=col + (255,))

def rot(pts, cx, cy, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

def hull_side(x0, x1, deck, keel):
    """Simple sport-cruiser side profile, bow left, flat transom right. Returns (hull, cabin, windows)."""
    L = x1 - x0
    hull = [(x0, deck - 30), (x0 + L * 0.08, deck), (x1, deck), (x1, keel - 10), (x1 - 8, keel),
            (x0 + L * 0.45, keel), (x0 + L * 0.2, keel - 30), (x0 + L * 0.08, deck + (keel - deck) * 0.45)]
    cabin = [(x0 + L * 0.30, deck), (x0 + L * 0.40, deck - 85), (x0 + L * 0.78, deck - 95), (x0 + L * 0.80, deck)]
    win = [(x0 + L * 0.42, deck - 70), (x0 + L * 0.47, deck - 72), (x0 + L * 0.47, deck - 22), (x0 + L * 0.37, deck - 22)]
    return hull, cabin, win

def water(lay, y, col=HL_TURQ):
    marker_fill(lay, [(90, y), (W, y), (W, H), (90, H)], col, 60)
    pts = [(90 + i * 20, y + 7 * math.sin(i * 0.7)) for i in range(0, 50)]
    pen(lay, pts, (20, 140, 160), 6, passes=1)

def boat(lay, ang, cx=560, cy=980, tab=False):
    hull, cabin, win = hull_side(150, 960, 940, 1030)
    hull, cabin, win = (rot(p, cx, cy, ang) for p in (hull, cabin, win))
    marker_fill(lay, hull, HULL, 255); marker_fill(lay, cabin, HULL, 255)
    pen(lay, hull, closed=True); pen(lay, cabin, closed=True)
    marker_fill(lay, win, (60, 90, 130), 200)
    stripe = rot([(240, 965), (960, 965)], cx, cy, ang); pen(lay, stripe, HL_GOLD, 10, passes=1)
    if tab:   # tab hinged at bottom of transom, deflected down ~20 degrees
        hx, hy = rot([(958, 1028)], cx, cy, ang)[0]; t = rot([(hx, hy), (hx + 70, hy + 26)], hx, hy, 0)
        pen(lay, t, HL_CORAL, 14, passes=1)
    return hull

def finish(im, lay, name):
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.5))); print(save(im, name))

# 1) close-up cross-section of the transom bottom: water hits the lowered tab and pushes the stern UP
def tab_closeup():
    im = paper(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    water(lay, 820)
    hull = [(90, 700), (720, 700), (720, 1040), (90, 1110)]          # stern section, transom at x=720
    marker_fill(lay, hull, HULL, 255); pen(lay, hull[1:] + [hull[0]], w=10)
    pen(lay, [(90, 760), (720, 760)], HL_GOLD, 10, passes=1)
    hinge = (720, 1040); tip = (720 + 200 * math.cos(math.radians(22)), 1040 + 200 * math.sin(math.radians(22)))
    pen(lay, [hinge, tip], HL_CORAL, 22, passes=1)                   # the tab plate
    ImageDraw.Draw(lay).ellipse([706, 1026, 734, 1054], fill=INKC + (255,))
    pen(lay, [(740, 760), (775, 760), (812, 1040)], (90, 100, 120), 12, passes=1)   # actuator ram from transom to tab
    for off in (22, 80, 140):                                        # streamlines hug the hull bottom, then the tab bends them down
        yb = lambda x: 1110 - (1110 - 1040) * (x - 90) / 630 + off
        dx, dy = math.cos(math.radians(30)), math.sin(math.radians(30))
        pts = [(110, yb(110)), (400, yb(400)), (690, yb(690)), (690 + 240 * dx, yb(690) + 240 * dy + off * 0.3)]
        arrow(lay, pts, (14, 150, 170), 9, 30)
    arrow(lay, [(800, 1320), (800, 1150)], HL_CORAL, 18, 52)          # lift on the tab -> stern up
    arrow(lay, [(560, 980), (560, 820)], HL_CORAL, 18, 52)
    finish(im, lay, "ep012-flow")

# 2) side profile: bow-high (no tabs, ghost) vs level (tabs down)
def profile():
    im = paper(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    water(lay, 1010)
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    h = hull_side(150, 960, 940, 1030)[0]; h = rot(h, 560, 980, 9)
    marker_fill(ghost, h, (200, 206, 220), 90); pen(ghost, h, (120, 132, 156), 6, passes=1, closed=True)
    a = np.array(ghost); a[..., 3] = (a[..., 3] * 0.8).astype(np.uint8); lay.alpha_composite(Image.fromarray(a))
    boat(lay, 1.5, tab=True)
    arrow(lay, [(250, 700), (215, 760), (215, 820)], HL_CORAL, 16, 48)    # bow comes down
    arrow(lay, [(905, 1230), (905, 1110)], HL_CORAL, 16, 48)              # stern pushed up
    finish(im, lay, "ep012-profile")

# 3) rear view: boat leaning to starboard (right); lower the tab on the LOW side -> it lifts level
def lean():
    im = paper(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    water(lay, 1060)
    cx, cy, ang = 540, 1000, 7          # positive = clockwise = right side low
    hull = [(250, 860), (830, 860), (830, 980), (700, 1080), (540, 1120), (380, 1080), (250, 980)]
    top = [(330, 860), (360, 760), (720, 760), (750, 860)]
    wins = [(385, 790), (695, 790), (712, 840), (368, 840)]
    hull, top, wins = (rot(p, cx, cy, ang) for p in (hull, top, wins))
    marker_fill(lay, hull, HULL, 255); marker_fill(lay, top, HULL, 255); pen(lay, hull, closed=True); pen(lay, top, closed=True)
    marker_fill(lay, wins, (60, 90, 130), 200)
    pen(lay, rot([(250, 905), (830, 905)], cx, cy, ang), HL_GOLD, 10, passes=1)
    lt = rot([(300, 1020), (430, 1020)], cx, cy, ang); rt = rot([(650, 1020), (780, 1020)], cx, cy, ang)
    pen(lay, lt, (120, 130, 150), 14, passes=1)                       # port tab: up
    rt2 = [rt[0], (rt[1][0], rt[1][1] + 40)]; pen(lay, rt2, HL_CORAL, 18, passes=1)   # starboard (low side) tab: down
    arrow(lay, [(760, 1260), (760, 1120)], HL_CORAL, 18, 52)          # lift on the low side
    # level reference line
    for x in range(160, 960, 50): pen(lay, [(x, 700), (x + 25, 700)], (120, 130, 150), 5, passes=1)
    finish(im, lay, "ep012-lean")

tab_closeup(); profile(); lean()
