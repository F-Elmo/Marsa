"""Illustrations for episode 006 (sacrificial anodes / zincs). Run from repo root: python3 episodes/art/006_diagrams.py
New look for this episode: deep green-teal underwater with caustic light, metallic silver/bronze parts and glowing
'electric' current lines (previous episodes: blueprint, amber heat, dusk)."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

ZINC = (196, 204, 212); ZINC_D = (120, 130, 142); BRONZE = (205, 140, 70); BRONZE_D = (130, 80, 36)
SPARK = (120, 255, 240); HULL = (236, 240, 244); ANTIFOUL = (40, 52, 84)

def deep_canvas(seed=3, tint=(0, 0, 0)):
    arr = vgrad([(0, (20, 120, 130)), (0.35, (8, 80, 96)), (0.75, (4, 44, 64)), (1, (2, 22, 38))])
    arr = np.clip(arr + np.array(tint), 0, 255)
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay); rnd = random.Random(seed)
    for k in range(40):  # caustic light net
        x = rnd.uniform(0, W); y = rnd.uniform(0, 900); r = rnd.uniform(40, 110)
        g.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], outline=(180, 255, 240, 34), width=5)
    for k in range(70):  # particles
        x = rnd.uniform(0, W); y = rnd.uniform(0, H); r = rnd.uniform(1.5, 4)
        g.ellipse([x - r, y - r, x + r, y + r], fill=(200, 240, 240, 60))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    # sandy seabed far below
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(0, 1700)] + [(x, 1660 + 18 * math.sin(x / 130)) for x in range(0, W + 20, 20)] + [(W, H), (0, H)], fill=(150, 140, 100, 160))
    return im, d

def collar(im, c, ang, L=150, R=44, state="new", seed=5):
    """Shaft anode collar (two bolted half-shells) drawn along angle ang at centre c."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rnd = random.Random(seed)
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v): return (c[0] + u * ca - v * sa, c[1] + u * sa + v * ca)
    if state == "eaten": R = R * 0.62
    base = ANTIFOUL if state == "painted" else ZINC
    # body + rounded ends
    d.polygon([P(-L / 2, -R), P(L / 2, -R), P(L / 2, R), P(-L / 2, R)], fill=base + (255,))
    for u in (-L / 2, L / 2):
        x, y = P(u, 0); d.ellipse([x - R * 0.5, y - R, x + R * 0.5, y + R], fill=base + (255,))
    if state != "painted":
        d.line([P(-L / 2 + 6, -R * 0.55), P(L / 2 - 6, -R * 0.55)], fill=(250, 252, 255, 200), width=7)  # sheen
        d.line([P(-L / 2 + 6, R * 0.7), P(L / 2 - 6, R * 0.7)], fill=ZINC_D + (255,), width=6)
    d.line([P(0, -R), P(0, R)], fill=(60, 70, 84, 255), width=4)  # split line
    for u in (-L / 4, L / 4):  # bolts
        x, y = P(u, -R * 0.1); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 98, 110, 255), outline=(220, 225, 230, 255), width=2)
    if state == "eaten":
        for k in range(26):
            u = rnd.uniform(-L / 2, L / 2); v = rnd.uniform(-R, R); r = rnd.uniform(3, 8)
            x, y = P(u, v); d.ellipse([x - r, y - r, x + r, y + r], fill=(70, 80, 92, 255))
        for k in range(8):
            u = rnd.uniform(-L / 2, L / 2); x, y = P(u, -R); d.ellipse([x - 9, y - 6, x + 9, y + 6], fill=(0, 0, 0, 0))
    if state == "painted":
        d.line([P(-L / 2 + 6, -R * 0.55), P(L / 2 - 6, -R * 0.55)], fill=(90, 104, 140, 220), width=7)
    im.alpha_composite(lay)

def stern(im, anode="new", hull_anode=True, sparks=None, shield=False, seed=7):
    """Underwater side view of a yacht stern (bow left, transom right). Returns label points."""
    d = ImageDraw.Draw(im, "RGBA")
    # hull bottom (antifouled) + white topsides fading up
    # bright surface band seen from below, then white topsides above it
    d.rectangle([0, 0, W, 250], fill=(170, 230, 235, 255))
    for k in range(6):
        y = 238 + k * 9; d.line([(x, y + 5 * math.sin(x / 40 + k)) for x in range(0, W + 10, 10)], fill=(230, 255, 255, 150 - k * 20), width=4)
    d.polygon([(0, 0), (1000, 0), (1000, 300), (0, 330)], fill=HULL + (255,))
    d.polygon([(0, 330), (1000, 300), (1000, 640), (0, 720)], fill=(150, 46, 44, 255))  # red antifouling
    d.polygon([(0, 330), (1000, 300), (1000, 316), (0, 346)], fill=NAVY + (255,))       # boot stripe
    d.line([(0, 720), (1000, 640)], fill=(100, 30, 30, 255), width=6)
    d.polygon([(1000, 0), (1012, 0), (1012, 640), (1000, 640)], fill=(200, 206, 214, 255))
    # trim tab at transom bottom
    d.polygon([(1000, 628), (1070, 640), (1070, 652), (1000, 646)], fill=(150, 160, 172, 255))
    tab_anode = (1036, 660)
    d.rounded_rectangle([1016, 650, 1058, 672], radius=6, fill=ZINC + (255,))
    # shaft
    s0, s1 = (120, 712), (790, 1000); ang = math.atan2(s1[1] - s0[1], s1[0] - s0[0])
    d.line([s0, s1], fill=(150, 160, 172, 255), width=26); d.line([s0, s1], fill=(215, 222, 230, 255), width=8)
    # P-bracket strut
    sx, sy = 640, 936
    d.polygon([(560, 662), (600, 659), (sx + 14, sy), (sx - 18, sy)], fill=(120, 130, 142, 255))
    d.ellipse([sx - 30, sy - 30, sx + 30, sy + 30], fill=(120, 130, 142, 255))
    # rudder
    d.polygon([(890, 605), (930, 602), (975, 640), (978, 1170), (900, 1180), (880, 1120)], fill=(170, 178, 190, 255))
    d.line([(915, 603), (915, 1170)], fill=(120, 130, 142, 255), width=6)
    # propeller (side view, bronze)
    px, py = s1
    for (dy, h) in ((-1, 150), (1, 150)):
        d.ellipse([px - 24, py + (dy * h if dy < 0 else 0) - (0 if dy < 0 else 0), px + 34, py + (0 if dy < 0 else h)], fill=BRONZE + (255,), outline=BRONZE_D + (255,), width=3)
    d.ellipse([px - 6, py - 60, px + 46, py + 60], fill=BRONZE_D + (255,))
    d.ellipse([px - 30, py - 26, px + 30, py + 26], fill=BRONZE + (255,), outline=BRONZE_D + (255,), width=3)
    d.polygon([(px + 26, py - 20), (px + 60, py), (px + 26, py + 20)], fill=BRONZE_D + (255,))
    # hull plate anode
    plate = (330, 698)
    if hull_anode:
        d.polygon([(270, 700), (390, 690), (392, 716), (272, 728)], fill=ZINC + (255,))
        d.line([(276, 708), (386, 697)], fill=(250, 252, 255, 220), width=4)
    # shaft anode collar
    u = 0.5; cpt = (s0[0] + (s1[0] - s0[0]) * u, s0[1] + (s1[1] - s0[1]) * u)
    collar(im, cpt, ang, state=anode, seed=seed)
    if sparks:  # glowing current paths from bronze parts to the anode
        col = sparks
        def zig(g, a, b, n=9, amp=16, rnd=random.Random(seed)):
            pts = [a]
            for k in range(1, n):
                t = k / n; pts.append((a[0] + (b[0] - a[0]) * t + rnd.uniform(-amp, amp), a[1] + (b[1] - a[1]) * t + rnd.uniform(-amp, amp)))
            pts.append(b); g.line(pts, fill=col + (255,), width=6, joint="curve")
        def draw(g):
            zig(g, (px - 10, py - 40), (cpt[0] + 40, cpt[1] + 40))
            zig(g, (920, 900), (cpt[0] + 50, cpt[1] - 10), n=12)
            zig(g, (sx, sy + 20), (cpt[0] + 30, cpt[1] + 50), n=6)
        glow(im, draw, radius=10)
    if shield:
        def sh(g):
            g.ellipse([px - 150, py - 190, px + 230, py + 190], outline=SPARK + (230,), width=8)
        glow(im, sh, radius=14)
    return {"anode": [int(cpt[0]), int(cpt[1])], "propeller": [px, py], "shaft": [int(s0[0] + (s1[0] - s0[0]) * 0.22), int(s0[1] + (s1[1] - s0[1]) * 0.22)],
            "rudder": [935, 1000], "strut": [sx, sy], "hull_anode": list(plate), "tab_anode": list(tab_anode)}

pts = {}
# 1) hook: corroded anode + current sparks
im, d = deep_canvas(); pts["ep006-hook"] = stern(im, anode="eaten", sparks=SPARK); save(im, "ep006-hook")
# 2) bodyguard: brand-new anodes everywhere, shield around the prop
im, d = deep_canvas(seed=9); pts["ep006-guard"] = stern(im, anode="new", sparks=GOLD_L, shield=True, seed=11); save(im, "ep006-guard")
# 3) leak: coral heavy current, anode badly eaten
im, d = deep_canvas(seed=12, tint=(30, -10, -10)); pts["ep006-leak"] = stern(im, anode="eaten", sparks=CORAL, seed=13); save(im, "ep006-leak")

# 4) galvanic 'battery' tank
im, d = canvas("blueprint")
d.rounded_rectangle([110, 700, 970, 1290], radius=40, fill=(20, 110, 150, 220), outline=STEEL + (255,), width=8)
for k in range(5):
    y = 740 + k * 26; d.line([(x, y + 6 * math.sin(x / 50 + k)) for x in range(130, 952, 12)], fill=(160, 230, 255, 40), width=3)
d.rounded_rectangle([250, 610, 350, 1200], radius=14, fill=BRONZE + (255,), outline=BRONZE_D + (255,), width=5)
d.line([(272, 640), (272, 1180)], fill=(245, 200, 140, 200), width=8)
rnd = random.Random(4)
zx0, zx1 = 730, 830
d.rounded_rectangle([zx0, 610, zx1, 1200], radius=14, fill=ZINC + (255,), outline=ZINC_D + (255,), width=5)
for k in range(40):  # pits on the dissolving plate
    x = rnd.uniform(zx0 + 8, zx1 - 8); y = rnd.uniform(720, 1190); r = rnd.uniform(4, 11)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(80, 90, 104, 255))
for k in range(9):  # bites out of the edges
    y = rnd.uniform(720, 1180); r = rnd.uniform(10, 22)
    d.ellipse([zx0 - r, y - r, zx0 + r, y + r], fill=(20, 110, 150, 255))
for k in range(34):  # ions drifting away
    x = rnd.uniform(560, 720); y = rnd.uniform(740, 1260); r = rnd.uniform(5, 10)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 210, 220, 200))
def wire(g):
    g.line([(300, 610), (300, 560), (780, 560), (780, 610)], fill=SPARK + (255,), width=10, joint="curve")
glow(im, wire, radius=10)
d = ImageDraw.Draw(im, "RGBA")
for x in (420, 640):  # electron flow arrows (zinc -> bronze along wire)
    d.polygon([(x, 546), (x, 574), (x - 28, 560)], fill=WHITE + (255,))
# lightning icon on the wire
bx, by = 540, 560
d.ellipse([bx - 40, by - 40, bx + 40, by + 40], fill=NAVY + (255,), outline=SPARK + (255,), width=5)
d.polygon([(bx + 6, by - 28), (bx - 16, by + 4), (bx - 2, by + 4), (bx - 8, by + 28), (bx + 16, by - 6), (bx + 2, by - 6)], fill=GOLD_L + (255,))
bg, _ = canvas("blueprint"); bg.alpha_composite(im.crop((0, 0, W, H - 120)), (0, 120)); im = bg  # shift figure down 120px (grid-aligned)
pts["ep006-battery"] = {"strong": [300, 1020], "weak": [780, 1020], "ions": [640, 1120], "wire": [540, 680], "water": [540, 1370]}
save(im, "ep006-battery")

# 5) wear guide: new / half gone / painted
im, d = deep_canvas(seed=21, tint=(-6, -20, -10))
d.rounded_rectangle([60, 700, 1020, 1250], radius=40, fill=(4, 20, 40, 170), outline=(120, 200, 210, 120), width=3)
for i, (x, st) in enumerate([(220, "new"), (540, "eaten"), (860, "painted")]):
    # stub of shaft
    d = ImageDraw.Draw(im, "RGBA")
    d.line([(x - 130, 960), (x + 130, 960)], fill=(150, 160, 172, 255), width=26); d.line([(x - 130, 960), (x + 130, 960)], fill=(215, 222, 230, 255), width=8)
    collar(im, (x, 960), 0.0, L=150, R=58, state=st, seed=30 + i)
d = ImageDraw.Draw(im, "RGBA")
d.ellipse([540 - 140, 960 - 140, 540 + 140, 960 + 140], outline=GOLD_L + (255,), width=8)
d.line([(800, 900), (920, 1020)], fill=CORAL + (255,), width=14); d.line([(920, 900), (800, 1020)], fill=CORAL + (255,), width=14)
d.ellipse([220 - 34, 1120 - 34, 220 + 34, 1120 + 34], fill=TURQ + (255,))
d.line([(202, 1121), (215, 1135), (240, 1106)], fill=WHITE + (255,), width=8, joint="curve")
pts["ep006-wear"] = {"new": [220, 960], "half": [540, 960], "painted": [860, 960]}
save(im, "ep006-wear")

# 6) CTA background: blurred, darkened hook
im = Image.open("assets/photos/ep006-hook.jpg").convert("RGBA").filter(ImageFilter.GaussianBlur(14))
im.alpha_composite(Image.new("RGBA", (W, H), (4, 16, 40, 110))); save(im, "ep006-cta")
import json; print(json.dumps(pts))
