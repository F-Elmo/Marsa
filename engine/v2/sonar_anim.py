"""Animated side-view diagrams for ep 015 (forward-looking sonar). Renders 4 MP4 clips 1080x1920@30.
  python3 engine/v2/sonar_anim.py OUTDIR [name ...]      names: look, echo, screen, range
  python3 engine/v2/sonar_anim.py OUTDIR --still name t   (single PNG for checking)"""
import math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FD = "/home/claude/ctm-reels/assets/fonts/"
def M(wt, sz): return ImageFont.truetype(FD + f"montserrat-latin-{wt}-normal.woff", sz)
def O(sz): return ImageFont.truetype(FD + "oswald-latin-700-normal.woff", sz)
NAVY = (9, 24, 54); GOLD = (214, 172, 86); TURQ = (18, 196, 204); WHITE = (255, 255, 255)
CORAL = (240, 90, 80); AMBER = (245, 170, 40); GREEN = (60, 205, 130); SAND = (196, 170, 120)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)

def vgrad(h, top, bot):
    y = np.linspace(0, 1, h)[:, None, None]
    return (np.array(top) * (1 - y) + np.array(bot) * y).repeat(W, 1).astype(np.uint8)

SURF = 620
def base_bg():
    arr = np.zeros((H, W, 3), np.uint8)
    arr[:SURF] = vgrad(SURF, (8, 22, 52), (22, 70, 120))
    arr[SURF:] = vgrad(H - SURF, (16, 120, 160), (3, 14, 34))
    im = Image.fromarray(arr); d = ImageDraw.Draw(im, "RGBA")
    for k in range(7):  # soft light rays
        x0 = 120 + k * 150
        d.polygon([(x0, SURF), (x0 + 60, SURF), (x0 - 120, 1350), (x0 - 230, 1350)], fill=(180, 240, 255, 10))
    return im
BG = base_bg()

SEABED = [(0, 1250), (560, 1250), (640, 1235), (700, 1120), (760, 960), (820, 850), (880, 812), (940, 822), (1000, 900), (1080, 960)]
def seabed(d, alpha=1.0, hl=0.0):
    poly = SEABED + [(W, 1420), (0, 1420)]
    d.polygon(poly, fill=A(SAND, 0.9 * alpha))
    reef = SEABED[2:] + [(W, 1420), (640, 1420)]
    col = tuple(int(lerp(c1, c2, hl)) for c1, c2 in zip((150, 95, 80), (235, 110, 85)))
    d.polygon(reef, fill=A(col, alpha))
    for i, (x, y) in enumerate([(720, 1150), (790, 940), (850, 880), (905, 850), (960, 900), (1030, 980), (760, 1060), (880, 950)]):
        r = 16 + (i % 3) * 8
        d.ellipse([x - r, y - r, x + r, y + r], fill=A((255, 150, 120), 0.35 * alpha))
    d.line(SEABED, fill=A(WHITE, 0.35 * alpha), width=3)
    # fade bottom into dark (caption area stays calm)
    return

def fade_bottom(im):
    a = np.zeros((H, W), np.uint8); a[1330:1460] = np.linspace(0, 255, 130).astype(np.uint8)[:, None]; a[1460:] = 255
    im.paste(Image.new("RGB", (W, H), (3, 12, 30)), (0, 0), Image.fromarray(a))

def surface(d, t):
    for k in range(9):
        x = (k * 140 + t * 40) % (W + 140) - 70
        d.line([(x, SURF + 4 * math.sin(t * 2 + k)), (x + 80, SURF + 4 * math.sin(t * 2 + k))], fill=(200, 245, 255, 150), width=3)
    d.line([(0, SURF), (W, SURF)], fill=(170, 230, 250, 120), width=2)

def boat(d, x0=90, y=SURF, s=1.0, bob=0.0):
    y += bob
    P = lambda px, py: (x0 + px * s, y + py * s)
    hull = [P(0, -62), P(330, -62), P(370, -56), P(345, -20), P(300, 38), P(40, 40), P(6, 22)]
    d.polygon(hull, fill=(240, 244, 250, 255))
    d.line([P(8, -6), P(338, -6)], fill=NAVY + (255,), width=max(2, int(7 * s)))
    d.polygon([P(70, -62), P(90, -120), P(250, -120), P(285, -62)], fill=(225, 232, 242, 255))
    d.polygon([P(105, -110), P(240, -110), P(262, -74), P(95, -74)], fill=(30, 60, 100, 255))
    d.line([P(160, -120), P(160, -160)], fill=(200, 210, 225, 255), width=max(2, int(5 * s)))

def pill(d, cx, cy, s, f, bg, fg, a=1.0, padx=26, h=None):
    if a <= 0.01: return
    tw = f.getlength(s); h = h or int(f.size * 1.75)
    cx = clamp(cx, 50 + tw / 2 + padx, W - 50 - tw / 2 - padx)
    d.rounded_rectangle([cx - tw / 2 - padx, cy - h / 2, cx + tw / 2 + padx, cy + h / 2], radius=h // 2, fill=A(bg, 0.96 * a))
    d.text((cx, cy + 1), s, font=f, fill=A(fg, a), anchor="mm")

def title(d, tag, line, t, col=GOLD, y=330):
    a = ease(t / 0.4)
    pill(d, W / 2, y, tag, M(800, 30), col, NAVY, a, h=56)
    if line:
        d.text((W / 2, y + 92 + (1 - a) * 30), line, font=O(70), fill=A(WHITE, a), anchor="mm", stroke_width=4, stroke_fill=A((3, 12, 30), a))

def wedge(d, o, ang_c, half, r, col, a):
    pts = [o] + [(o[0] + r * math.cos(math.radians(ang_c + k)), o[1] + r * math.sin(math.radians(ang_c + k)))
                 for k in np.linspace(-half, half, 24)]
    d.polygon(pts, fill=A(col, a))

def arcs(d, o, ang_c, half, t, speed, period, rmax, col, a=1.0, t0=0.0, width=7):
    n = int((t - t0) / period) + 1
    for i in range(max(0, n - 6), n):
        r = (t - t0 - i * period) * speed
        if r <= 4 or r > rmax: continue
        fa = a * (1 - r / rmax) ** 0.6
        d.arc([o[0] - r, o[1] - r, o[0] + r, o[1] + r], ang_c - half, ang_c + half, fill=A(col, fa), width=width)

def leader(d, pt, lab, txt, prog, bg=WHITE, fg=NAVY):
    if prog <= 0: return
    a = ease(prog); mx, my = lerp(pt[0], lab[0], a), lerp(pt[1], lab[1], a)
    d.line([pt, (mx, my)], fill=A(WHITE, a), width=4)
    d.ellipse([pt[0] - 11, pt[1] - 11, pt[0] + 11, pt[1] + 11], outline=A(WHITE, a), width=4)
    d.ellipse([pt[0] - 5, pt[1] - 5, pt[0] + 5, pt[1] + 5], fill=A(TURQ, a))
    if prog > 0.45: pill(d, lab[0], lab[1], txt, M(800, 30), bg, fg, ease((prog - 0.45) / 0.55), h=56)

BOW_T = (432, 668)   # forward transducer (bow, below waterline)
BELLY_T = (250, 662)
HIT = (760, 960)

# ---------------------------------------------------------------- 1: looks down vs looks ahead (5.1 s)
def f_look(t):
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    rot = ease((t - 3.0) / 1.0)
    seabed(d, hl=rot); fade_bottom(im); d = ImageDraw.Draw(im, "RGBA")
    o = (lerp(BELLY_T[0], BOW_T[0], rot), lerp(BELLY_T[1], BOW_T[1], rot))
    ang = lerp(90, 30, rot); half = lerp(13, 24, rot)
    col = GOLD if rot < 0.5 else TURQ
    wedge(d, o, ang, half, lerp(590, 640, rot), col, 0.3)
    arcs(d, o, ang, half, t, 520, 0.42, 620, col, width=8)
    surface(d, t); boat(d, bob=3 * math.sin(t * 2.2))
    if rot < 0.5:
        title(d, "DEPTH SOUNDER", "LOOKS STRAIGHT DOWN", t, GOLD)
        a = ease((t - 1.0) / 0.4) * (1 - ease((rot - 0.2) / 0.3))
        pill(d, 850, 700, "REEF AHEAD?", M(800, 32), CORAL, WHITE, a, h=60)
    else:
        title(d, "FORWARD-LOOKING SONAR", "LOOKS AHEAD", t - 3.6, TURQ)
        pill(d, 860, 700, "REEF SEEN EARLY", M(800, 30), TURQ, NAVY, ease((t - 4.2) / 0.4), h=58)
    return im

# ---------------------------------------------------------------- 2: pulse out, echo back, time = distance (9.8 s)
def f_echo(t):
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    seabed(d, hl=0.6); fade_bottom(im); d = ImageDraw.Draw(im, "RGBA")
    o = BOW_T; ang = 30; half = 24
    wedge(d, o, ang, half, 640, TURQ, 0.2)
    dist = math.dist(o, HIT); SP = 300; PER = 1.6; T0 = 0.4
    arcs(d, o, ang, half, t, SP, PER, dist + 10, TURQ, t0=T0, width=9)
    back_ang = math.degrees(math.atan2(o[1] - HIT[1], o[0] - HIT[0]))
    n = int((t - T0) / PER) + 1
    for i in range(max(0, n - 6), n):  # echoes start when each pulse reaches the reef
        te = T0 + i * PER + dist / SP
        r = (t - te) * SP
        if 4 < r < dist:
            d.arc([HIT[0] - r, HIT[1] - r, HIT[0] + r, HIT[1] + r], back_ang - 14, back_ang + 14, fill=A(GOLD, 1 - 0.6 * r / dist), width=9)
        if 0 <= t - te < 0.35:
            rr = 20 + 60 * (t - te); d.ellipse([HIT[0] - rr, HIT[1] - rr, HIT[0] + rr, HIT[1] + rr], outline=A(WHITE, 1 - (t - te) / 0.35), width=5)
    surface(d, t); boat(d, bob=3 * math.sin(t * 2.2))
    title(d, "HOW IT WORKS", "SOUND OUT  ·  ECHO BACK", t, TURQ)
    leader(d, (o[0] - 4, o[1] - 6), (300, 780), "TRANSDUCER", (t - 0.2) / 0.6)
    pill(d, 290, 880, "SOUND PULSE", M(800, 28), TURQ, NAVY, ease((t - 1.0) / 0.4) * (1 - ease((t - 4.4) / 0.4)), h=54)
    pill(d, 290, 960, "ECHO", M(800, 28), GOLD, NAVY, ease((t - 2.6) / 0.4) * (1 - ease((t - 4.4) / 0.4)), h=54)
    # distance + height (after "the time they take...")
    pd = ease((t - 4.6) / 0.8)
    if pd > 0:
        ex, ey = lerp(o[0], HIT[0], pd), lerp(o[1], HIT[1], pd)
        for k in range(0, 60):
            f0, f1 = k / 60, (k + 0.55) / 60
            if f1 > pd: break
            d.line([(lerp(o[0], HIT[0], f0), lerp(o[1], HIT[1], f0)), (lerp(o[0], HIT[0], f1), lerp(o[1], HIT[1], f1))], fill=A(WHITE, 1), width=6)
        pill(d, 470, 860, "ECHO TIME = DISTANCE", M(800, 28), WHITE, NAVY, ease((t - 5.2) / 0.4), h=56)
    ph = ease((t - 7.2) / 0.7)
    if ph > 0:
        x = 965; yb, yt = 1250, lerp(1250, 812, ph)
        d.line([(x, yb), (x, yt)], fill=A(GOLD, 1), width=8)
        d.polygon([(x, yt - 22), (x - 18, yt + 8), (x + 18, yt + 8)], fill=A(GOLD, 1))
        pill(d, 880, 1180, "REEF HEIGHT", M(800, 28), GOLD, NAVY, ease((t - 7.6) / 0.4), h=56)
    pill(d, W / 2, 1370, "SOUND TRAVELS ~1,500 m PER SECOND IN SEAWATER", M(700, 25), NAVY, WHITE, ease((t - 5.6) / 0.5) * 0.95, h=50)
    return im

# ---------------------------------------------------------------- 3: the screen + shallow alarm (5.5 s)
SCR = (80, 300, 1000, 1330)
def depth_at(x):  # simulated profile, metres below surface, along screen x (0..1)
    return 14 - 11 * ease((x - 0.45) / 0.4) + 0.5 * math.sin(x * 23)
def f_screen(t):
    im = Image.new("RGB", (W, H), (3, 12, 30)); d = ImageDraw.Draw(im, "RGBA")
    x0, y0, x1, y1 = SCR
    d.rounded_rectangle([x0 - 26, y0 - 26, x1 + 26, y1 + 26], radius=44, fill=(28, 34, 44, 255), outline=(70, 80, 96, 255), width=4)
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(4, 16, 36, 255))
    d.text((x0 + 30, y0 + 40), "FORWARD SONAR", font=M(800, 34), fill=(150, 220, 240, 255), anchor="lm")
    d.text((x1 - 30, y0 + 40), "AHEAD  >>", font=M(700, 30), fill=(150, 220, 240, 255), anchor="rm")
    top, bot = y0 + 150, y1 - 40; sx0 = x0 + 150
    ymap = lambda m: top + (bot - top) * m / 16
    d.line([(x0 + 20, top), (x1 - 20, top)], fill=(120, 200, 230, 200), width=3)
    for m in (4, 8, 12):
        d.line([(x0 + 20, ymap(m)), (x1 - 20, ymap(m))], fill=(60, 110, 150, 90), width=2)
        d.text((x0 + 30, ymap(m) - 18), f"{m} m", font=M(600, 24), fill=(110, 160, 190, 255), anchor="lm")
    # boat icon
    d.polygon([(sx0 - 110, top - 30), (sx0 - 10, top - 30), (sx0 + 10, top - 12), (sx0 - 20, top + 8), (sx0 - 100, top + 8)], fill=(240, 244, 250, 255))
    prog = ease(t / 2.6); n = int((x1 - 30 - sx0) / 6)
    alarm_m = 5.0
    for i in range(int(n * prog)):
        fx = i / n; m = depth_at(fx); x = sx0 + i * 6
        col = GREEN if m > 9 else (AMBER if m > alarm_m else CORAL)
        d.rectangle([x, ymap(m), x + 5, bot], fill=col + (235,))
    # alarm line
    al = ease((t - 2.4) / 0.4)
    ya = ymap(alarm_m)
    for xx in range(x0 + 20, x1 - 20, 34):
        d.line([(xx, ya), (xx + 18, ya)], fill=A(CORAL, al), width=4)
    if al > 0: d.text((x0 + 150, ya - 22), "ALARM DEPTH", font=M(800, 24), fill=A(CORAL, al), anchor="rm")
    fl = ease((t - 3.2) / 0.3) * (0.65 + 0.35 * math.sin(t * 14))
    if fl > 0:
        cx, cy = W / 2, y0 + 105; fpl = M(800, 34); lab = "      SHALLOW WATER AHEAD"; tw = fpl.getlength(lab)
        pill(d, cx, cy, lab, fpl, CORAL, WHITE, fl, h=66, padx=36)
        tx = cx - tw / 2 + 26
        d.polygon([(tx, cy - 22), (tx - 24, cy + 20), (tx + 24, cy + 20)], fill=A(WHITE, fl))
        d.text((tx, cy + 6), "!", font=M(800, 30), fill=A(CORAL, fl), anchor="mm")
    title(d, "ON YOUR SCREEN", None, t, TURQ, y=210)
    return im

# ---------------------------------------------------------------- 4: range ~ 8x depth (8.4 s)
def panel(im, box, surf_y, bed_y, t, reach, label, sub, a, scale_note=None, dims=None):
    if a <= 0: return
    lay = im.copy(); d = ImageDraw.Draw(lay, "RGBA")
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=30, fill=(8, 28, 60, 255), outline=(60, 120, 170, 255), width=3)
    d.rectangle([x0 + 3, surf_y, x1 - 3, bed_y], fill=(18, 110, 150, 255))
    d.rectangle([x0 + 3, bed_y, x1 - 3, y1 - 30], fill=SAND + (255,))
    d.rounded_rectangle([x0 + 3, y1 - 40, x1 - 3, y1 - 3], radius=26, fill=SAND + (255,))
    for k in range(8):
        xx = (x0 + 40 + k * 120 + t * 30) % (x1 - x0 - 60) + x0 + 20
        d.line([(xx, surf_y), (xx + 50, surf_y)], fill=(200, 245, 255, 160), width=3)
    bx = x0 + 40; bow = (bx + 150, surf_y + 14)
    end = min(x1 - 20, bow[0] + reach * ease(t / 1.2))
    ang = math.degrees(math.atan2(bed_y - bow[1], end - bow[0]))
    d.polygon([bow, (end, bed_y), (end, max(surf_y + 4, bed_y - (end - bow[0]) * 0.18)) if reach > 900 else (end, bed_y - 4), bow], fill=A(TURQ, 0.35))
    d.line([bow, (end, bed_y)], fill=A(TURQ, 0.9), width=4)
    if end < x1 - 40:  # beyond range = unknown
        d.rectangle([end + 6, surf_y + 6, x1 - 6, bed_y], fill=(4, 18, 40, 170))
        d.text((x1 - 50, (surf_y + bed_y) / 2), "?", font=O(56), fill=(200, 230, 255, 200), anchor="mm")
    # boat (small)
    s = 0.48; P = lambda px, py: (bx + px * s, surf_y + py * s)
    d.polygon([P(0, -62), P(330, -62), P(370, -56), P(345, -20), P(300, 30), P(40, 30), P(6, 18)], fill=(240, 244, 250, 255))
    d.polygon([P(70, -62), P(90, -115), P(250, -115), P(285, -62)], fill=(225, 232, 242, 255))
    d.text((x0 + 30, y0 + 38), label, font=M(800, 32), fill=WHITE + (255,), anchor="lm")
    if sub: d.text((x1 - 30, y0 + 38), sub, font=M(700, 28), fill=(150, 220, 240, 255), anchor="rm")
    if dims: dims(d, bow, end, bed_y)
    im.paste(Image.blend(im, lay, clamp(a)))

def f_range(t):
    im = Image.new("RGB", (W, H), (3, 12, 30)); d = ImageDraw.Draw(im, "RGBA")
    title(d, "THE CATCH", "RANGE DEPENDS ON DEPTH", t, CORAL, y=300)
    panel(im, (60, 460, 1020, 880), 600, 840, t - 0.3, 2000, "DEEP WATER", "SEES FAR AHEAD", ease((t - 0.3) / 0.4))
    d = ImageDraw.Draw(im, "RGBA")
    pill(d, W / 2, 925, "ABOUT 8 x THE DEPTH AHEAD *", M(800, 32), GOLD, NAVY, ease((t - 1.6) / 0.4), h=62)
    def dims(dd, bow, end, bed):
        a = ease((t - 5.4) / 0.5)
        if a <= 0: return
        xd = end + 50; sy = bow[1] - 14
        dd.line([(xd, sy), (xd, bed)], fill=A(GOLD, a), width=5)
        for yy in (sy, bed): dd.line([(xd - 14, yy), (xd + 14, yy)], fill=A(GOLD, a), width=5)
        dd.text((xd - 22, (sy + bed) / 2), "3 m", font=M(800, 28), fill=A(GOLD, a), anchor="rm")
        yb = bed + 46
        dd.line([(bow[0], yb), (end, yb)], fill=A(NAVY, a), width=5)
        for xx in (bow[0], end): dd.line([(xx, yb - 16), (xx, yb + 16)], fill=A(NAVY, a), width=5)
        dd.text(((bow[0] + end) / 2, yb + 38), "8 x 3 m  =  ABOUT 24 m", font=M(800, 30), fill=A(NAVY, a), anchor="mm")
    panel(im, (60, 975, 1020, 1350), 1095, 1155, t - 4.0, 480, "SHALLOW WATER: 3 m", "SEES ONLY 24 m", ease((t - 4.0) / 0.4), dims=dims)
    d = ImageDraw.Draw(im, "RGBA")
    d.text((W / 2, 1385), "* figure quoted for Simrad ForwardScan", font=M(600, 22), fill=(130, 160, 190, int(255 * ease((t - 1.6) / 0.4))), anchor="mm")
    return im

CLIPS = {"look": (f_look, 5.4), "echo": (f_echo, 10.1), "screen": (f_screen, 5.8), "range": (f_range, 8.7)}

def render(outdir, name):
    fn, dur = CLIPS[name]; out = os.path.join(outdir, f"sonar_{name}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)): p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait(); print("->", out)

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == "--still":
        nm, tt = sys.argv[3], float(sys.argv[4]); CLIPS[nm][0](tt).convert("RGB").save(os.path.join(outdir, f"still_{nm}_{tt}.png"))
    else:
        for nm in (sys.argv[2:] or CLIPS): render(outdir, nm)
