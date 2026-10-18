"""Animated magnified cut-aways for episode 014 (hard vs ablative antifouling).
Renders 3 MP4 clips 1080x1920@30: af_intro.mp4, af_hard.mp4, af_ablative.mp4.
Look: 'magnifier' panel over a deep-teal background (different from ep 013's navy grid hull section)."""
import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = "/home/claude/ctm-reels/assets/fonts/"
def F(wt, sz): return ImageFont.truetype(ROOT + "montserrat-latin-%d-normal.woff" % wt, sz)
def O(sz): return ImageFont.truetype(ROOT + "oswald-latin-700-normal.woff", sz)
NAVY = (9, 24, 54); GOLD = (214, 172, 86); TURQ = (18, 196, 204); WHITE = (255, 255, 255)
CORAL = (240, 90, 80); GREEN = (70, 215, 125); PAINT = (168, 46, 42); PAINT_D = (120, 30, 30)
BIO = (120, 255, 170)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t

# panel geometry
PX0, PY0, PX1, PY1 = 60, 400, 1020, 1400
HULL_TOP = 1230            # top of fibreglass laminate
PAINT0 = 1060              # nominal paint top (170 px thick)

def make_bg():
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([6, 52, 70]); bot = np.array([3, 16, 30])
    arr = (top * (1 - y) + bot * y).repeat(W, 1).astype(np.uint8)
    im = Image.fromarray(arr).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(4)
    for _ in range(60):
        x, yy, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(3, 12)
        d.ellipse([x - r, yy - r, x + r, yy + r], outline=(160, 230, 240, 40), width=2)
    return im
BG = make_bg()

def water_layer(t, flow):
    """inside-panel water: gradient + moving flow streaks (flow = px/s)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im, "RGBA")
    for yy in range(PY0, HULL_TOP, 6):
        k = (yy - PY0) / (HULL_TOP - PY0)
        d.rectangle([PX0, yy, PX1, yy + 6], fill=(int(lerp(40, 14, k)), int(lerp(150, 90, k)), int(lerp(200, 150, k)), 255))
    rnd = random.Random(7)
    for i in range(26):
        y0 = rnd.randint(PY0 + 30, PAINT0 - 40); L = rnd.randint(60, 160); sp = flow * rnd.uniform(0.7, 1.3)
        x = (rnd.randint(0, 1400) + t * sp) % 1400 - 200
        d.line([(x, y0), (x + L, y0)], fill=(200, 245, 255, 90 if flow > 0 else 0), width=4)
    return im

def hull(d):
    d.rectangle([PX0, HULL_TOP, PX1, PY1], fill=(226, 216, 190, 255))
    rnd = random.Random(2)
    for i in range(40):
        y = rnd.randint(HULL_TOP + 15, PY1 - 10); x = rnd.randint(PX0, PX1 - 120)
        d.line([(x, y), (x + rnd.randint(60, 200), y + rnd.randint(-6, 6))], fill=(190, 176, 140, 255), width=3)

def pill(d, txt, xy, a, bg=WHITE, fg=NAVY, size=36, anchor="mm"):
    if a <= 0: return
    f = F(800, size); tw = f.getlength(txt); x, y = xy
    if anchor == "lm": x = x + tw / 2 + 24
    d.rounded_rectangle([x - tw / 2 - 24, y - size * 0.9, x + tw / 2 + 24, y + size * 0.9], radius=int(size * 0.9), fill=bg + (int(245 * a),))
    d.text((x, y + 1), txt, font=f, fill=fg + (int(255 * a),), anchor="mm")

def leader(d, p0, p1, a):
    if a <= 0: return
    d.line([p0, p1], fill=WHITE + (int(230 * a),), width=4)
    d.ellipse([p0[0] - 9, p0[1] - 9, p0[0] + 9, p0[1] + 9], fill=TURQ + (int(255 * a),), outline=WHITE + (int(255 * a),), width=3)

def header(d, letter, title, col, a):
    if a <= 0: return
    d.ellipse([90, 262, 194, 366], fill=col + (int(255 * a),), outline=WHITE + (int(255 * a),), width=4)
    d.text((142, 316), letter, font=O(70), fill=NAVY + (int(255 * a),), anchor="mm")
    d.text((222, 316), title, font=O(78), fill=WHITE + (int(255 * a),), anchor="lm")

def panel_frame(im):
    """round the panel corners + magnifier frame"""
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle([PX0, PY0, PX1, PY1], radius=48, fill=255)
    out = BG.copy(); out.paste(im, (0, 0), mask)
    d = ImageDraw.Draw(out, "RGBA")
    d.rounded_rectangle([PX0, PY0, PX1, PY1], radius=48, outline=WHITE + (255,), width=6)
    pill(d, "MAGNIFIED", (PX1 - 150, PY0 + 50), 1, bg=NAVY, fg=WHITE, size=26)
    return out

def checkrow(d, txt, y, a, ok=True):
    if a <= 0: return
    col = GREEN if ok else CORAL; dx = (1 - ease(a)) * 60
    d.rounded_rectangle([100 + dx, y - 44, 980 + dx, y + 44], radius=44, fill=(255, 255, 255, int(240 * a)))
    d.ellipse([118 + dx, y - 32, 182 + dx, y + 32], fill=col + (int(255 * a),))
    if ok: d.line([(134 + dx, y), (147 + dx, y + 14), (168 + dx, y - 14)], fill=WHITE + (int(255 * a),), width=8)
    else: d.line([(150 + dx, y - 18), (150 + dx, y + 8)], fill=WHITE + (int(255 * a),), width=8); d.ellipse([145 + dx, y + 14, 155 + dx, y + 24], fill=WHITE + (int(255 * a),))
    d.text((206 + dx, y + 1), txt, font=F(800, 36), fill=NAVY + (int(255 * a),), anchor="lm")

# ---------- barnacle larva sprite
def larva(d, x, y, a, ang=0.0, stuck=False):
    c = (250, 180, 80, int(255 * a))
    if stuck:  # little barnacle cone
        d.polygon([(x - 34, y), (x + 34, y), (x + 14, y - 44), (x - 14, y - 44)], fill=(235, 225, 200, int(255 * a)), outline=(150, 130, 100, int(255 * a)))
        d.line([(x - 8, y - 44), (x + 8, y - 44)], fill=(90, 70, 50, int(255 * a)), width=5); return
    d.ellipse([x - 16, y - 12, x + 16, y + 12], fill=c)
    for k in (-1, 1):
        d.line([(x + 10 * k, y + 8), (x + 22 * k + 6 * math.sin(ang), y + 26)], fill=c, width=4)
    d.ellipse([x + 4, y - 6, x + 10, y], fill=(40, 30, 20, int(255 * a)))

# ---------- biocide particles
RND = random.Random(11)
PORES = [(RND.uniform(PX0 + 20, PX1 - 20), RND.uniform(0, 1)) for _ in range(150)]  # x, depth fraction in paint

def draw_paint_block(d, top, bottom, porous=False, bands=False, depleted_to=0.0, glow=True):
    d.rectangle([PX0, top, PX1, bottom], fill=PAINT + (255,))
    if bands:
        n = 7
        for k in range(1, n):
            yy = lerp(PAINT0, bottom, k / n)
            if yy > top: d.line([(PX0, yy), (PX1, yy)], fill=PAINT_D + (255,), width=3)
    for x, f in PORES:
        y = lerp(PAINT0, bottom, f)
        if y < top + 6: continue
        if porous:
            d.ellipse([x - 11, y - 9, x + 11, y + 9], fill=(90, 22, 22, 255))
            depth = (y - top) / max(1, bottom - top)
            if depth > depleted_to: d.ellipse([x - 7, y - 6, x + 7, y + 6], fill=BIO + (255,))
        else:
            d.ellipse([x - 7, y - 6, x + 7, y + 6], fill=BIO + (255,))
    if glow and top < bottom - 4:
        pass

def bio_cloud(im, t, surface, strength):
    """biocide particles drifting up from the paint surface"""
    if strength <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rnd = random.Random(5)
    for i in range(70):
        x0 = rnd.uniform(PX0 + 10, PX1 - 10); ph = (t * 0.35 + rnd.random()) % 1
        y = surface - ph * 230; x = x0 + 18 * math.sin(t * 2 + i)
        a = int(220 * strength * (1 - ph))
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=BIO + (a,))
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(halo)
    hd.rectangle([PX0, surface - 120, PX1, surface], fill=BIO + (int(60 * strength),))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(30))); im.alpha_composite(lay)

# ================= INTRO: how antifouling works (5.8 s)
def intro(t):
    im = water_layer(t, 0); d = ImageDraw.Draw(im, "RGBA"); hull(d)
    draw_paint_block(d, PAINT0, HULL_TOP)
    s = ease(t / 1.2)
    bio_cloud(im, t, PAINT0, s); d = ImageDraw.Draw(im, "RGBA")
    # larvae: swim down, get repelled when entering the biocide zone
    for i, (x0, st) in enumerate([(230, 0.9), (520, 1.4), (800, 1.9), (380, 2.6), (700, 3.1)]):
        u = t - st
        if u < 0: continue
        turn = 1.6
        if u < turn: y = lerp(PY0 + 80, PAINT0 - 150, ease(u / turn)); x = x0
        else:
            v = u - turn; y = PAINT0 - 150 - 260 * ease(v / 1.6); x = x0 + 90 * ease(v / 1.6) * (1 if i % 2 else -1)
        a = clamp(u / 0.3) * (1 - clamp((u - 3.0) / 0.6))
        larva(d, x, y, a, ang=t * 8)
        if turn < u < turn + 1.2:
            b = 1 - clamp((u - turn - 0.8) / 0.4); cx, cy = x + 38, y - 40
            d.line([(cx - 14, cy - 14), (cx + 14, cy + 14)], fill=CORAL + (int(255 * b),), width=7)
            d.line([(cx - 14, cy + 14), (cx + 14, cy - 14)], fill=CORAL + (int(255 * b),), width=7)
    out = panel_frame(im); d = ImageDraw.Draw(out, "RGBA")
    a0 = ease(t / 0.4)
    d.text((540, 316), "HOW ANTIFOULING WORKS", font=O(76), fill=WHITE + (int(255 * a0),), anchor="mm")
    pill(d, "HULL", (200, 1320), ease((t - 0.2) / 0.4), size=32)
    pill(d, "ANTIFOULING PAINT", (330, 1145), ease((t - 0.4) / 0.4), bg=WHITE, size=32)
    a = ease((t - 2.2) / 0.4)
    leader(d, (760, PAINT0 - 70), (800, 560), a); pill(d, "BIOCIDE", (800, 560), a, bg=GREEN, size=36)
    a = ease((t - 2.8) / 0.4)
    pill(d, "BARNACLE LARVAE", (300, 480), a, bg=(250, 180, 80), size=30)
    return out

# ================= HARD: sponge (12.2 s)  0-6.2 leaching, film stays ; 6.2-12.2 depleted, layers build up
def hard(t):
    flow = 260 if 2.8 < t < 6.4 else 60
    im = water_layer(t, flow); d = ImageDraw.Draw(im, "RGBA"); hull(d)
    dep = clamp(lerp(0.05, 0.55, t / 6.2)) if t < 6.2 else lerp(0.55, 1.05, ease((t - 6.2) / 1.6))
    # new layers stacking from t=8.6
    extra = [ease((t - 8.6 - k * 1.0) / 0.6) for k in range(3)]
    top = PAINT0
    draw_paint_block(d, PAINT0, HULL_TOP, porous=True, depleted_to=dep)
    for k, e in enumerate(extra):
        if e <= 0: continue
        th = 46; y1 = top; y0 = top - th * e
        d.rectangle([PX0, y0, PX1, y1], fill=(PAINT[0] - 18 * (k % 2), PAINT[1], PAINT[2], 255))
        d.line([(PX0, y1), (PX1, y1)], fill=(70, 15, 15, 255), width=4)
        top = y0
    strength = clamp(1 - dep) * (1 if t < 8.6 else 0)
    bio_cloud(im, t, PAINT0, 0.9 * strength); d = ImageDraw.Draw(im, "RGBA")
    if 7.2 < t < 8.8:  # barnacle settles on the exhausted film
        u = t - 7.2; a = clamp(u / 0.3) * (1 - clamp((t - 8.5) / 0.3))
        y = lerp(PY0 + 120, PAINT0, ease(u / 0.9))
        if u < 0.9: larva(d, 560, y, a, ang=t * 8)
        else: larva(d, 560, PAINT0, a, stuck=True)
    out = panel_frame(im); d = ImageDraw.Draw(out, "RGBA")
    header(d, "A", "HARD PAINT", GOLD, ease(t / 0.4))
    # thickness bracket (right edge)
    bx = PX1 - 70; a = ease((t - 0.6) / 0.4)
    if a > 0:
        d.line([(bx, top), (bx, HULL_TOP)], fill=WHITE + (int(255 * a),), width=5)
        for yy in (top, HULL_TOP): d.line([(bx - 18, yy), (bx + 18, yy)], fill=WHITE + (int(255 * a),), width=5)
    if t < 6.2:
        pill(d, "LIKE A SPONGE", (300, 1320), ease((t - 0.5) / 0.4), size=32)
        a = ease((t - 1.6) / 0.4); leader(d, (660, PAINT0 - 60), (700, 560), a)
        pill(d, "BIOCIDE LEACHES OUT", (620, 560), a, bg=GREEN, size=32)
        pill(d, "FILM STAYS", (bx - 170, 1320), ease((t - 3.4) / 0.4), bg=GOLD, size=30)
        checkrow(d, "HANDLES SPEED", 700, ease((t - 4.3) / 0.4))
        checkrow(d, "HANDLES SCRUBBING", 810, ease((t - 4.9) / 0.4))
    else:
        a = ease((t - 6.8) / 0.4)
        pill(d, "BIOCIDE USED UP", (540, 560), a, bg=CORAL, fg=WHITE, size=38)
        pill(d, "STOPS WORKING", (540, 660), ease((t - 7.4) / 0.4), bg=WHITE, fg=CORAL, size=34)
        a = ease((t - 8.8) / 0.4)
        if a > 0:
            pill(d, "NEW COAT", (300, top - 60), ease((t - 8.8) / 0.3), size=30)
            pill(d, "OLD LAYERS BUILD UP", (540, 800), ease((t - 9.6) / 0.4), bg=GOLD, size=36)
    return out

# ================= ABLATIVE: soap (8.5 s) surface wears away, fresh biocide always at the surface
def ablative(t):
    flow = 320
    im = water_layer(t, flow); d = ImageDraw.Draw(im, "RGBA"); hull(d)
    wear = 95 * ease((t - 1.2) / 6.6)
    top = PAINT0 + wear
    draw_paint_block(d, top, HULL_TOP, bands=True)
    # fresh-biocide glow line on the surface
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.rectangle([PX0, top - 8, PX1, top + 10], fill=BIO + (200,)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)))
    bio_cloud(im, t, top, 0.9); d = ImageDraw.Draw(im, "RGBA")
    # flakes being carried off by the flow
    rnd = random.Random(9)
    if t > 1.2:
        for i in range(40):
            ph = (t * 0.8 + rnd.random()) % 1; x0 = rnd.uniform(PX0, PX1)
            x = (x0 + ph * 420) % (PX1 - PX0) + PX0; y = top - 6 - ph * 120 - 30 * ph * ph
            a = int(230 * (1 - ph)); s = rnd.randint(5, 10)
            d.rectangle([x - s, y - s / 2, x + s, y + s / 2], fill=(200, 70, 60, a))
    # ghost of the original surface
    if wear > 4:
        for x in range(PX0 + 10, PX1 - 10, 40): d.line([(x, PAINT0), (x + 20, PAINT0)], fill=WHITE + (170,), width=3)
    out = panel_frame(im); d = ImageDraw.Draw(out, "RGBA")
    header(d, "B", "ABLATIVE PAINT", TURQ, ease(t / 0.4))
    pill(d, "LIKE A BAR OF SOAP", (370, 1320), ease((t - 0.5) / 0.4), size=32)
    a = ease((t - 1.6) / 0.4)
    pill(d, "WATER FLOW  >>>", (300, 520), a, bg=NAVY, fg=WHITE, size=32)
    a = ease((t - 2.6) / 0.4); leader(d, (820, PAINT0 + 10), (760, 660), a)
    pill(d, "SURFACE WEARS AWAY", (620, 660), a, bg=WHITE, size=32)
    a = ease((t - 4.4) / 0.4); leader(d, (330, top - 10), (360, 800), a)
    pill(d, "FRESH BIOCIDE", (360, 800), a, bg=GREEN, size=34)
    a = ease((t - 6.6) / 0.4)
    pill(d, "LESS BUILD-UP", (780, 540), a, bg=GOLD, size=34)
    return out

def render(name, dur, fn):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", name], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ims = [intro(1.0), intro(4.0), hard(2.0), hard(5.8), hard(7.9), hard(11.5), ablative(3.5), ablative(8.0)]
        sh = Image.new("RGB", (330 * 4, 590 * 2), "white")
        for i, im in enumerate(ims): sh.paste(im.convert("RGB").resize((320, 569)), ((i % 4) * 330, (i // 4) * 590))
        sh.save(sys.argv[2] if len(sys.argv) > 2 else "stills.png")
    elif sys.argv[1] == "frame":
        fn = {"intro": intro, "hard": hard, "ablative": ablative}[sys.argv[2]]
        fn(float(sys.argv[3])).convert("RGB").save(sys.argv[4])
    else:
        render("af_intro.mp4", 6.0, intro)
        render("af_hard.mp4", 12.4, hard)
        render("af_ablative.mp4", 8.8, ablative)
        print("ok")
