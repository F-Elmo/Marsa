"""Animated diagrams for episode 014 (hard vs ablative antifouling). Renders 4 MP4 clips 1080x1920@30.
New look (not used before): "magnified paint cross-section" - a microscope-style lens panel showing hull laminate,
primer and antifouling layers, sea water flowing underneath, copper biocide particles and barnacle larvae.
Run from repo root:  python3 episodes/art/014_antifouling_anim.py [stills|video]"""
import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = "/home/claude/ctm-reels/assets/fonts/"
def F(wt, sz): return ImageFont.truetype(ROOT + "montserrat-latin-%d-normal.woff" % wt, sz)
def O(sz): return ImageFont.truetype(ROOT + "oswald-latin-700-normal.woff", sz)
NAVY = (9, 24, 54); GOLD = (214, 172, 86); TURQ = (18, 196, 204); WHITE = (255, 255, 255)
CORAL = (240, 90, 80); GREEN = (60, 210, 120); COPPER = (236, 140, 60)
PAINT_A = (176, 44, 52)    # ablative red
PAINT_H = (40, 66, 130)    # hard paint blue
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t
def fade(t, st, d=0.35): return clamp((t - st) / d)

# ---- lens panel geometry: everything important lives between y 300 and 1380 (captions at ~1450, TikTok UI below)
LX0, LX1, LY0, LY1 = 70, 1010, 430, 1370
HULL_Y0, HULL_Y1 = LY0, 600            # fibreglass laminate
PRIMER_Y1 = 625                        # primer / barrier coat
PAINT0 = 760                           # bottom surface of a fresh antifouling coat

def background():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([4, 30, 44]); bot = np.array([2, 10, 20])
    arr = (top * (1 - y[..., None]) + bot * y[..., None]).repeat(W, 1).astype(np.uint8).reshape(H, W, 3)
    im = Image.fromarray(arr).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(14)
    for _ in range(160):  # faint plankton specks
        x, yy, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 3)
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=(120, 220, 230, rnd.randint(20, 60)))
    return im
BG = background()

def laminate_texture():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([LX0, HULL_Y0, LX1, HULL_Y1], fill=(226, 230, 236, 255))
    rnd = random.Random(3)
    for k in range(70):   # glass fibre strands
        y = rnd.uniform(HULL_Y0 + 8, HULL_Y1 - 8); x = rnd.uniform(LX0, LX1 - 200)
        d.line([(x, y), (x + rnd.uniform(120, 320), y + rnd.uniform(-6, 6))], fill=(190, 198, 210, 255), width=2)
    d.rectangle([LX0, HULL_Y1, LX1, PRIMER_Y1], fill=(150, 156, 166, 255))
    return im
LAM = laminate_texture()

rndp = random.Random(7)
PARTICLES = [(rndp.uniform(LX0 + 20, LX1 - 20), rndp.uniform(PRIMER_Y1 + 10, 1100), rndp.uniform(5, 8)) for _ in range(260)]
LARVAE = [(rndp.uniform(0, 1), rndp.uniform(0, 1), rndp.uniform(0.7, 1.3)) for _ in range(9)]

def lens_mask():
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([LX0, LY0, LX1, LY1], radius=46, fill=255)
    return m
MASK = lens_mask()

def pill(d, cx, cy, txt, bg, fg, a=1.0, size=40, font=None):
    f = font or F(800, size); tw = f.getlength(txt); h = size * 0.85
    d.rounded_rectangle([cx - tw / 2 - 28, cy - h, cx + tw / 2 + 28, cy + h], radius=int(h), fill=bg + (int(245 * a),))
    d.text((cx, cy + 1), txt, font=f, fill=fg + (int(255 * a),), anchor="mm")

def tick(d, x, y, s, col, a):
    d.line([(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)], fill=col + (int(255 * a),), width=10, joint="curve")

def draw_lens(t, surface, paint_col, mode, extra=None):
    """surface: y of the paint's bottom (water-facing) surface. mode drives particle behaviour."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay, "RGBA")
    d.rectangle([LX0, LY0, LX1, LY1], fill=(14, 92, 128, 255))                # sea water
    # flow lines (water moving past the hull, left -> right)
    speed = 420 if mode in ("ablative", "intro") else 300
    for row in range(9):
        yy = surface + 40 + row * 62
        if yy > LY1 - 20: break
        off = (t * speed * (1 - row * 0.05) + row * 97) % 260
        for x in np.arange(LX0 - 260 + off, LX1, 260):
            d.line([(x, yy), (x + 120, yy)], fill=(170, 235, 255, 90), width=4)
    lay.alpha_composite(LAM); d = ImageDraw.Draw(lay, "RGBA")
    # paint layer(s)
    if extra and "layers" in extra:
        y = PRIMER_Y1
        for i, (th, col) in enumerate(extra["layers"]):
            d.rectangle([LX0, y, LX1, y + th], fill=col + (255,)); d.line([(LX0, y), (LX1, y)], fill=(0, 0, 0, 90), width=3)
            y += th
        surface = y
    else:
        d.rectangle([LX0, PRIMER_Y1, LX1, surface], fill=paint_col + (255,))
    # leached (depleted) zone for hard paint: pale band growing inward from the surface
    if extra and extra.get("leach", 0) > 0:
        lz = extra["leach"]
        d.rectangle([LX0, surface - lz, LX1, surface], fill=(150, 170, 205, 200))
    # biocide particles embedded in the paint
    for (x, y, r) in PARTICLES:
        if PRIMER_Y1 + 6 < y < surface - 6:
            if extra and extra.get("leach", 0) > 0 and y > surface - extra["leach"]:
                continue
            d.ellipse([x - r, y - r, x + r, y + r], fill=COPPER + (255,))
    # released copper in the water just below the surface
    rel = []
    for k in range(70):
        ph = (t * 0.55 + k / 70) % 1
        x = LX0 + 20 + ((k * 137) % 900) + ph * 160
        y = surface + 8 + ph * 150 + 10 * math.sin(k + t * 3)
        if x < LX1 - 10: rel.append((x, y, 6 * (1 - ph * 0.6), 1 - ph))
    for x, y, r, a in rel:
        c = tuple(int(lerp(w, cc, a)) for w, cc in zip((14, 92, 128), COPPER))   # blend into the water colour
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (255,))
    # barnacle larvae drifting up toward the hull and getting repelled
    for i, (ox, oy, sp) in enumerate(LARVAE):
        cyc = (t * 0.32 * sp + oy) % 1
        x = LX0 + 80 + ox * 780 + 40 * math.sin(t * 1.4 + i)
        y = LY1 - 40 - cyc * (LY1 - 40 - (surface + 70))
        near = cyc > 0.82
        col = (200, 210, 190) if not near else (150, 150, 140)
        a = 1.0 if not near else max(0, 1 - (cyc - 0.82) / 0.18)
        d.ellipse([x - 14, y - 10, x + 14, y + 10], fill=col + (int(230 * a),), outline=WHITE + (int(200 * a),), width=2)
        for leg in (-1, 1):
            d.line([(x + leg * 10, y + 6), (x + leg * 18, y + 18 + 4 * math.sin(t * 8 + i))], fill=col + (int(200 * a),), width=3)
        if near:
            s = 12; c = CORAL + (int(255 * a),)
            d.line([(x - s, y - s - 26), (x + s, y + s - 26)], fill=c, width=6); d.line([(x - s, y + s - 26), (x + s, y - s - 26)], fill=c, width=6)
    # scrub pad (hard paint): sweeps along the surface, wiping a slime film away
    if extra and "scrub" in extra:
        sx = extra["scrub"]
        sa = extra.get("slime", 1.0)
        if sa > 0:
            for x in np.arange(max(LX0, sx), LX1, 22):
                d.ellipse([x - 12, surface - 4, x + 12, surface + 16], fill=(80, 150, 70, int(220 * sa)))
        if LX0 - 120 < sx < LX1 + 120:
            d.rounded_rectangle([sx - 95, surface + 4, sx + 95, surface + 70], radius=16, fill=(250, 214, 70, 255), outline=WHITE + (255,), width=4)
            d.rounded_rectangle([sx - 30, surface + 70, sx + 30, surface + 150], radius=10, fill=(230, 230, 236, 255))
            for k in range(5):
                gx = sx + 110 + k * 26; d.line([(gx, surface + 20), (gx + 18, surface + 20)], fill=WHITE + (180,), width=5)
    # lens frame
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.split()[3]), np.array(MASK))))
    return lay, surface

def base(t, title, title_col, title_fg, sub):
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    pill(d, 540, 318, title, title_col, title_fg, fade(t, 0.0), size=50, font=O(64))
    if sub: d.text((540, 395), sub, font=F(700, 32), fill=(200, 230, 240, int(255 * fade(t, 0.2))), anchor="mm")
    return im

def frame_lens(im, lay):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([LX0 - 6, LY0 - 6, LX1 + 6, LY1 + 6], radius=52, fill=(0, 0, 0, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); im.alpha_composite(lay)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([LX0, LY0, LX1, LY1], radius=46, outline=(210, 240, 248, 255), width=5)
    d.text((LX1 - 24, LY1 - 30), "MAGNIFIED", font=F(700, 24), fill=(220, 245, 250, 200), anchor="rm")
    d.line([(LX1 - 230, LY1 - 58), (LX1 - 30, LY1 - 58)], fill=(220, 245, 250, 200), width=4)
    return d

def tag(d, txt, y, a, x=LX0 + 26, bg=(255, 255, 255), fg=NAVY, size=30):
    if a <= 0: return
    f = F(800, size); tw = f.getlength(txt)
    d.rounded_rectangle([x, y - 26, x + tw + 36, y + 26], radius=26, fill=bg + (int(235 * a),))
    d.text((x + 18, y + 1), txt, font=f, fill=fg + (int(255 * a),), anchor="lm")

# ---------------- clip 1: what antifouling does (4.4 s)
def intro(t):
    im = base(t, "ANTIFOULING", GOLD, NAVY, "the paint below the waterline")
    lay, s = draw_lens(t, PAINT0, PAINT_A, "intro"); d = frame_lens(im, lay)
    tag(d, "HULL", 515, fade(t, 0.2))
    tag(d, "ANTIFOULING PAINT", 692, fade(t, 0.5), bg=GOLD)
    tag(d, "COPPER BIOCIDE", 930, fade(t, 1.0), bg=COPPER, fg=WHITE)
    tag(d, "BARNACLE LARVAE CAN'T SETTLE", 1290, fade(t, 2.0), bg=CORAL, fg=WHITE)
    return im

# ---------------- clip 2: ablative wears away like soap (9.4 s)
def ablative(t):
    im = base(t, "ABLATIVE", GOLD, NAVY, "wears away slowly, like soap")
    surf = lerp(PAINT0 + 20, 700, ease((t - 0.8) / 7.5))
    lay, s = draw_lens(t, surf, PAINT_A, "ablative"); d = frame_lens(im, lay)
    # soap inset (top-right of lens) shrinking with the paint
    k = 1 - 0.55 * ease((t - 0.8) / 7.5); cx, cy = 880, 520
    if fade(t, 0.3) > 0:
        a = fade(t, 0.3)
        d.rounded_rectangle([cx - 80 * k - 10, cy - 46 * k - 10, cx + 80 * k + 10, cy + 46 * k + 10], radius=20, fill=(255, 255, 255, int(70 * a)))
        d.rounded_rectangle([cx - 80 * k, cy - 46 * k, cx + 80 * k, cy + 46 * k], radius=int(30 * k), fill=(250, 196, 210, int(255 * a)), outline=WHITE + (int(255 * a),), width=4)
        d.text((cx, cy), "SOAP", font=F(800, max(12, int(30 * k))), fill=NAVY + (int(255 * a),), anchor="mm")
    # thickness gauge on the left of the paint
    a = fade(t, 1.2)
    if a > 0:
        gx = LX0 + 40
        d.line([(gx, PRIMER_Y1 + 6), (gx, surf - 6)], fill=WHITE + (int(255 * a),), width=6)
        for yy in (PRIMER_Y1 + 6, surf - 6): d.line([(gx - 14, yy), (gx + 14, yy)], fill=WHITE + (int(255 * a),), width=6)
    tag(d, "WATER FLOW", 1050, fade(t, 0.6), x=LX0 + 26, bg=TURQ, fg=WHITE)
    tag(d, "SURFACE WEARS AWAY", 1130, fade(t, 3.0))
    tag(d, "FRESH BIOCIDE EXPOSED", 1210, fade(t, 5.3), bg=COPPER, fg=WHITE)
    a = fade(t, 7.6)
    if a > 0: pill(d, 540, 1300, "SELF-CLEANING SURFACE", GREEN, NAVY, a, size=36)
    return im

# ---------------- clip 3: hard paint stays put, leaches, can be scrubbed (8.8 s)
def hard(t):
    im = base(t, "HARD", TURQ, WHITE, "a tough film that stays put")
    leach = 48 * ease((t - 1.8) / 3.0)
    sx = lerp(LX0 - 140, LX1 + 140, ease((t - 6.2) / 2.2)) if t > 6.2 else LX0 - 300
    lay, s = draw_lens(t, PAINT0, PAINT_H, "hard", {"leach": leach, "scrub": sx, "slime": fade(t, 4.6, 1.2)}); d = frame_lens(im, lay)
    a = fade(t, 3.0)
    if a > 0: d.text((LX1 - 30, PAINT0 - 24), "BIOCIDE USED UP", font=F(800, 24), fill=NAVY + (int(255 * a),), anchor="rm")
    tag(d, "TOUGH FILM - STAYS PUT", 970, fade(t, 0.5), bg=TURQ, fg=WHITE)
    tag(d, "BIOCIDE LEACHES FROM INSIDE", 1050, fade(t, 2.2), bg=COPPER, fg=WHITE)
    tag(d, "SCRUB & POLISH SMOOTH", 1130, fade(t, 6.4))
    a = fade(t, 7.6)
    if a > 0: pill(d, 540, 1300, "FAST BOATS LOVE IT", GREEN, NAVY, a, size=36)
    return im

# ---------------- clip 4: hard paint builds up, eventually strip (3.9 s)
def buildup(t):
    im = base(t, "HARD", TURQ, WHITE, "every new coat adds a layer")
    cols = [(40, 66, 130), (54, 84, 150), (34, 58, 116), (62, 94, 160), (46, 74, 140)]
    n = 1 + int(clamp(t / 0.55, 0, 4.0)) if t < 2.4 else 5
    grow = clamp((t % 0.55) / 0.3) if t < 2.4 else 1
    layers = [(64 if i < n - 1 else 64 * grow, cols[i]) for i in range(n)]
    lay, s = draw_lens(t, PAINT0, PAINT_H, "hard", {"layers": layers}); d = frame_lens(im, lay)
    y = PRIMER_Y1
    for i, (th, c) in enumerate(layers):
        if th > 30: d.text((LX1 - 30, y + th / 2), "COAT %d" % (i + 1), font=F(800, 26), fill=(230, 238, 255, 230), anchor="rm")
        y += th
    a = fade(t, 2.5)
    if a > 0:
        pill(d, 540, 1210, "TOO THICK: CRACKS & FLAKES", WHITE, CORAL, a, size=34)
        pill(d, 540, 1300, "STRIP BACK & START AGAIN", CORAL, WHITE, fade(t, 2.9), size=36)
    return im

CLIPS = [("af_intro.mp4", 4.4, intro), ("af_ablative.mp4", 9.4, ablative), ("af_hard.mp4", 8.8, hard), ("af_buildup.mp4", 3.9, buildup)]

def render(name, dur, fn):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", name], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    out = "media/014b/"
    if sys.argv[1] == "stills":
        picks = [(intro, 3.5), (ablative, 2.0), (ablative, 8.5), (hard, 4.5), (hard, 7.0), (buildup, 3.5)]
        sh = Image.new("RGB", (330 * len(picks), 586), "white")
        for i, (fn, tt) in enumerate(picks): sh.paste(fn(tt).convert("RGB").resize((320, 569)), (i * 330, 0))
        sh.save(sys.argv[2] if len(sys.argv) > 2 else "stills.png")
    elif sys.argv[1] == "frame":
        dict((f.__name__, f) for _, _, f in CLIPS)[sys.argv[2]](float(sys.argv[3])).convert("RGB").save(sys.argv[4])
    else:
        for name, dur, fn in CLIPS: render(out + name, dur, fn)
        print("ok")
