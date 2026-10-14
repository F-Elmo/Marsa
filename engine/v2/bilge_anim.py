"""Animated cut-away diagrams for the bilge-pump episode. Renders 3 MP4 clips 1080x1920@30."""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT = "/home/claude/ctm-reels/assets/fonts/montserrat-latin-%d-normal.woff"
FO = "/home/claude/ctm-reels/assets/fonts/oswald-latin-700-normal.woff"
def F(wt, sz): return ImageFont.truetype(FONT % wt, sz)
NAVY = (9, 24, 54); GOLD = (214, 172, 86); TURQ = (18, 196, 204); WATER = (40, 170, 220)
CORAL = (240, 90, 80); WHITE = (255, 255, 255); GREEN = (60, 210, 120)
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def lerp(a, b, t): return a + (b - a) * t

def bg():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([10, 30, 66]); bot = np.array([3, 10, 26])
    arr = (top * (1 - y[..., None]) + bot * y[..., None]).repeat(W, 1).astype(np.uint8)
    im = Image.fromarray(arr.reshape(H, W, 3)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=(80, 140, 220, 22))
    for yy in range(0, H, 54): d.line([(0, yy), (W, yy)], fill=(80, 140, 220, 22))
    return im
BG = bg()

# hull cross-section geometry (looking from the stern)
DECK_Y = 520; KEEL = (540, 1240)
HULL_OUT = [(90, DECK_Y), (130, 900), (300, 1150), KEEL, (780, 1150), (950, 900), (990, DECK_Y)]
HULL_IN = [(130, DECK_Y + 30), (165, 895), (320, 1120), (540, 1200), (760, 1120), (915, 895), (950, DECK_Y + 30)]
FLOOR_Y = 1010   # cabin floor (sole)
SEA_Y = 760      # outside waterline
THRU = (942, 690)  # through-hull outlet on the side, above waterline
PUMP = (640, 1150)
FLOAT_PIVOT = (420, 1150)

def hull_x_at(y, side):
    """x of inner hull at height y (side -1 left / +1 right)"""
    pts = HULL_IN[:4] if side < 0 else HULL_IN[3:][::-1]
    pts = sorted(pts, key=lambda p: p[1])
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if y1 <= y <= y2:
            return x1 + (x2 - x1) * (y - y1) / max(1, (y2 - y1))
    return pts[-1][0]

def water_poly(level):
    pts = [(hull_x_at(level, -1), level)]
    for p in HULL_IN[1:6]:
        if p[1] >= level: pts.append(p)
    pts.append((hull_x_at(level, 1), level))
    return pts

def draw_frame(t, mode):
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    # sea outside
    d.rectangle([0, SEA_Y, W, H], fill=(14, 90, 140, 150))
    for k in range(6):
        yy = SEA_Y + 6 * math.sin(t * 2 + k)
        d.line([(0 + k * 190, yy), (150 + k * 190, yy)], fill=(160, 230, 255, 120), width=3)
    # hull
    d.polygon(HULL_OUT, fill=(232, 238, 245, 255))
    d.polygon(HULL_IN, fill=(28, 44, 70, 255))
    d.line(HULL_OUT + [HULL_OUT[0]], fill=(255, 255, 255, 255), width=5)
    # engine silhouette above floor
    d.rounded_rectangle([380, 850, 700, 1000], radius=18, fill=(70, 86, 110, 255), outline=(150, 170, 200, 255), width=3)
    d.text((540, 925), "ENGINE", font=F(800, 30), fill=(200, 215, 235, 255), anchor="mm")

    # water level timeline
    if mode == "work":
        # 0-3 rise, 3-4.5 float lifts, 4.5 pump on, 4.5-10 drain, float drops ~9
        if t < 3.2: lvl = lerp(1200, 1080, ease(t / 3.2))
        elif t < 4.6: lvl = 1080 - 8 * ease((t - 3.2) / 1.4)
        else: lvl = lerp(1072, 1196, ease((t - 4.6) / 5.4))
        float_up = ease((t - 2.2) / 1.4) * (1 - ease((t - 8.6) / 1.0))
        pump_on = 4.4 < t < 9.6
    elif mode == "fail":
        lvl = lerp(1120, 900, ease(t / 7.0)); float_up = 0.0; pump_on = False
    else:
        lvl = 1185; float_up = 0; pump_on = False

    # bilge water (clip to inner hull)
    wl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); wd = ImageDraw.Draw(wl)
    if lvl < 1199:
        wd.polygon(water_poly(lvl), fill=WATER + (220,))
        xl, xr = hull_x_at(lvl, -1), hull_x_at(lvl, 1)
        for k in range(int(max(0, (xr - xl - 80) // 90))):
            xx = xl + 30 + k * 90
            wd.arc([xx, lvl - 8 + 4 * math.sin(t * 4 + k), xx + 60, lvl + 8], 200, 340, fill=(200, 245, 255, 200), width=3)
    im.alpha_composite(wl); d = ImageDraw.Draw(im, "RGBA")

    # pump body
    px, py = PUMP
    glow = (GREEN if pump_on else (120, 130, 150))
    if pump_on:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.ellipse([px - 80, py - 90, px + 80, py + 40], fill=GREEN + (120,)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(18)))
        d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([px - 42, py - 70, px + 42, py + 10], radius=14, fill=(230, 235, 242, 255), outline=glow + (255,), width=6)
    d.rectangle([px - 50, py + 4, px + 50, py + 20], fill=(200, 205, 215, 255))
    # discharge hose: pump top -> up the side -> through-hull
    hose = [(px, py - 70), (px, 1075), (800, 1010), (880, 820), (THRU[0] - 40, THRU[1] + 20), THRU]
    d.line(hose, fill=(250, 250, 250, 255), width=16, joint="curve"); d.line(hose, fill=(60, 70, 90, 255), width=8, joint="curve")
    if pump_on:
        # flowing dashes along hose
        for i in range(len(hose) - 1):
            (x1, y1), (x2, y2) = hose[i], hose[i + 1]; L = math.hypot(x2 - x1, y2 - y1)
            for s in np.arange(-(t * 260) % 40, L, 40):
                a = s / L; b = min(1, (s + 18) / L)
                d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=WATER + (255,), width=8)
        # jet out of the hull side
        for k in range(14):
            ph = ((t * 1.6 + k / 14) % 1)
            jx = THRU[0] + ph * 120; jy = THRU[1] + ph * ph * 160
            r = 9 * (1 - ph * 0.5)
            d.ellipse([jx - r, jy - r, jx + r, jy + r], fill=(150, 225, 255, int(255 * (1 - ph))))
    # through-hull fitting
    d.ellipse([THRU[0] - 14, THRU[1] - 14, THRU[0] + 14, THRU[1] + 14], fill=GOLD + (255,), outline=WHITE + (255,), width=3)

    # float switch: arm hinged at pivot, ball at end
    fx, fy = FLOAT_PIVOT
    ang = lerp(-2, -50, float_up) if mode != "fail" else -6
    ex = fx - 80 * math.cos(math.radians(ang)); ey = fy + 80 * math.sin(math.radians(ang))
    d.rectangle([fx - 18, fy - 14, fx + 18, fy + 14], fill=(200, 205, 215, 255))
    d.line([(fx, fy), (ex, ey)], fill=(230, 230, 240, 255), width=10)
    col = (255, 200, 40) if mode != "fail" else (120, 100, 60)
    d.ellipse([ex - 26, ey - 22, ex + 26, ey + 22], fill=col + (255,), outline=WHITE + (255,), width=3)
    if mode == "fail":  # grime + jam X
        for k in range(9):
            gx = fx - 110 + (k * 13) % 80; gy = fy - 10 + (k * 7) % 20
            d.ellipse([gx - 9, gy - 6, gx + 9, gy + 6], fill=(60, 50, 30, 230))
        a = clamp((t - 1.0) / 0.4)
        if a > 0:
            cx, cy = ex, ey - 90; s = 34
            d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=CORAL + (int(255 * a),), width=12)
            d.line([(cx - s, cy + s), (cx + s, cy - s)], fill=CORAL + (int(255 * a),), width=12)

    # labels (pill + leader)
    def label(txt, pt, at, color=WHITE, tcol=NAVY, start=0.0):
        a = clamp((t - start) / 0.4)
        if a <= 0: return
        f = F(800, 34); tw = f.getlength(txt)
        x, y = at; d.line([pt, (x, y)], fill=WHITE + (int(220 * a),), width=4)
        d.ellipse([pt[0] - 9, pt[1] - 9, pt[0] + 9, pt[1] + 9], fill=TURQ + (int(255 * a),), outline=WHITE + (int(255 * a),), width=3)
        d.rounded_rectangle([x - tw / 2 - 22, y - 30, x + tw / 2 + 22, y + 30], radius=30, fill=color + (int(245 * a),))
        d.text((x, y + 1), txt, font=f, fill=tcol + (int(255 * a),), anchor="mm")
    if mode == "work":
        label("BILGE", (540, 1185), (540, 1330), start=0.3)
        label("FLOAT SWITCH", (ex, ey), (240, 1290), start=2.4)
        label("PUMP", (px + 30, py - 30), (820, 1290), color=GREEN if pump_on else WHITE, start=4.4)
        label("OVERBOARD", (THRU[0] + 60, THRU[1] + 40), (840, 610), color=TURQ, tcol=WHITE, start=5.4)
        if pump_on:
            a = clamp((t - 4.5) / 0.3)
            d.rounded_rectangle([395, 330, 685, 400], radius=35, fill=GREEN + (int(240 * a),))
            d.text((540, 366), "PUMP ON", font=F(800, 40), fill=NAVY + (int(255 * a),), anchor="mm")
    elif mode == "fail":
        label("FLOAT JAMMED", (fx - 60, fy - 10), (300, 1300), color=CORAL, tcol=WHITE, start=0.8)
        a = clamp((t - 0.4) / 0.3)
        d.rounded_rectangle([370, 330, 710, 400], radius=35, fill=CORAL + (int(240 * a),))
        d.text((540, 366), "PUMP OFF", font=F(800, 40), fill=WHITE + (int(255 * a),), anchor="mm")
        a2 = clamp((t - 3.0) / 0.4)
        if a2 > 0:
            d.rounded_rectangle([240, 430, 840, 500], radius=35, fill=(255, 255, 255, int(235 * a2)))
            d.text((540, 466), "WATER KEEPS RISING", font=F(800, 38), fill=CORAL + (int(255 * a2),), anchor="mm")
    return im

def checklist_frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    a0 = clamp(t / 0.4)
    d.text((540, 420), "3 THINGS", font=ImageFont.truetype(FO, 120), fill=WHITE + (int(255 * a0),), anchor="mm")
    d.text((540, 530), "EVERY BOAT NEEDS", font=ImageFont.truetype(FO, 70), fill=GOLD + (int(255 * a0),), anchor="mm")
    items = [("1", "A clean float switch", 0.8), ("2", "A backup pump, mounted higher", 2.0), ("3", "A high-water alarm", 3.4)]
    for i, (n, txt, st) in enumerate(items):
        a = clamp((t - st) / 0.35); y = 720 + i * 190; dx = (1 - a) * 80
        if a <= 0: continue
        d.rounded_rectangle([90 + dx, y - 75, 990 + dx, y + 75], radius=36, fill=(255, 255, 255, int(240 * a)))
        d.ellipse([125 + dx, y - 48, 221 + dx, y + 48], fill=TURQ + (int(255 * a),))
        d.text((173 + dx, y + 2), n, font=ImageFont.truetype(FO, 64), fill=WHITE + (int(255 * a),), anchor="mm")
        d.text((250 + dx, y), txt, font=F(800, 40), fill=NAVY + (int(255 * a),), anchor="lm")
    a4 = clamp((t - 5.2) / 0.4)
    if a4 > 0:
        d.rounded_rectangle([170, 1330, 910, 1410], radius=40, fill=GOLD + (int(245 * a4),))
        d.text((540, 1371), "TEST IT EVERY MONTH", font=F(800, 40), fill=NAVY + (int(255 * a4),), anchor="mm")
    return im

def render(name, dur, fn):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", name], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(fn(i / FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ims = [draw_frame(1, "work"), draw_frame(4, "work"), draw_frame(6.5, "work"), draw_frame(4, "fail"), checklist_frame(6)]
        sh = Image.new("RGB", (330 * 5, 586), "white")
        for i, im in enumerate(ims): sh.paste(im.convert("RGB").resize((320, 569)), (i * 330, 0))
        sh.save("stills.png")
    else:
        render("bilge_work.mp4", 10.5, lambda t: draw_frame(t, "work"))
        render("bilge_fail.mp4", 7.0, lambda t: draw_frame(t, "fail"))
        render("bilge_checklist.mp4", 8.0, checklist_frame)
        print("ok")
