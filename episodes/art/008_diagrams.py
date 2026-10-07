"""Illustrations for episode 008 (marine air-conditioning in Saudi summer). Run from repo root:
    python3 episodes/art/008_diagrams.py
New look for this episode: THERMAL-CAMERA false colour (iron palette) for the 'heat' shots, plus bright
white-noon daylight cut-aways (previous: blueprint, amber heat, dusk, deep teal underwater, night indigo)."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

SUN = (255, 236, 170); COPPER = (214, 120, 60); COPPER_D = (150, 76, 36); ICE = (150, 225, 255)

# ---------------------------------------------------------------- thermal helpers
IRON = [(0.00, (6, 4, 26)), (0.18, (52, 10, 110)), (0.36, (150, 20, 140)), (0.52, (220, 50, 70)),
        (0.68, (250, 120, 20)), (0.84, (255, 205, 40)), (1.00, (255, 252, 220))]
def iron(v):
    v = np.clip(v, 0, 1); out = np.zeros(v.shape + (3,))
    for c in range(3): out[..., c] = np.interp(v, [s[0] for s in IRON], [s[1][c] for s in IRON])
    return out
def blur_field(f, r):
    im = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im).astype(float) / 255
def mask_of(draw_fn, r=0):
    m = Image.new("L", (W, H), 0); draw_fn(ImageDraw.Draw(m))
    if r: m = m.filter(ImageFilter.GaussianBlur(r))
    return np.asarray(m).astype(float) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(float)
def ripples(seed, top, amp=0.06):
    rnd = random.Random(seed); f = np.zeros((H, W))
    for k in range(6):
        a = rnd.uniform(0.004, 0.012); b = rnd.uniform(0.02, 0.05); ph = rnd.uniform(0, 6)
        f += np.sin(xx * a + yy * b + ph) * amp / 3
    f[yy < top] = 0; return f
def hud(d, cx, cy, txt, col=WHITE):
    for s in (-1, 1):
        d.line([(cx + s * 30, cy), (cx + s * 80, cy)], fill=col + (255,), width=5)
        d.line([(cx, cy + s * 30), (cx, cy + s * 80)], fill=col + (255,), width=5)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=col + (255,), width=4)
    d.rounded_rectangle([cx + 40, cy - 110, cx + 40 + F(800, 40).getlength(txt) + 36, cy - 50], radius=12, fill=(0, 0, 0, 150))
    d.text((cx + 58, cy - 80), txt, font=F(800, 40), fill=col + (255,), anchor="lm")
def scale_bar(d, x=990, y0=640, y1=1240):
    for i in range(int(y1 - y0)):
        v = 1 - i / (y1 - y0); c = tuple(int(q) for q in iron(np.array(v)))
        d.line([(x, y0 + i), (x + 26, y0 + i)], fill=c + (255,))
    d.rectangle([x, y0, x + 26, y1], outline=WHITE + (200,), width=2)

pts = {}
# 1) HOOK: thermal-camera view of a yacht at anchor in a hot sea; cabin glows cool, sun + sea glow hot
WL = 1020
f = 0.30 + 0.10 * (yy / H)                                    # air
sun = np.exp(-(((xx - 820) / 210) ** 2 + ((yy - 300) / 210) ** 2)); f += 0.75 * sun
sea = yy >= WL; f[sea] = 0.62 + 0.10 * np.exp(-(yy[sea] - WL) / 260)  # hot sea surface
f += ripples(3, WL)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); info = yacht_profile(lay, waterline=WL, x0=60, x1=1020, tint_under=False)
hull = np.asarray(lay.getchannel("A")).astype(float) / 255
f = f * (1 - hull) + 0.80 * hull                               # sun-baked hull
cool = mask_of(lambda g: [g.rounded_rectangle(b, radius=10, fill=255) for b in ((330, 900, 600, 962), (640, 898, 860, 960))], r=18)
f = f * (1 - cool) + 0.14 * cool                               # air-conditioned cabin = cool
f = blur_field(f, 3)
im = Image.fromarray(iron(f).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
hud(d, 470, 1200, "SEA 31°C"); hud(d, 470, 930, "CABIN 22°C", col=ICE); scale_bar(d)
pts["ep008-hook"] = {"sea": [470, 1200], "cabin": [470, 930], "hull": [760, 990]}
save(im, "ep008-hook")

# 2) HOW IT WORKS: bright noon daylight cut-away with the seawater loop
def shift_left(im, wl, dx=100):
    """Move the drawing left so the stern / discharge stays clear of the TikTok button column."""
    bg = noon(wl, sun=False); bg.paste(im.crop((dx, 0, W, H)), (0, 0)); return bg
def noon(wl, sun=True):
    arr = vgrad([(0, (120, 190, 240)), (wl / H * 0.999, (235, 246, 252)), (wl / H, (30, 190, 205)), (0.75, (10, 120, 160)), (1, (4, 50, 90))])
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    def s(g): g.ellipse([820, 120, 980, 280], fill=SUN + (255,))
    if sun: glow(im, s, radius=40)
    return im
WL2 = 1000
im = noon(WL2); info = yacht_profile(im, waterline=WL2, x0=40, x1=1040)
d = ImageDraw.Draw(im, "RGBA")
d.rounded_rectangle([250, 870, 930, 1110], radius=26, fill=(250, 250, 246, 240), outline=NAVY + (255,), width=5)  # cut-away
# components
intake = (330, 1120); strainer = (330, 1010); pumpc = (480, 1050); unit = (700, 980, 880, 1080); disch = (1000, 950)
def loop(g):
    g.line([intake, (330, 1060)], fill=TURQ + (255,), width=16)
    g.line([(330, 960), (330, 930), (420, 930), (420, 1050), (450, 1050)], fill=TURQ + (255,), width=16, joint="curve")
    g.line([(510, 1050), (640, 1050), (640, 1030), (700, 1030)], fill=TURQ + (255,), width=16, joint="curve")
    g.line([(880, 1030), (950, 1030), (950, 950), (1000, 950)], fill=CORAL + (255,), width=16, joint="curve")
glow(im, loop, radius=8); d = ImageDraw.Draw(im, "RGBA")
for (x, y, ang, c) in ((330, 1095, -90, WHITE), (580, 1050, 0, WHITE), (920, 1030, 0, WHITE), (950, 990, -90, WHITE)):
    a = math.radians(ang); s = 22
    d.polygon([(x + s * math.cos(a), y + s * math.sin(a)), (x + s * math.cos(a + 2.5), y + s * math.sin(a + 2.5)), (x + s * math.cos(a - 2.5), y + s * math.sin(a - 2.5))], fill=c + (255,))
d.rounded_rectangle([295, 960, 365, 1060], radius=14, fill=(200, 210, 220, 255), outline=NAVY + (255,), width=4)   # strainer
for yb in range(975, 1050, 14): d.line([(305, yb), (355, yb)], fill=(120, 130, 150, 255), width=3)
d.ellipse([450, 1020, 510, 1080], fill=GOLD + (255,), outline=NAVY + (255,), width=4)                               # pump
d.ellipse([468, 1038, 492, 1062], fill=NAVY + (255,))
box(d, unit, "AC UNIT", color=NAVY, fill=(18, 196, 204, 235), fs=28)
# cold air into cabin: blue wavy lines rising from the unit
def cold(g):
    for k in range(3):
        x0 = 740 + k * 50
        g.line([(x0 + 10 * math.sin(t / 9), 970 - t) for t in range(0, 70, 4)], fill=(40, 130, 230, 255), width=7)
glow(im, cold, radius=6); d = ImageDraw.Draw(im, "RGBA")
# discharge stream from topsides
strm = [(1000, 950)] + [(1000 + t * 1.0, 950 + (t / 6.5) ** 2) for t in range(0, 64, 4)]
d.line(strm, fill=NAVY + (255,), width=16); d.line(strm, fill=(200, 240, 255, 255), width=10)
d.ellipse([310, 1112, 350, 1132], fill=NAVY + (255,))  # thru-hull
im = shift_left(im, WL2)
pts["ep008-loop"] = {"intake": [230, 1122], "strainer": [230, 1010], "pump": [380, 1050], "ac_unit": [690, 1030], "discharge": [940, 990], "cold_air": [690, 935]}
save(im, "ep008-loop")

# 3) CONDENSER close-up: copper refrigerant coil inside a seawater jacket, heat flowing into the water
im = noon(1920); d = ImageDraw.Draw(im, "RGBA")
d.rectangle([0, 0, W, H], fill=(240, 244, 248, 160))
jx0, jy0, jx1, jy1 = 120, 760, 960, 1180
d.rounded_rectangle([jx0, jy0, jx1, jy1], radius=110, fill=(30, 180, 200, 255), outline=NAVY + (255,), width=8)
for k in range(9):  # coil turns (front)
    x = 210 + k * 85
    d.ellipse([x, jy0 + 50, x + 110, jy1 - 50], outline=COPPER_D + (255,), width=20)
    d.arc([x, jy0 + 50, x + 110, jy1 - 50], 90, 270, fill=COPPER + (255,), width=20)
def heat(g):
    for k in range(8):
        x = 225 + k * 90
        for (y0, sg) in ((jy0 + 46, -1), (jy1 - 46, 1)):
            g.line([(x + 14 * math.sin(t / 8 + k), y0 + sg * t) for t in range(0, 40, 4)], fill=(255, 110, 50, 255), width=9)
glow(im, heat, radius=6); d = ImageDraw.Draw(im, "RGBA")
d.polygon([(60, 970), (120, 930), (120, 1010)], fill=TURQ + (255,)); d.polygon([(1020, 970), (960, 930), (960, 1010)], fill=CORAL + (255,))
pts["ep008-coil"] = {"coil": [470, 970], "water_in": [120, 970], "water_out": [960, 970], "jacket": [540, 1160]}
save(im, "ep008-coil")

# 4) COOL SEA vs HOT SEA (thermal split): big heat escape on the left, small on the right
f = np.zeros((H, W))
left = xx < W / 2
f[left] = 0.20 + 0.06 * (yy[left] / H); f[~left] = 0.66 + 0.05 * (yy[~left] / H)
f += ripples(8, 0, amp=0.04)
for (cx, hot) in ((270, True), (810, True)):
    blob = np.exp(-(((xx - cx) / 120) ** 2 + ((yy - 960) / 120) ** 2)); f = np.maximum(f, 0.9 * blob)
plume_l = np.exp(-(((xx - 270) / 170) ** 2)) * np.clip((960 - yy) / 380, 0, 1) * (yy > 620) * 0.0
f = blur_field(f, 6)
im = Image.fromarray(iron(f).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
d.line([(W / 2, 600), (W / 2, 1320)], fill=WHITE + (230,), width=6)
def arr_(g, cx, n, ln):
    for k in range(n):
        a = math.radians(k * 360 / n + 10); r0 = 150
        p0 = (cx + r0 * math.cos(a), 960 + r0 * math.sin(a)); p1 = (cx + (r0 + ln) * math.cos(a), 960 + (r0 + ln) * math.sin(a))
        g.line([p0, p1], fill=WHITE + (255,), width=12)
        g.polygon([(p1[0] + 24 * math.cos(a), p1[1] + 24 * math.sin(a)), (p1[0] + 18 * math.cos(a + 1.8), p1[1] + 18 * math.sin(a + 1.8)), (p1[0] + 18 * math.cos(a - 1.8), p1[1] + 18 * math.sin(a - 1.8))], fill=WHITE + (255,))
arr_(d, 270, 8, 90); arr_(d, 810, 8, 22)
d.text((270, 960), "COIL", font=F(800, 34), fill=NAVY + (255,), anchor="mm"); d.text((810, 960), "COIL", font=F(800, 34), fill=NAVY + (255,), anchor="mm")
for (cx, t, c) in ((270, "SEA 22°C", ICE), (810, "SEA 31°C", (255, 230, 150))):
    d.rounded_rectangle([cx - 150, 1200, cx + 150, 1270], radius=14, fill=(0, 0, 0, 150)); d.text((cx, 1235), t, font=F(800, 40), fill=c + (255,), anchor="mm")
pts["ep008-seas"] = {"cool_coil": [270, 960], "hot_coil": [810, 960], "cool_sea": [270, 1235], "hot_sea": [810, 1235]}
save(im, "ep008-seas")

# 5) CLOGGED sea strainer basket (top view of strainer, lid off, weed + shells)
im = noon(1920); d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(236, 240, 244, 200))
d.ellipse([200, 660, 880, 1300], fill=(170, 180, 192, 255), outline=NAVY + (255,), width=10)
d.ellipse([250, 710, 830, 1250], fill=(60, 66, 80, 255))
rnd = random.Random(11)
for i in range(-260, 270, 26):  # mesh
    d.line([(540 + i, 720), (540 + i, 1240)], fill=(120, 128, 140, 120), width=3); d.line([(260, 980 + i), (820, 980 + i)], fill=(120, 128, 140, 120), width=3)
for k in range(40):  # weed strands
    x = rnd.uniform(300, 780); y = rnd.uniform(760, 1200)
    d.line([(x + 30 * math.sin(t / 12 + k), y + t) for t in range(0, 90, 6)], fill=(rnd.randint(60, 110), rnd.randint(120, 170), 50, 255), width=8)
for k in range(14):  # shells
    x = rnd.uniform(320, 760); y = rnd.uniform(780, 1180); r = rnd.uniform(18, 30)
    d.pieslice([x - r, y - r, x + r, y + r], 200, 340, fill=(240, 228, 205, 255), outline=(170, 150, 120, 255), width=3)
pts["ep008-strainer"] = {"weed": [470, 930], "shells": [640, 1060], "basket": [860, 1100]}
save(im, "ep008-strainer")

# 6) HELP IT: yacht in noon sun with blinds drawn, filters, strong discharge stream
WL3 = 1080
im = noon(WL3); info = yacht_profile(im, waterline=WL3, x0=40, x1=1040); d = ImageDraw.Draw(im, "RGBA")
for b in ((260, 945, 560, 1015), (580, 945, 840, 1015)):  # blinds over windows
    d.rounded_rectangle(b, radius=8, fill=(236, 230, 214, 255))
    for yb in range(b[1] + 10, b[3], 12): d.line([(b[0] + 6, yb), (b[2] - 6, yb)], fill=(190, 180, 160, 255), width=3)
strm = [(1000, 1030)] + [(1000 + t * 1.0, 1030 + (t / 6.5) ** 2) for t in range(0, 64, 4)]
d.line(strm, fill=NAVY + (255,), width=18); d.line(strm, fill=(200, 240, 255, 255), width=12)  # strong stream
d.ellipse([990, 1022, 1010, 1040], fill=NAVY + (255,))
im = shift_left(im, WL3)
pts["ep008-help"] = {"blinds": [310, 980], "stream": [945, 1075], "saloon": [600, 980]}
save(im, "ep008-help")

# 7) CTA bg: blurred hook
im = Image.open("assets/photos/ep008-hook.jpg").convert("RGBA").filter(ImageFilter.GaussianBlur(14))
im.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 30, 90))); save(im, "ep008-cta")
import json; print(json.dumps(pts))
