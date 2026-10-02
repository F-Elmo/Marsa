"""Illustrations for episode 005 (planing hull vs displacement hull). Run from repo root: python3 episodes/art/005_diagrams.py
New look for this episode: golden-hour / dusk side views at the waterline (sunset sky above, cut-away sea below),
a trawler-style displacement hull vs a sport-cruiser planing hull (previous episodes: blue sea, blueprint, amber heat)."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

def dusk_canvas(horizon=980, sun_x=None, sun_r=110):
    arr = vgrad([(0, (40, 30, 80)), (0.28, (150, 70, 110)), (horizon / H * 0.98, (250, 160, 90)), (horizon / H, (255, 200, 130)),
                 (horizon / H + 0.002, (24, 120, 150)), (0.78, (10, 70, 110)), (1, (4, 26, 58))])
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    if sun_x is not None:
        glow(im, lambda g: g.ellipse([sun_x - sun_r, horizon - sun_r * 0.85, sun_x + sun_r, horizon + sun_r * 1.15], fill=(255, 214, 140, 255)), radius=40)
        sea = Image.fromarray(arr[horizon:].astype(np.uint8)).convert("RGBA"); im.alpha_composite(sea, (0, horizon))
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)  # soft sun glitter on the water
        rnd = random.Random(3)
        for k in range(60):
            y = horizon + 6 + rnd.uniform(0, 260); w = rnd.uniform(14, 40) * (1 + (y - horizon) / 120)
            x = sun_x + rnd.gauss(0, 18 + (y - horizon) * 0.25)
            g.line([(x - w / 2, y), (x + w / 2, y)], fill=(255, 215, 150, int(max(30, 160 - (y - horizon) * 0.5))), width=3)
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(1.5)))
    # underwater light rays
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); r = ImageDraw.Draw(rays)
    for x0 in (120, 360, 620, 880):
        r.polygon([(x0 - 30, horizon), (x0 + 30, horizon), (x0 + 170, H), (x0 - 40, H)], fill=(255, 220, 170, 26))
    im.alpha_composite(rays.filter(ImageFilter.GaussianBlur(22)))
    return im

def xf(pts, origin, L, flip=False, ang=0.0, pivot=(0, 0)):
    """normalized hull coords (x 0..1 bow->stern, y in L units, +down, 0 = waterline) -> pixels; flip = bow points right."""
    out = []
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for x, y in pts:
        x -= pivot[0]; y -= pivot[1]
        # positive ang = bow up (bow is at x<pivot, so rotate so that low-x points go up)
        xr, yr = x * ca - y * sa, x * sa + y * ca
        xr += pivot[0]; yr += pivot[1]
        px = origin[0] + (-xr if flip else xr) * L; py = origin[1] + yr * L
        out.append((px, py))
    return out

def draw_trawler(im, origin, L, flip=False, wl=None, ang=0.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    T = lambda p: xf(p, origin, L, flip, ang, (0.5, 0.0))
    hull = [(0.02, -0.17), (0.98, -0.12), (0.985, 0.02), (0.88, 0.07), (0.6, 0.095), (0.3, 0.095), (0.13, 0.075), (0.05, 0.03), (0.0, -0.05)]
    d.polygon(T(hull), fill=(250, 248, 244, 255))
    d.polygon(T([(0.05, 0.0), (0.985, 0.0), (0.985, 0.02), (0.88, 0.07), (0.6, 0.095), (0.3, 0.095), (0.13, 0.075), (0.05, 0.03)]), fill=(150, 40, 40, 255))  # red bottom paint
    d.polygon(T([(0.33, 0.09), (0.74, 0.13), (0.80, 0.13), (0.82, 0.08)]), fill=(120, 34, 34, 255))  # full keel
    d.line(T([(0.015, -0.13), (0.985, -0.085)]), fill=NAVY + (255,), width=max(3, int(L * 0.012)))
    d.line(T([(0.03, -0.035), (0.985, -0.03)]), fill=GOLD + (255,), width=max(2, int(L * 0.007)))
    for x in (0.2, 0.3, 0.8, 0.88): d.ellipse(T([(x - 0.012, -0.075), (x + 0.012, -0.055)]), fill=(26, 38, 56, 255))
    d.polygon(T([(0.24, -0.16), (0.30, -0.28), (0.78, -0.28), (0.80, -0.14)]), fill=(245, 243, 238, 255))
    d.polygon(T([(0.31, -0.18), (0.335, -0.255), (0.76, -0.255), (0.765, -0.18)]), fill=(28, 44, 66, 255))
    d.polygon(T([(0.34, -0.28), (0.38, -0.37), (0.62, -0.37), (0.64, -0.28)]), fill=(250, 248, 244, 255))
    d.polygon(T([(0.39, -0.295), (0.405, -0.35), (0.60, -0.35), (0.61, -0.295)]), fill=(28, 44, 66, 255))
    d.line(T([(0.5, -0.37), (0.5, -0.52)]), fill=(230, 230, 230, 255), width=max(3, int(L * 0.01)))
    d.line(T([(0.44, -0.47), (0.56, -0.47)]), fill=(230, 230, 230, 255), width=max(3, int(L * 0.008)))
    d.line(T([(0.98, -0.12), (0.98, -0.2)]), fill=STEEL + (255,), width=3)
    if wl is not None: lay = tint_below(lay, wl)
    im.alpha_composite(lay)
    return {k: T([v])[0] for k, v in {"bow": (0.0, -0.05), "stern": (0.985, -0.05), "keel": (0.6, 0.11), "bottom": (0.45, 0.095),
                                       "house": (0.5, -0.32), "forefoot": (0.07, 0.05)}.items()}

def draw_planer(im, origin, L, flip=False, wl=None, ang=0.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    T = lambda p: xf(p, origin, L, flip, ang, (1.0, 0.03))
    hull = [(0.0, -0.13), (0.04, -0.14), (1.0, -0.115), (1.0, 0.03), (0.6, 0.035), (0.3, 0.015), (0.1, -0.04)]
    d.polygon(T(hull), fill=(250, 251, 252, 255))
    d.polygon(T([(0.14, -0.03), (1.0, -0.02), (1.0, 0.03), (0.6, 0.035), (0.3, 0.015), (0.1, -0.04)]), fill=(24, 36, 58, 255))
    d.line(T([(0.03, -0.105), (1.0, -0.09)]), fill=NAVY + (255,), width=max(3, int(L * 0.012)))
    d.line(T([(0.08, -0.055), (1.0, -0.045)]), fill=GOLD + (255,), width=max(2, int(L * 0.007)))
    d.polygon(T([(0.34, -0.125), (0.47, -0.215), (0.70, -0.215), (0.72, -0.12)]), fill=(26, 40, 62, 255))
    d.polygon(T([(0.44, -0.215), (0.48, -0.235), (0.80, -0.235), (0.80, -0.215)]), fill=(250, 251, 252, 255))
    d.line(T([(0.78, -0.235), (0.78, -0.12)]), fill=(250, 251, 252, 255), width=max(3, int(L * 0.012)))
    for x in (0.2, 0.27): d.polygon(T([(x, -0.085), (x + 0.05, -0.083), (x + 0.05, -0.072), (x, -0.074)]), fill=(26, 38, 56, 255))
    if wl is not None: lay = tint_below(lay, wl)
    im.alpha_composite(lay)
    return {k: T([v])[0] for k, v in {"bow": (0.02, -0.12), "stern": (1.0, 0.0), "bottom": (0.7, 0.035), "vee": (0.3, 0.015),
                                       "cabin": (0.6, -0.17), "transom_low": (1.0, 0.03)}.items()}

def tint_below(lay, wl):
    a = np.array(lay); below = np.zeros(a.shape[:2], bool)
    if callable(wl):
        for x in range(W): below[int(wl(x)):, x] = True
    else: below[int(wl):] = True
    m = below & (a[..., 3] > 0); a[m, :3] = (a[m, :3] * 0.55 + np.array([10, 90, 120]) * 0.45).astype(np.uint8)
    return Image.fromarray(a)

def surface(im, f, color=(255, 236, 200, 255), width=6):
    d = ImageDraw.Draw(im, "RGBA"); d.line([(x, f(x)) for x in range(0, W + 10, 10)], fill=color, width=width)

def spray(im, c, spread=160, up=120, n=70, seed=1, direction=-1):
    rnd = random.Random(seed); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    for k in range(n):
        t = rnd.random(); x = c[0] + direction * t * spread * rnd.uniform(0.4, 1.0); y = c[1] - up * math.sin(t * math.pi) * rnd.uniform(0.3, 1.0)
        r = rnd.uniform(4, 16); g.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rnd.uniform(120, 230))))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))

def foam(im, x0, x1, y, seed=2, thick=26):
    rnd = random.Random(seed); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    for k in range(int(abs(x1 - x0) / 6)):
        x = rnd.uniform(min(x0, x1), max(x0, x1)); fade = 1 - abs(x - x0) / max(1, abs(x1 - x0))
        r = rnd.uniform(5, 14) * (0.5 + fade); yy = y + rnd.uniform(-thick, thick) * 0.4; g.ellipse([x - r * 2, yy - r, x + r * 2, yy + r], fill=(255, 255, 255, int(200 * fade + 30)))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))

def arrow(d, a, b, col=GOLD_L, w=12):
    d.line([a, b], fill=col + (255,), width=w); ang = math.atan2(b[1] - a[1], b[0] - a[0]); s = w * 2.6
    d.polygon([(b[0] + s * 0.6 * math.cos(ang), b[1] + s * 0.6 * math.sin(ang)),
               (b[0] + s * math.cos(ang + 2.4), b[1] + s * math.sin(ang + 2.4)), (b[0] + s * math.cos(ang - 2.4), b[1] + s * math.sin(ang - 2.4))], fill=col + (255,))

# ---------------- 1. hook: trawler (left, ploughing) vs sport cruiser (right, flying) at sunset
HZ = 1000
im = dusk_canvas(HZ, sun_x=540, sun_r=90)
tp = draw_trawler(im, (60, HZ), 430, wl=HZ)
foam(im, 40, 130, HZ - 4, seed=5, thick=20)
spray(im, (690, HZ - 6), spread=150, up=90, n=80, seed=7, direction=-1)
pp = draw_planer(im, (1030, HZ - 6), 430, flip=True, ang=7, wl=HZ)
foam(im, 680, 560, HZ - 2, seed=6, thick=30)
print("hook", tp, pp)
save(im, "ep005-hook")

# ---------------- 2. displacement hull sitting deep: water pushed aside (arrows), cut-away sea
HZ = 970
im = dusk_canvas(HZ, sun_x=900, sun_r=70)
tp = draw_trawler(im, (120, HZ), 840, wl=HZ)
d = ImageDraw.Draw(im, "RGBA")
for (a, b) in [((320, 1070), (200, 1170)), ((540, 1100), (540, 1230)), ((770, 1095), (890, 1200))]:
    arrow(d, a, b, col=GOLD_L, w=11)
foam(im, 60, 160, HZ - 2, seed=8)
print("disp", tp)
save(im, "ep005-displace")

# ---------------- 3. hull speed: trawler trapped between its own bow wave and stern wave
HZ = 1000; L = 860; x0 = 110; A_ = 46
f = lambda x: HZ - A_ * math.cos(2 * math.pi * (x - x0) / L)
arr = vgrad([(0, (40, 30, 80)), (0.3, (150, 70, 110)), (0.47, (250, 160, 90)), (0.5, (255, 200, 130)), (1, (255, 200, 130))])
im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
sea = vgrad([(0, (24, 120, 150)), (0.45, (10, 70, 110)), (1, (4, 26, 58))])
seaim = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(x, f(x)) for x in range(0, W + 10, 10)] + [(W, H), (0, H)], fill=255)
im.paste(seaim, (0, 0), mask)
tp = draw_trawler(im, (x0, HZ + 18), L, wl=f, ang=1.5)
surface(im, f)
d = ImageDraw.Draw(im, "RGBA")
for xc in (x0, x0 + L):  # crest foam
    foam(im, xc - 70, xc + 70, f(xc) - 4, seed=int(xc), thick=24)
d = ImageDraw.Draw(im, "RGBA")
d.line([(x0, 1262), (x0 + L, 1262)], fill=GOLD_L + (255,), width=6)
for xx in (x0, x0 + L): d.line([(xx, 1240), (xx, 1284)], fill=GOLD_L + (255,), width=6)
d.text((x0 + L / 2, 1306), "WAVE LENGTH  =  BOAT LENGTH", font=F(800, 30), fill=(255, 236, 200, 255), anchor="mm")
print("hullspeed crest pts", (x0, f(x0)), (x0 + L, f(x0 + L)), "trough", (x0 + L / 2, f(x0 + L / 2)))
save(im, "ep005-hullspeed")

# ---------------- 4. planing: sport cruiser skimming, bow up, spray + flat wake (bow right)
HZ = 1000
im = dusk_canvas(HZ, sun_x=200, sun_r=80)
spray(im, (600, HZ - 6), spread=300, up=120, n=170, seed=12, direction=-1)
pp = draw_planer(im, (1010, HZ - 4), 880, flip=True, ang=4, wl=HZ)
d = ImageDraw.Draw(im, "RGBA")
foam(im, 600, 10, HZ - 2, seed=11, thick=36)
arrow(d, (620, 1170), (620, 1060), col=GOLD_L, w=12); arrow(d, (820, 1170), (820, 1060), col=GOLD_L, w=12)
print("plane", pp)
save(im, "ep005-planing")

# ---------------- 5. bow-on cross-sections: round displacement bottom (ghost, left) vs V planing bottom (right)
im, d = canvas("blueprint")
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
g.rectangle([0, 960, W, H], fill=(18, 160, 190, 60)); im.alpha_composite(lay); d = ImageDraw.Draw(im, "RGBA")
d.line([(0, 960), (W, 960)], fill=(140, 230, 240, 255), width=5)
# left: round bilge (displacement), faint
cx = 280
d.polygon([(cx - 200, 760), (cx + 200, 760), (cx + 200, 900)] + [(cx + 200 * math.cos(a), 900 + 230 * math.sin(a)) for a in np.linspace(0, math.pi, 30)] + [(cx - 200, 900)], fill=(255, 255, 255, 50), outline=(220, 235, 255, 140))
d.text((cx, 700), "ROUND", font=F(800, 30), fill=(220, 235, 255, 150), anchor="mm")
# right: deep V with chines + strakes (planing), bright
cx = 760
V = [(cx - 230, 760), (cx + 230, 760), (cx + 235, 935), (cx + 200, 950), (cx, 1080), (cx - 200, 950), (cx - 235, 935)]
d.polygon(V, fill=(245, 247, 250, 255)); d.line(V + [V[0]], fill=GOLD_L + (255,), width=6)
for s in (-1, 1):
    for t in (0.35, 0.68):
        px, py = cx + s * 200 * t, 1080 - 130 * t
        d.polygon([(px, py), (px + s * 22, py - 4), (px + s * 22, py + 8)], fill=GOLD_L + (255,))
d.polygon([(cx - 200, 760), (cx + 200, 760), (cx + 200, 840), (cx - 200, 840)], fill=(28, 44, 66, 255))
d.arc([cx - 90, 990, cx + 90, 1170], 215, 325, fill=TURQ + (255,), width=5)
d.text((cx, 700), "V-SHAPED", font=F(800, 30), fill=WHITE + (255,), anchor="mm")
print("vee keel", (cx, 1080), "chine", (cx + 220, 942), "round", (280, 1130))
save(im, "ep005-vee")

# ---------------- 6. choppy sea: planing boat launching off a wave, spray (cost of speed)
HZ = 1010
f = lambda x: HZ + 38 * math.sin(x / 75.0) + 18 * math.sin(x / 31.0 + 1)
arr = vgrad([(0, (36, 40, 70)), (0.3, (110, 80, 110)), (0.5, (230, 150, 100)), (1, (230, 150, 100))])
im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
sea = vgrad([(0, (20, 100, 130)), (0.4, (10, 60, 95)), (1, (4, 24, 52))]); seaim = Image.fromarray(sea.astype(np.uint8)).convert("RGBA")
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(x, f(x)) for x in range(0, W + 10, 10)] + [(W, H), (0, H)], fill=255)
im.paste(seaim, (0, 0), mask)
spray(im, (520, HZ - 10), spread=260, up=150, n=150, seed=21, direction=-1)
pp = draw_planer(im, (960, HZ - 40), 760, flip=True, ang=9)
surface(im, f, color=(255, 240, 220, 255), width=5)
for xc in (110, 340, 580, 820, 1040):
    foam(im, xc - 50, xc + 50, f(xc) - 6, seed=xc, thick=18)
spray(im, (850, HZ - 10), spread=200, up=110, n=90, seed=22, direction=1)
print("chop", pp)
save(im, "ep005-chop")

# ---------------- 7. CTA background: faint version of the hook
im = Image.open("assets/photos/ep005-hook.jpg").convert("RGBA").filter(ImageFilter.GaussianBlur(6))
im.alpha_composite(Image.new("RGBA", (W, H), (20, 14, 40, 110)))
save(im, "ep005-cta")
