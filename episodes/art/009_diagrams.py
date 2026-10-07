"""Illustrations for episode 009 (outboard vs inboard). Run from repo root:
    python3 episodes/art/009_diagrams.py
New look for this episode: layered PAPER-CUT craft style (stacked wavy paper sea strips with soft drop shadows,
warm sand/peach paper sky, paper grain). Previous looks: blueprint, amber heat, dusk, deep teal underwater,
night indigo, thermal false colour, noon daylight."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

SKY_T = (255, 226, 190); SKY_B = (255, 244, 226); SUNC = (255, 170, 90)
SEA = [(120, 222, 222), (60, 196, 204), (22, 160, 184), (12, 118, 156), (8, 78, 122), (6, 46, 86)]
SAND = (238, 214, 168); SAND_D = (210, 180, 128)
HULL = (252, 250, 245); HULL_S = (226, 230, 236); DARK = (28, 44, 66); RED = (196, 70, 60)
ENG = (230, 120, 50); ENG_D = (160, 80, 30)
rnd = random.Random(9)

def paper(im, fn, off=(5, 9), blur=7, alpha=120):
    """draw fn(d) on a layer, cast a soft paper drop shadow, composite."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay))
    sh = Image.new("RGBA", (W, H), (20, 30, 50, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha / 255)))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(sh, off); im.alpha_composite(lay)

def wave(y, amp, per, ph):
    return [(x, y + amp * math.sin(x / per + ph) + amp * 0.4 * math.sin(x / (per * 0.43) + ph * 2)) for x in range(-20, W + 30, 10)]

def grain(im, k=7):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    n = np.random.default_rng(5).integers(-k, k + 1, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8)).convert("RGBA")

def scene_bg(wl, sun=(800, 330), bottom=None):
    arr = vgrad([(0, SKY_T), (wl / H, SKY_B)]); im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    if sun: paper(im, lambda g: g.ellipse([sun[0] - 95, sun[1] - 95, sun[0] + 95, sun[1] + 95], fill=SUNC + (255,)), alpha=60)
    for (x, y, s) in ((200, 250, 1.0), (620, 180, 0.7)):  # paper clouds
        paper(im, lambda g, x=x, y=y, s=s: [g.ellipse([x + dx * s, y + dy * s, x + (dx + w) * s, y + (dy + h) * s], fill=(255, 255, 255, 255))
                                             for dx, dy, w, h in ((0, 20, 120, 60), (60, 0, 110, 80), (130, 22, 110, 58))], alpha=50)
    return im

def sea_layers(im, wl, n=6, step=None, bottom=None):
    step = step or (H - wl) / n
    for i in range(n):
        y = wl + i * step; c = SEA[min(i, len(SEA) - 1)]
        pts = wave(y, 10 + i * 2, 70 + i * 13, i * 1.7)
        paper(im, lambda g, pts=pts, c=c: g.polygon(pts + [(W + 30, H + 10), (-20, H + 10)], fill=c + (255,)), off=(0, -6), alpha=90)
    if bottom:
        pts = wave(bottom, 18, 120, 0.5)
        paper(im, lambda g: g.polygon(pts + [(W + 30, H + 10), (-20, H + 10)], fill=SAND + (255,)), off=(0, -6), alpha=90)

def front_waves(im, wl, alpha_fill=170):
    """translucent paper strip in front of the hull at the waterline."""
    pts = wave(wl + 6, 9, 60, 2.2)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    g.polygon(pts + [(W + 30, wl + 40), (-20, wl + 40)], fill=SEA[0] + (alpha_fill,)); im.alpha_composite(lay)

def T(pts, o, s, rot=0.0, piv=(0, 0)):
    ca, sa = math.cos(rot), math.sin(rot); out = []
    for x, y in pts:
        x -= piv[0]; y -= piv[1]; x, y = x * ca - y * sa + piv[0], x * sa + y * ca + piv[1]
        out.append((o[0] + x * s, o[1] + y * s))
    return out

def outboard(g, o, s, tilt=0.0):
    """outboard motor; local origin = transom mounting bracket top, +y down. tilt in radians (positive = tilts up/back)."""
    P = lambda pts: T(pts, o, s, -tilt, (0, 0))
    g.polygon(P([(-6, -20), (16, -20), (16, 30), (-6, 30)]), fill=(70, 78, 92, 255))                       # bracket
    g.rounded_rectangle  # (keep linter quiet)
    g.polygon(P([(4, -10), (40, -14), (78, -70), (90, -150), (60, -190), (0, -192), (-12, -150), (-6, -60)]), fill=(245, 246, 248, 255))  # cowling
    g.polygon(P([(-6, -100), (88, -110), (90, -120), (-10, -110)]), fill=GOLD + (255,))                     # stripe
    g.polygon(P([(6, -12), (40, -14), (44, 150), (16, 156)]), fill=(52, 60, 74, 255))                     # midsection leg
    g.polygon(P([(0, 120), (70, 116), (72, 126), (0, 130)]), fill=(80, 90, 104, 255))                     # cavitation plate
    g.polygon(P([(6, 156), (56, 150), (64, 176), (30, 186), (8, 176)]), fill=(52, 60, 74, 255))           # gearcase
    g.polygon(P([(26, 186), (40, 186), (36, 226), (28, 226)]), fill=(52, 60, 74, 255))                    # skeg
    c = P([(-14, 166)])[0]                                                                              # prop hub
    r = 9 * s
    for k in range(3):
        a = k * 2.1 + 0.4
        g.ellipse([c[0] + math.cos(a) * 22 * s - 18 * s, c[1] + math.sin(a) * 26 * s - 10 * s, c[0] + math.cos(a) * 22 * s + 18 * s, c[1] + math.sin(a) * 26 * s + 10 * s], fill=(190, 198, 210, 255))
    g.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(120, 128, 140, 255))
    return {"cowling": P([(40, -110)])[0], "leg": P([(26, 60)])[0], "prop": c, "bracket": P([(5, 5)])[0]}

def console_boat(g, o, s):
    """open centre-console boat, bow left; local transom top at (0,0); waterline at local y=110."""
    P = lambda pts: T(pts, o, s)
    g.polygon(P([(-720, -40), (0, 0), (0, 150), (-260, 158), (-480, 150), (-610, 90)]), fill=HULL + (255,))
    g.polygon(P([(-560, 112), (0, 112), (0, 150), (-260, 158), (-480, 150), (-580, 122)]), fill=DARK + (255,))  # bottom paint
    g.line(P([(-710, -30), (0, 8)]), fill=NAVY + (255,), width=max(3, int(10 * s)))
    g.line(P([(-640, 30), (0, 48)]), fill=GOLD + (255,), width=max(2, int(5 * s)))
    g.polygon(P([(-380, -30), (-260, -24), (-250, -120), (-372, -126)]), fill=HULL_S + (255,))               # console
    g.polygon(P([(-372, -126), (-250, -120), (-268, -170), (-352, -172)]), fill=(120, 190, 220, 220))       # windscreen
    g.line(P([(-420, -128), (-420, -250)]), fill=(200, 205, 212, 255), width=max(3, int(8 * s)))            # t-top posts
    g.line(P([(-200, -118), (-200, -250)]), fill=(200, 205, 212, 255), width=max(3, int(8 * s)))
    g.polygon(P([(-460, -250), (-160, -250), (-170, -272), (-450, -272)]), fill=HULL + (255,))
    for x in (-150, -100): g.line(P([(x, -10), (x, -60)]), fill=(200, 205, 212, 255), width=max(2, int(5 * s)))  # rails
    g.line(P([(-640, -40), (-20, -40)]), fill=(200, 205, 212, 255), width=max(2, int(5 * s)))
    return {"cockpit": P([(-150, -30)])[0], "console": P([(-310, -80)])[0], "bow": P([(-700, -30)])[0]}

def cruiser(g, o, s, cut=False):
    """inboard motor cruiser, bow left; local transom top (0,0); waterline at local y=120."""
    P = lambda pts: T(pts, o, s)
    g.polygon(P([(-800, -70), (0, -20), (0, 140), (-300, 172), (-560, 160), (-700, 70)]), fill=HULL + (255,))
    g.polygon(P([(-640, 120), (0, 120), (0, 140), (-300, 172), (-560, 160), (-660, 128)]), fill=DARK + (255,))
    g.line(P([(-790, -60), (0, -12)]), fill=NAVY + (255,), width=max(3, int(10 * s)))
    g.line(P([(-720, 20), (0, 40)]), fill=GOLD + (255,), width=max(2, int(5 * s)))
    g.polygon(P([(-560, -46), (-470, -150), (-110, -150), (-80, -28)]), fill=HULL + (255,))                 # superstructure
    g.polygon(P([(-520, -60), (-458, -132), (-300, -132), (-300, -58)]), fill=DARK + (255,))
    g.polygon(P([(-280, -132), (-124, -132), (-104, -56), (-280, -56)]), fill=DARK + (255,))
    g.polygon(P([(-440, -150), (-410, -190), (-150, -190), (-140, -150)]), fill=HULL + (255,))              # flybridge
    for x in (-640, -590): g.ellipse(P([(x, 0), (x + 26, 16)]), fill=DARK + (255,))
    g.polygon(P([(0, 70), (70, 70), (70, 86), (0, 86)]), fill=(214, 186, 140, 255))                        # swim platform (teak)
    pts = {"platform": P([(40, 72)])[0], "saloon": P([(-300, -100)])[0], "bow": P([(-780, -60)])[0]}
    if cut:
        g.rounded_rectangle(P([(-500, 34), (-60, 34)]) [0] + P([(-60, 150)])[0], radius=int(16 * s), fill=(250, 244, 230, 245), outline=NAVY + (255,), width=max(3, int(6 * s)))
    return pts

def engine_block(g, c, s):
    x, y = c
    g.rounded_rectangle([x - 90 * s, y - 50 * s, x + 90 * s, y + 40 * s], radius=int(12 * s), fill=ENG + (255,), outline=ENG_D + (255,), width=max(2, int(5 * s)))
    g.rounded_rectangle([x - 70 * s, y - 82 * s, x + 70 * s, y - 50 * s], radius=int(8 * s), fill=ENG_D + (255,))
    for k in range(4): g.ellipse([x - 60 * s + k * 36 * s, y - 76 * s, x - 40 * s + k * 36 * s, y - 56 * s], fill=(250, 210, 160, 255))
    g.rounded_rectangle([x + 90 * s, y - 20 * s, x + 120 * s, y + 20 * s], radius=int(6 * s), fill=(70, 78, 92, 255))  # gearbox

def shaft_line(g, a, b, prop, s, rudder=None):
    g.line([a, b], fill=(150, 160, 175, 255), width=max(3, int(9 * s)))
    g.line([(b[0] - 40 * s, b[1] - 6 * s), (b[0] - 40 * s, b[1] - 46 * s)], fill=(110, 118, 130, 255), width=max(3, int(8 * s)))  # strut
    for k in range(3):
        a_ = k * 2.1 + 0.3
        g.ellipse([prop[0] + math.cos(a_) * 16 * s - 9 * s, prop[1] + math.sin(a_) * 26 * s - 16 * s, prop[0] + math.cos(a_) * 16 * s + 9 * s, prop[1] + math.sin(a_) * 26 * s + 16 * s], fill=(214, 168, 90, 255))
    g.ellipse([prop[0] - 8 * s, prop[1] - 8 * s, prop[0] + 8 * s, prop[1] + 8 * s], fill=(150, 110, 50, 255))
    if rudder:
        x, y = rudder; g.polygon([(x, y), (x + 34 * s, y), (x + 28 * s, y + 80 * s), (x + 4 * s, y + 80 * s)], fill=(70, 78, 92, 255))

pts = {}
# ---------------------------------------------------------------- 1) HOOK: two boats, outboard on top, inboard cut-away below
WLa, WLb = 900, 1200
im = scene_bg(WLa, sun=(930, 250))
sea_layers(im, WLa, n=6, step=150)
o1 = (760, WLa - 108); s1 = 0.78
paper(im, lambda g: console_boat(g, o1, s1));
paper(im, lambda g: pts.setdefault("_ob", outboard(g, (o1[0] + 8, o1[1] + 4), 0.78)))
front_waves(im, WLa)
o2 = (840, WLb - 120 * 0.8); s2 = 0.8
paper(im, lambda g: cruiser(g, o2, s2, cut=True))
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
ec = T([(-300, 104)], o2, s2)[0]; engine_block(g, ec, 0.62)
shaft_line(g, (ec[0] + 70, ec[1] + 6), T([(-90, 182)], o2, s2)[0], T([(-80, 186)], o2, s2)[0], 0.8, rudder=T([(-50, 150)], o2, s2)[0])
im.alpha_composite(lay)
im = grain(im)
pts["ep009-hook"] = {"outboard": [int(pts["_ob"]["cowling"][0]), int(pts["_ob"]["cowling"][1])], "inboard_engine": [int(ec[0]), int(ec[1])]}
save(im, "ep009-hook")

# ---------------------------------------------------------------- 2) OUTBOARD close: big stern view of console boat with outboard
WL = 1080
im = scene_bg(WL, sun=(240, 380)); sea_layers(im, WL, n=5, step=180)
o = (640, WL - 110 * 1.25); s = 1.25
paper(im, lambda g: console_boat(g, o, s))
ob = {}
paper(im, lambda g: ob.update(outboard(g, (o[0] + 10, o[1] + 6), 1.25)))
front_waves(im, WL, 140)
im = grain(im)
pts["ep009-outboard"] = {k: [int(v[0]), int(v[1])] for k, v in ob.items()}
pts["ep009-outboard"]["cockpit"] = [int(T([(-150, -20)], o, s)[0][0]), int(T([(-150, -20)], o, s)[0][1])]
save(im, "ep009-outboard")

# ---------------------------------------------------------------- 3) TILT: shallow sandy bay, outboard tilted up, sand close below
WL = 980
im = scene_bg(WL, sun=(850, 330))
sea_layers(im, WL, n=2, step=60)
paper(im, lambda g: g.polygon(wave(WL + 230, 22, 140, 0.8) + [(W + 30, H + 10), (-20, H + 10)], fill=SAND + (255,)), off=(0, -6), alpha=90)
paper(im, lambda g: g.polygon(wave(WL + 330, 18, 100, 2.0) + [(W + 30, H + 10), (-20, H + 10)], fill=SAND_D + (255,)), off=(0, -6), alpha=70)
for k in range(9):  # paper shells / coral bits on the sand
    x = rnd.uniform(80, 900); y = rnd.uniform(WL + 280, WL + 420); r = rnd.uniform(10, 20)
    paper(im, lambda g, x=x, y=y, r=r: g.pieslice([x - r, y - r, x + r, y + r], 200, 340, fill=(255, 236, 220, 255)), alpha=60, blur=3, off=(2, 3))
o = (700, WL - 110 * 1.1); s = 1.1
paper(im, lambda g: console_boat(g, o, s))
ob = {}
paper(im, lambda g: ob.update(outboard(g, (o[0] + 10, o[1] + 6), 1.1, tilt=math.radians(78))))
front_waves(im, WL, 130)
im = grain(im)
pts["ep009-tilt"] = {k: [int(v[0]), int(v[1])] for k, v in ob.items()}
pts["ep009-tilt"]["sand"] = [300, WL + 300]
save(im, "ep009-tilt")

# ---------------------------------------------------------------- 4) INBOARD cut-away: cruiser, engine low & centred, shaft, prop, rudder
WL = 1100
im = scene_bg(WL, sun=(860, 300)); sea_layers(im, WL, n=5, step=170)
o = (880, WL - 120 * 1.0); s = 1.0
cp = {}
paper(im, lambda g: cp.update(cruiser(g, o, s, cut=True)))
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
ec = T([(-300, 104)], o, s)[0]; engine_block(g, ec, 0.8)
sb = T([(-90, 186)], o, s)[0]; pr = T([(-78, 192)], o, s)[0]
shaft_line(g, (ec[0] + 96, ec[1] + 4), sb, pr, 1.0, rudder=T([(-46, 150)], o, s)[0])
im.alpha_composite(lay); front_waves(im, WL, 120); im = grain(im)
pts["ep009-inboard"] = {"engine": [int(ec[0]), int(ec[1])], "shaft": [int((ec[0] + sb[0]) / 2 + 40), int((ec[1] + sb[1]) / 2 + 6)], "prop": [int(pr[0]), int(pr[1])],
                        "platform": [int(cp["platform"][0]), int(cp["platform"][1])], "saloon": [int(cp["saloon"][0]), int(cp["saloon"][1])]}
save(im, "ep009-inboard")

# ---------------------------------------------------------------- 5) PLATFORM: stern close-up of the cruiser, clean swim platform + ladder, calm water
WL = 1120
im = scene_bg(WL, sun=(200, 360)); sea_layers(im, WL, n=5, step=170)
o = (850, WL - 120 * 1.9); s = 1.9
cp = {}
paper(im, lambda g: cp.update(cruiser(g, o, s)))
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
lx = T([(20, 86)], o, s)[0]
for k in range(4): g.line([(lx[0] + 0, lx[1] + k * 34), (lx[0] + 46, lx[1] + k * 34)], fill=(200, 205, 212, 255), width=7)  # ladder rungs
g.line([lx, (lx[0], lx[1] + 110)], fill=(200, 205, 212, 255), width=7); g.line([(lx[0] + 46, lx[1]), (lx[0] + 46, lx[1] + 110)], fill=(200, 205, 212, 255), width=7)
im.alpha_composite(lay); front_waves(im, WL, 110); im = grain(im)
pf = T([(35, 70)], o, s)[0]
pts["ep009-platform"] = {"platform": [int(pf[0]), int(pf[1])], "ladder": [int(lx[0] + 23), int(lx[1] + 60)]}
save(im, "ep009-platform")

# ---------------------------------------------------------------- 6) ENGINE ROOM squeeze: paper-cut cross-section (looking forward), engine filling the bilge
im = Image.fromarray(vgrad([(0, (252, 236, 214)), (1, (244, 214, 180))]).astype(np.uint8)).convert("RGBA")
hullpts = [(150, 640), (930, 640), (930, 900), (760, 1260), (540, 1340), (320, 1260), (150, 900)]
paper(im, lambda g: g.polygon(hullpts, fill=HULL + (255,), outline=NAVY + (255,)), alpha=110)
paper(im, lambda g: g.polygon([(190, 700), (890, 700), (890, 900), (740, 1220), (540, 1290), (340, 1220), (190, 900)], fill=(40, 52, 72, 255)), alpha=80)  # bilge space (dark)
paper(im, lambda g: g.rectangle([170, 690, 910, 714], fill=(214, 186, 140, 255)), alpha=80)  # deck hatch line
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
x, y, s_ = 540, 1010, 2.0   # engine end-on (big)
g.rounded_rectangle([x - 150, y - 150, x + 150, y + 170], radius=30, fill=ENG + (255,), outline=ENG_D + (255,), width=8)
g.polygon([(x - 150, y - 150), (x - 60, y - 250), (x + 60, y - 250), (x + 150, y - 150)], fill=ENG_D + (255,))
g.ellipse([x - 60, y - 40, x + 60, y + 80], fill=(150, 76, 36, 255)); g.ellipse([x - 28, y - 8, x + 28, y + 48], fill=(250, 210, 160, 255))
for (bx, by) in ((x - 230, y + 40), (x + 230, y + 40)): g.rounded_rectangle([bx - 46, by - 60, bx + 46, by + 60], radius=10, fill=(90, 100, 116, 255))  # filters / pumps
g.line([(x - 150, y - 180), (x - 260, y - 120), (x - 260, y - 20)], fill=TURQ + (255,), width=12)
g.line([(x + 150, y - 180), (x + 260, y - 120), (x + 260, y - 20)], fill=CORAL + (255,), width=12)
im.alpha_composite(lay)
# little service figure reaching in (paper silhouette)
paper(im, lambda g: (g.ellipse([760, 560, 830, 630], fill=NAVY + (255,)), g.polygon([(770, 620), (830, 620), (850, 700), (750, 700)], fill=NAVY + (255,)),
                     g.line([(780, 690), (700, 800)], fill=NAVY + (255,), width=22)), alpha=90)
im = grain(im)
pts["ep009-engineroom"] = {"engine": [540, 1000], "tight_gap": [750, 960], "hatch": [540, 702], "filters": [310, 1050]}
save(im, "ep009-engineroom")

# ---------------------------------------------------------------- 7) CTA bg: blurred hook
im = Image.open("assets/photos/ep009-hook.jpg").convert("RGBA").filter(ImageFilter.GaussianBlur(14))
im.alpha_composite(Image.new("RGBA", (W, H), (6, 16, 40, 80))); save(im, "ep009-cta")
pts.pop("_ob", None)
import json; print(json.dumps(pts))
