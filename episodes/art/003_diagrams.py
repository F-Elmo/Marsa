"""Illustrations for episode 003 (gyro vs fin stabilizers). Run from repo root: python3 episodes/art/003_diagrams.py
New look for this episode: bow-on (front view) hull cross-sections showing the ROLL, instead of side profiles."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

def rot(pts, c, deg):
    a = math.radians(deg); ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]

HULL = [(-300, -200), (300, -200), (318, 20), (0, 175), (-318, 20)]
BOTTOM = [(-316, 0), (316, 0), (318, 20), (0, 175), (-318, 20)]
CABIN = [(-215, -200), (-175, -365), (175, -365), (215, -200)]
ROOF = [(-195, -365), (-150, -420), (150, -420), (195, -365)]

def hull_front(im, c, deg, scale=1.0, alpha=255, clean=True):
    S = lambda P: rot([(x * scale, y * scale) for x, y in P], c, deg)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon(S(CABIN), fill=(250, 251, 252, alpha))
    d.polygon(S(ROOF), fill=(236, 240, 246, alpha))
    d.polygon(S([(-190, -225), (-160, -340), (160, -340), (190, -225)]), fill=(28, 44, 66, alpha))
    d.polygon(S(HULL), fill=(245, 247, 250, alpha))
    d.polygon(S(BOTTOM), fill=(24, 36, 58, alpha))
    d.line(S([(-305, -150), (305, -150)]), fill=GOLD + (alpha,), width=max(2, int(6 * scale)))
    d.line(S([(-300, -200), (300, -200)]), fill=(200, 206, 216, alpha), width=max(2, int(5 * scale)))
    im.alpha_composite(lay)
    return S

def arc_arrow(d, c, r, a0, a1, col, w=12, both=False):
    pts = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 40)]
    d.line(pts, fill=col + (255,), width=w, joint="curve")
    def head(p, q):
        ang = math.atan2(q[1] - p[1], q[0] - p[0]); s = w * 2.6
        d.polygon([(q[0] + s * math.cos(ang), q[1] + s * math.sin(ang)),
                   (q[0] + s * math.cos(ang + 2.4), q[1] + s * math.sin(ang + 2.4)),
                   (q[0] + s * math.cos(ang - 2.4), q[1] + s * math.sin(ang - 2.4))], fill=col + (255,))
    head(pts[-2], pts[-1])
    if both: head(pts[1], pts[0])

def waves(d, y, col=(235, 250, 255), n=3, amp=16, seed=1):
    for j in range(n):
        yy = y + j * 26
        d.line([(x, yy + amp * math.sin(x / 70 + j * 1.3 + seed)) for x in range(-10, W + 20, 10)], fill=col + (200 - j * 60,), width=6 - j * 2)

# ---------------- 1. hook: bow-on yacht rolling on a swell
WL = 1270
im, d = canvas("sea", waterline=WL)
C = (540, 1220)
hull_front(im, C, -13, 1.0, alpha=70)   # ghost of the roll the other way
hull_front(im, C, 13, 1.0)
d = ImageDraw.Draw(im, "RGBA")
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
g.polygon([(0, WL)] + [(x, WL + 22 * math.sin(x / 110)) for x in range(0, W + 10, 10)] + [(W, H), (0, H)], fill=(20, 170, 190, 150))
im.alpha_composite(lay); d = ImageDraw.Draw(im, "RGBA")
waves(d, WL - 4)
arc_arrow(d, C, 460, 240, 300, GOLD_L, w=14, both=True)
save(im, "ep003-roll")

# ---------------- 2. gyro: blueprint cut-away, flywheel in a sealed sphere
im, d = canvas("blueprint")
C = (540, 1060)
S = lambda P: rot([(x * 1.3, y * 1.3) for x, y in P], C, 7)
d.polygon(S(HULL), outline=STEEL + (255,), fill=(20, 50, 95, 255))
d.line(S(HULL + [HULL[0]]), fill=STEEL + (255,), width=6)
d.line(S([(-305, -150), (305, -150)]), fill=GOLD + (200,), width=4)
d.line(S([(-250, 60), (250, 60)]), fill=(120, 150, 190, 255), width=5)       # engine-room floor
sc = S([(0, -30)])[0]
glow(im, lambda g: g.ellipse([sc[0] - 150, sc[1] - 150, sc[0] + 150, sc[1] + 150], outline=TURQ + (255,), width=10), radius=12)
d = ImageDraw.Draw(im, "RGBA")
d.ellipse([sc[0] - 150, sc[1] - 150, sc[0] + 150, sc[1] + 150], fill=(30, 70, 120, 230), outline=TURQ + (255,), width=6)
d.rounded_rectangle([sc[0] - 190, sc[1] + 120, sc[0] + 190, sc[1] + 160], radius=10, fill=(90, 110, 140, 255), outline=STEEL + (255,), width=3)  # cradle
# flywheel seen at an angle: ellipse + rim
fw = [sc[0] - 120, sc[1] - 38, sc[0] + 120, sc[1] + 38]
d.ellipse([fw[0], fw[1] + 14, fw[2], fw[3] + 14], fill=(120, 94, 44, 255))
d.ellipse(fw, fill=GOLD + (255,), outline=WHITE + (255,), width=4)
d.ellipse([sc[0] - 22, sc[1] - 8, sc[0] + 22, sc[1] + 8], fill=NAVY + (255,))
d.line([(sc[0], sc[1] - 130), (sc[0], sc[1] + 110)], fill=WHITE + (200,), width=4)      # spin axis
# spin arrow around the disc (flattened arc)
pts = [(sc[0] + 150 * math.cos(math.radians(a)), sc[1] + 50 * math.sin(math.radians(a)) - 2) for a in np.linspace(20, 160, 30)]
d.line(pts, fill=WHITE + (255,), width=7, joint="curve")
q, p = pts[-1], pts[-2]; ang = math.atan2(q[1] - p[1], q[0] - p[0])
d.polygon([(q[0] + 20 * math.cos(ang), q[1] + 20 * math.sin(ang)), (q[0] + 20 * math.cos(ang + 2.4), q[1] + 20 * math.sin(ang + 2.4)), (q[0] + 20 * math.cos(ang - 2.4), q[1] + 20 * math.sin(ang - 2.4))], fill=WHITE + (255,))
save(im, "ep003-gyro-close")
# roll (coral) vs gyro push-back (turq)
arc_arrow(d, C, 400, 250, 300, CORAL, w=14)
arc_arrow(d, C, 340, 292, 245, TURQ, w=14)
save(im, "ep003-gyro")

# ---------------- 3. at anchor: calm, clean hull, gyro glowing inside
WL = 900
im, d = canvas("sea", waterline=WL)
pts = yacht_profile(im, waterline=WL)
d = ImageDraw.Draw(im, "RGBA")
waves(d, WL - 2, amp=4)
g0 = (pts["engine_room"][0] - 40, WL - 30)
glow(im, lambda g: g.ellipse([g0[0] - 34, g0[1] - 34, g0[0] + 34, g0[1] + 34], fill=TURQ + (255,)), radius=14)
d = ImageDraw.Draw(im, "RGBA")
d.ellipse([g0[0] - 20, g0[1] - 7, g0[0] + 20, g0[1] + 7], fill=GOLD + (255,))
bow = pts["bow"]; seabed = 1560
chain = [(bow[0] + 40, bow[1] + 40)]
for i in range(1, 30):
    t = i / 29; chain.append((bow[0] + 40 - 30 * t + 10 * math.sin(t * 3), bow[1] + 40 + (seabed - 40 - bow[1] - 40) * t))
d.line(chain, fill=(210, 215, 225, 230), width=5)
ax, ay = chain[-1]
d.line([(ax, ay - 60), (ax, ay + 20)], fill=(210, 215, 225, 255), width=9)
d.arc([ax - 45, ay - 40, ax + 45, ay + 40], 20, 160, fill=(210, 215, 225, 255), width=9)
d.polygon([(0, seabed + 30)] + [(x, seabed + 18 * math.sin(x / 150)) for x in range(0, W + 10, 10)] + [(W, H), (0, H)], fill=(222, 204, 160, 255))
save(im, "ep003-anchor")

# ---------------- 4. fins: underwater bow-on view, two fins + lift arrows
WL = 800
im, d = canvas("sea", waterline=WL)
C = (540, 920)
S = hull_front(im, C, 0, 1.1)
d = ImageDraw.Draw(im, "RGBA")
waves(d, WL - 4, amp=8)
def fin(root, sgn, tilt):
    base = [(0, -24), (0, 24), (150, 16), (160, -12)]
    P = [(root[0] + sgn * x * math.cos(math.radians(tilt)) - 0, root[1] + y + sgn * x * math.sin(math.radians(tilt * sgn))) for x, y in base]
    d.polygon(P, fill=(200, 208, 220, 255), outline=WHITE + (255,))
    d.line([P[0], P[3]], fill=(150, 160, 175, 255), width=4)
    return ((P[2][0] + P[3][0]) / 2, (P[2][1] + P[3][1]) / 2)
lroot = S([(-270, 70)])[0]; rroot = S([(270, 70)])[0]
lt = fin(lroot, -1, -18); rt = fin(rroot, 1, 18)
d = ImageDraw.Draw(im, "RGBA")
mids = [(((lroot[0] + lt[0]) / 2, (lroot[1] + lt[1]) / 2), True), (((rroot[0] + rt[0]) / 2, (rroot[1] + rt[1]) / 2), False)]
for (x, y), up in mids:
    y2 = y - 170 if up else y + 170
    d.line([(x, y), (x, y2)], fill=(TURQ if up else CORAL) + (255,), width=14)
    d.polygon([(x, y2 + (-30 if up else 30)), (x - 26, y2), (x + 26, y2)], fill=(TURQ if up else CORAL) + (255,))
rnd = random.Random(4)
for i in range(16):   # water flowing past (toward the viewer)
    x = rnd.uniform(60, 1020); y = rnd.uniform(1200, 1320); r = rnd.uniform(4, 10)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 250, 255, 120))
save(im, "ep003-fins")

# ---------------- 5. at speed: side profile, fin under the hull, wake + speed lines
WL = 860
im, d = canvas("sea", waterline=WL)
pts = yacht_profile(im, waterline=WL)
d = ImageDraw.Draw(im, "RGBA")
fx = pts["keel"][0]; fy = WL + 60
d.polygon([(fx - 70, fy), (fx + 60, fy), (fx + 40, fy + 90), (fx - 40, fy + 90)], fill=(200, 208, 220, 255), outline=WHITE + (255,))
rnd = random.Random(9)
for i in range(22):
    y = rnd.uniform(620, 1300); x0 = rnd.uniform(700, 1000); L = rnd.uniform(80, 220)
    d.line([(x0, y), (x0 + L, y)], fill=(255, 255, 255, 110), width=4)
for k in range(5):
    y = WL - 6 + k * 10; d.line([(pts["stern"][0] - 40 * k, y), (W, y + 30 + k * 12)], fill=(240, 252, 255, 220 - k * 35), width=10 - k)
d.polygon([(pts["bow"][0] - 10, WL - 10), (pts["bow"][0] + 90, WL - 6), (pts["bow"][0] + 60, WL + 18)], fill=(240, 252, 255, 220))
save(im, "ep003-speed")

# ---------------- 6. calm CTA background: faint roll picture on blueprint
bg, _ = canvas("blueprint")
save(Image.blend(bg, Image.open("assets/photos/ep003-roll.jpg").convert("RGBA"), 0.3), "ep003-cta")
print("gyro sphere", sc, "fins", mids, "speed", pts)
