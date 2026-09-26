"""Illustrations for episode 002 (engine cooling). Run from repo root: python3 episodes/art/002_diagrams.py"""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

def spray(d, x, y, n=60, seed=3):
    rnd = random.Random(seed)
    for i in range(n):
        t = rnd.random(); ang = rnd.uniform(-0.35, 0.25)
        vx, vy = 150 * math.cos(ang), 150 * math.sin(ang)
        px, py = x + vx * t * 0.7, y + vy * t + 170 * t * t
        r = rnd.uniform(3, 8); a = int(230 - 120 * t)
        d.ellipse([px - r, py - r, px + r, py + r], fill=(220, 250, 255, a))

# ---------------- 1. big stern cut-away with the raw-water path
WL = 1000
im, d = canvas("sea", waterline=WL)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); h = ImageDraw.Draw(lay)
h.polygon([(-40, 640), (740, 640), (760, 720), (-40, 720)], fill=(250, 251, 252, 255))           # saloon level
h.polygon([(40, 656), (420, 656), (420, 704), (40, 704)], fill=(28, 44, 66, 255))
h.polygon([(-40, 720), (920, 720), (920, 1160), (-40, 1240)], fill=(245, 247, 250, 255))         # hull topsides
h.polygon([(-40, 985), (920, 985), (920, 1160), (-40, 1240)], fill=(24, 36, 58, 255))            # bottom paint
h.line([(-40, 730), (920, 730)], fill=GOLD + (255,), width=5)
im.alpha_composite(lay); d = ImageDraw.Draw(im, "RGBA")
win = (90, 770, 870, 1130)
d.rounded_rectangle(win, radius=26, fill=(214, 224, 236, 255), outline=GOLD_L + (255,), width=6)
d.line([(110, 1100), (850, 1100)], fill=(150, 160, 175, 255), width=6)
eng = (370, 880, 620, 1080)
d.rounded_rectangle(eng, radius=16, fill=(70, 82, 100, 255), outline=WHITE + (255,), width=4)
for i in range(4):
    cx = 405 + i * 60
    d.rounded_rectangle([cx - 22, 840, cx + 22, 886], radius=8, fill=(96, 110, 130, 255), outline=WHITE + (160,), width=2)
for yy in range(930, 1060, 30): d.line([(395, yy), (595, yy)], fill=(100, 114, 134, 255), width=5)
hx = (660, 830, 800, 890)
seacock = (215, 1200); strainer = (215, 960); pump = (350, 1030); exh_out = (920, 950)
pipe(d, [seacock, (215, 1000)], TURQ, width=16)
pipe(d, [(215, 920), (215, 800), (300, 800), (300, 1030), (332, 1030)], TURQ, width=16)
pipe(d, [(620, 1000), (730, 1000), (730, 890)], TURQ, width=16)
pipe(d, [(760, 830), (760, 800), (840, 800), (840, 950), (905, 950)], (190, 198, 210), width=22)
d.rounded_rectangle(hx, radius=28, fill=GOLD + (255,), outline=WHITE + (255,), width=4)
for yy in (846, 860, 874): d.line([(676, yy), (784, yy)], fill=(255, 235, 190, 255), width=3)
d.rounded_rectangle([180, 915, 250, 1005], radius=14, fill=(236, 240, 246, 255), outline=NAVY + (255,), width=5)
for yy in (940, 960, 980): d.line([(195, yy), (235, yy)], fill=NAVY + (255,), width=3)
d.ellipse([seacock[0] - 26, seacock[1] - 26, seacock[0] + 26, seacock[1] + 26], fill=(205, 127, 50, 255), outline=WHITE + (255,), width=5)
d.line([(seacock[0] - 16, seacock[1]), (seacock[0] + 16, seacock[1])], fill=WHITE + (255,), width=6)
d.ellipse([pump[0] - 30, pump[1] - 30, pump[0] + 30, pump[1] + 30], fill=CORAL + (255,), outline=WHITE + (255,), width=5)
for k in range(4):
    a = k * math.pi / 2; d.line([pump, (pump[0] + 20 * math.cos(a), pump[1] + 20 * math.sin(a))], fill=WHITE + (255,), width=5)
d.rounded_rectangle([900, 932, 930, 968], radius=6, fill=(160, 170, 185, 255))
spray(d, 928, 950, n=90)
for k in range(3):
    yy = seacock[1] + 60 + k * 40
    d.polygon([(seacock[0], yy - 22), (seacock[0] - 16, yy), (seacock[0] + 16, yy)], fill=(230, 250, 255, 210 - k * 55))
save(im, "ep002-cutaway")

# ---------------- 2. fresh-water (closed) loop schematic
im, d = canvas("blueprint")
def glowline(pts, col, w=22):
    glow(im, lambda g: g.line(pts, fill=col + (255,), width=w, joint="curve"), radius=10)
glowline([(480, 860), (800, 860), (800, 880)], CORAL)           # hot coolant out
glowline([(800, 1040), (800, 1210), (330, 1210), (330, 1140)], GOLD)  # cooled coolant back
d = ImageDraw.Draw(im, "RGBA")
pipe(d, [(480, 860), (800, 860), (800, 880)], CORAL, width=22)
pipe(d, [(800, 1040), (800, 1210), (330, 1210), (330, 1140)], GOLD, width=22)
# engine block
d.rounded_rectangle([170, 800, 490, 1140], radius=24, fill=(60, 74, 96, 255), outline=STEEL + (255,), width=5)
for i in range(4):
    cx = 215 + i * 77
    d.rounded_rectangle([cx - 28, 740, cx + 28, 806], radius=10, fill=(84, 100, 124, 255), outline=STEEL + (255,), width=3)
    d.ellipse([cx - 24, 880, cx + 24, 928], outline=(255, 150, 120, 200), width=4)
for yy in range(960, 1110, 36): d.line([(200, yy), (460, yy)], fill=(120, 136, 160, 255), width=6)
# heat exchanger (cylinder with tube bundle)
d.rounded_rectangle([690, 880, 910, 1040], radius=40, fill=(40, 70, 110, 255), outline=GOLD_L + (255,), width=5)
for yy in range(910, 1020, 22): d.line([(705, yy), (895, yy)], fill=TURQ + (220,), width=6)
pipe(d, [(1000, 1010), (910, 1010)], TURQ, width=18)
pipe(d, [(910, 910), (1000, 910)], TURQ, width=18)
d.text((955, 1072), "SEAWATER IN", font=F(800, 22), fill=TURQ + (255,), anchor="mm")
d.text((955, 848), "SEAWATER OUT", font=F(800, 22), fill=TURQ + (255,), anchor="mm")
d.text((640, 820), "HOT", font=F(800, 26), fill=(255, 170, 150, 255), anchor="mm")
d.text((560, 1255), "COOLED", font=F(800, 26), fill=GOLD_L + (255,), anchor="mm")
save(im, "ep002-freshloop")

# ---------------- 3. impeller close-up (new) and 4. (worn)
def impeller(worn=False):
    im, d = canvas("blueprint")
    C = (540, 960)
    d.ellipse([C[0] - 360, C[1] - 360, C[0] + 360, C[1] + 360], fill=(150, 162, 178, 255), outline=WHITE + (255,), width=6)
    for k in range(6):
        a = k * math.pi / 3 + 0.3; bx, by = C[0] + 335 * math.cos(a), C[1] + 335 * math.sin(a)
        d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=(110, 120, 135, 255), outline=WHITE + (200,), width=2)
    d.ellipse([C[0] - 300, C[1] - 300, C[0] + 300, C[1] + 300], fill=(18, 40, 70, 255))
    d.chord([C[0] - 300, C[1] - 300, C[0] + 300, C[1] + 300], 200, 340, fill=(120, 132, 148, 255))  # cam
    rnd = random.Random(7); vane = (32, 44, 60)
    for k in range(12):
        a0 = math.radians(15 + k * 30)
        if worn and k in (2, 3, 7):   # broken vanes: short stubs
            L = 120
        else:
            L = 290 if not (200 <= (15 + k * 30) <= 340) else 215   # vanes squeezed by the cam
        pts = []
        for j in range(12):
            r = 90 + (L - 90) * j / 11; bend = -0.30 * (j / 11) ** 2 if L < 250 else -0.06 * (j / 11) ** 2
            pts.append((C[0] + r * math.cos(a0 + bend), C[1] + r * math.sin(a0 + bend)))
        d.line(pts, fill=vane + (255,), width=40, joint="curve")
        tx, ty = pts[-1]; d.ellipse([tx - 24, ty - 24, tx + 24, ty + 24], fill=vane + (255,))
        if worn and k in (2, 3, 7):
            d.ellipse([tx - 30, ty - 30, tx + 30, ty + 30], outline=CORAL + (255,), width=6); d.line([(tx - 20, ty - 12), (tx + 18, ty + 14)], fill=CORAL + (255,), width=6)
        elif worn and k in (0, 5, 9):
            mx, my = pts[6]; d.line([(mx - 10, my - 14), (mx + 12, my + 10)], fill=(120, 130, 150, 255), width=4)
    d.ellipse([C[0] - 100, C[1] - 100, C[0] + 100, C[1] + 100], fill=vane + (255,), outline=(60, 76, 96, 255), width=6)
    d.ellipse([C[0] - 46, C[1] - 46, C[0] + 46, C[1] + 46], fill=(205, 170, 90, 255), outline=WHITE + (255,), width=4)
    d.rectangle([C[0] - 10, C[1] - 46, C[0] + 10, C[1] - 22], fill=(18, 40, 70, 255))
    if worn:
        for (fx, fy, fa) in ((250, 1330, 0.4), (820, 1360, -0.8), (900, 1290, 1.2)):
            pts = [(fx + 60 * math.cos(fa + s), fy + 60 * math.sin(fa + s)) for s in (0, 0.5, math.pi, math.pi + 0.4)]
            d.polygon(pts, fill=vane + (255,), outline=CORAL + (255,))
    return im
save(impeller(False), "ep002-impeller")
save(impeller(True), "ep002-impeller-worn")

# ---------------- 5. calm background for the call-to-action (faint impeller on blueprint)
bg, _ = canvas("blueprint")
save(Image.blend(bg, impeller(True).resize((W, H)), 0.28), "ep002-cta")
