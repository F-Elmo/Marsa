"""Illustrations for episode 004 (why diesel goes bad in Red Sea heat). Run from repo root: python3 episodes/art/004_diagrams.py
New look for this episode: warm amber 'heat' palette, fuel-tank cut-aways, a microscope view and a filter bowl
(previous episodes were blue sea / blueprint)."""
import sys, math, random; sys.path.insert(0, "engine")
from diagram import *

AMBER = (232, 170, 60); AMBER_D = (170, 110, 30); WATER = (70, 150, 210); SLIME = (34, 30, 22)

def heat_canvas(top=(250, 150, 60), mid=(150, 60, 50), bot=(12, 22, 48)):
    arr = vgrad([(0, top), (0.42, mid), (1, bot)])
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    # heat shimmer bands
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    for k in range(9):
        y = 120 + k * 60
        g.line([(x, y + 14 * math.sin(x / 70 + k)) for x in range(0, W + 20, 20)], fill=(255, 220, 150, 40), width=6)
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
    return im, ImageDraw.Draw(im, "RGBA")

def sun(im, c, r=90):
    glow(im, lambda g: g.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(255, 210, 90, 255)), radius=30)
    d = ImageDraw.Draw(im, "RGBA")
    for k in range(12):
        a = k * math.pi / 6
        d.line([(c[0] + (r + 20) * math.cos(a), c[1] + (r + 20) * math.sin(a)),
                (c[0] + (r + 55) * math.cos(a), c[1] + (r + 55) * math.sin(a))], fill=(255, 220, 120, 255), width=10)

def moon(d, c, r=70, bg=(40, 40, 70)):
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(235, 238, 250, 255))
    d.ellipse([c[0] - r + 34, c[1] - r - 12, c[0] + r + 34, c[1] + r - 12], fill=bg + (255,))

def tank(im, box_, fuel_top, water_top, slime=True, drops=False, seed=1):
    """Cut-away steel fuel tank. fuel_top / water_top are y levels inside the tank."""
    x0, y0, x1, y1 = box_; d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(box_, radius=40, fill=(40, 48, 62, 255), outline=STEEL + (255,), width=10)
    inner = (x0 + 16, y0 + 16, x1 - 16, y1 - 16)
    d.rounded_rectangle(inner, radius=30, fill=(62, 72, 88, 255))
    # fuel (amber gradient)
    fa = vgrad([(0, AMBER), (1, AMBER_D)], h=int(water_top - fuel_top), w=int(inner[2] - inner[0]))
    fim = Image.fromarray(fa.astype(np.uint8)).convert("RGBA"); fim.putalpha(235)
    im.alpha_composite(fim, (int(inner[0]), int(fuel_top)))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([inner[0], water_top, inner[2], inner[3] - 26], fill=WATER + (255,))
    d.rounded_rectangle([inner[0], inner[3] - 60, inner[2], inner[3]], radius=30, fill=WATER + (255,))
    d.line([(inner[0], fuel_top), (inner[2], fuel_top)], fill=(255, 225, 150, 255), width=5)
    rnd = random.Random(seed)
    if slime:  # black mat at the fuel / water interface
        pts = [(inner[0], water_top - 6)]
        for x in range(int(inner[0]), int(inner[2]) + 1, 18): pts.append((x, water_top - 10 - rnd.uniform(0, 22)))
        pts += [(inner[2], water_top + 16)]
        for x in range(int(inner[2]), int(inner[0]) - 1, -18): pts.append((x, water_top + 10 + rnd.uniform(0, 16)))
        d.polygon(pts, fill=SLIME + (255,))
        for k in range(10):  # strands hanging into the water
            x = rnd.uniform(inner[0] + 30, inner[2] - 30); L = rnd.uniform(30, 80)
            d.line([(x, water_top + 10), (x + rnd.uniform(-12, 12), water_top + 10 + L)], fill=SLIME + (230,), width=7)
    if drops:  # condensation on the empty upper walls
        for k in range(26):
            x = rnd.uniform(inner[0] + 20, inner[2] - 20); y = rnd.uniform(inner[1] + 20, fuel_top - 40)
            r = rnd.uniform(7, 14)
            d.ellipse([x - r, y - r, x + r, y + r * 1.3], fill=(200, 235, 255, 230), outline=WHITE + (255,), width=2)
        for k in range(5):  # falling drops
            x = rnd.uniform(inner[0] + 60, inner[2] - 60); y = rnd.uniform(fuel_top + 30, water_top - 50)
            d.polygon([(x, y - 22), (x - 11, y + 4), (x + 11, y + 4)], fill=(170, 220, 255, 240))
            d.ellipse([x - 11, y - 6, x + 11, y + 14], fill=(170, 220, 255, 240))
    # fill pipe + vent
    d.rectangle([x0 + 80, y0 - 70, x0 + 120, y0 + 10], fill=STEEL + (255,))
    d.rectangle([x1 - 110, y0 - 50, x1 - 90, y0 + 10], fill=STEEL + (255,))
    d.arc([x1 - 110, y0 - 90, x1 - 50, y0 - 30], 180, 360, fill=STEEL + (255,), width=20)
    return inner

# ---------------- 1. hook: hot sun over a cut-away tank with water + slime
im, d = heat_canvas()
sun(im, (890, 760), 50)
tank(im, (90, 740, 780, 1280), fuel_top=850, water_top=1130, slime=True, drops=False, seed=4)
save(im, "ep004-tank")

# ---------------- 2. condensation: half-empty tank, day sun (left) + night moon (right)
arr = vgrad([(0, (245, 150, 70)), (0.5, (60, 60, 110)), (1, (10, 18, 40))])
im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
# diagonal day / night split tint
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
g.polygon([(620, 0), (W, 0), (W, H), (380, H)], fill=(20, 30, 80, 150)); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)))
sun(im, (190, 400), 70)
d = ImageDraw.Draw(im, "RGBA"); moon(d, (880, 390), 60, bg=(58, 58, 118))
for (sx, sy) in ((770, 300), (960, 260), (820, 470), (990, 480)):
    d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(255, 255, 255, 230))
tank(im, (130, 690, 950, 1290), fuel_top=1010, water_top=1170, slime=False, drops=True, seed=9)
d = ImageDraw.Draw(im, "RGBA")
d.text((540, 1370), "HOT DAY  +  COOL NIGHT  =  DROPS", font=F(800, 34), fill=(255, 235, 200, 255), anchor="mm")
save(im, "ep004-condense")

# ---------------- 3. microscope view of the fuel / water interface
im, d = heat_canvas(top=(30, 30, 40), mid=(20, 24, 36), bot=(8, 12, 24))
C, R = (540, 960), 400
lens = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L = ImageDraw.Draw(lens)
fa = vgrad([(0, (240, 185, 80)), (0.52, (200, 130, 40)), (0.53, (40, 36, 26)), (0.6, (40, 36, 26)), (0.61, (90, 170, 220)), (1, (40, 100, 160))], h=2 * R, w=2 * R)
view = Image.fromarray(fa.astype(np.uint8)).convert("RGBA"); V = ImageDraw.Draw(view)
rnd = random.Random(11)
iy = int(0.56 * 2 * R)  # interface row inside the lens
for k in range(55):  # rod bacteria
    x = rnd.uniform(40, 2 * R - 40); y = iy + rnd.gauss(0, 55); a = rnd.uniform(0, math.pi); l = rnd.uniform(18, 34)
    V.line([(x - l * math.cos(a), y - l * math.sin(a)), (x + l * math.cos(a), y + l * math.sin(a))], fill=(120, 200, 90, 255), width=16)
for k in range(22):  # yeast / mould blobs
    x = rnd.uniform(60, 2 * R - 60); y = iy + rnd.gauss(-10, 70); r = rnd.uniform(14, 26)
    V.ellipse([x - r, y - r, x + r, y + r], fill=(210, 170, 230, 255), outline=(120, 70, 150, 255), width=4)
    V.ellipse([x + r * 0.6, y - r * 0.9, x + r * 1.3, y - r * 0.2], fill=(210, 170, 230, 255))
for k in range(18):  # fungal threads
    x = rnd.uniform(40, 2 * R - 40); y = iy + rnd.gauss(0, 40); pts = [(x, y)]
    for j in range(8): x += rnd.uniform(10, 26); y += rnd.uniform(-16, 16); pts.append((x, y))
    V.line(pts, fill=(240, 240, 220, 200), width=5)
mask = Image.new("L", (2 * R, 2 * R), 0); ImageDraw.Draw(mask).ellipse([0, 0, 2 * R, 2 * R], fill=255)
lens.paste(view, (C[0] - R, C[1] - R), mask); im.alpha_composite(lens)
d = ImageDraw.Draw(im, "RGBA")
d.ellipse([C[0] - R, C[1] - R, C[0] + R, C[1] + R], outline=(210, 216, 226, 255), width=26)
d.ellipse([C[0] - R - 20, C[1] - R - 20, C[0] + R + 20, C[1] + R + 20], outline=(90, 98, 112, 255), width=10)
d.text((C[0], C[1] - 250), "DIESEL", font=F(800, 40), fill=(90, 50, 10, 255), anchor="mm")
d.text((C[0], C[1] + 290), "WATER", font=F(800, 40), fill=WHITE + (255,), anchor="mm")
save(im, "ep004-microbes")

# ---------------- 4. fuel filter / water separator with a clear bowl
im, d = heat_canvas(top=(70, 76, 88), mid=(44, 50, 62), bot=(14, 18, 30))
d = ImageDraw.Draw(im, "RGBA")
d.rounded_rectangle([300, 640, 780, 740], radius=20, fill=(150, 30, 34, 255), outline=WHITE + (200,), width=4)   # head
pipe(d, [(60, 690), (300, 690)], AMBER, width=26); pipe(d, [(780, 690), (1020, 690)], AMBER, width=26)
d.rounded_rectangle([350, 740, 730, 1010], radius=30, fill=(170, 40, 44, 255), outline=WHITE + (200,), width=4)   # element can
for yy in range(780, 990, 36): d.line([(380, yy), (700, yy)], fill=(130, 26, 30, 255), width=6)
bowl = (380, 1010, 700, 1300)
d.rounded_rectangle(bowl, radius=60, fill=(225, 235, 245, 90), outline=WHITE + (255,), width=6)
d.rounded_rectangle([392, 1020, 688, 1150], radius=20, fill=AMBER + (210,))
d.rounded_rectangle([392, 1150, 688, 1288], radius=50, fill=WATER + (235,))
rnd = random.Random(5)
pts = [(392, 1150)] + [(x, 1140 - rnd.uniform(0, 16)) for x in range(400, 690, 16)] + [(688, 1165)] + [(x, 1168 + rnd.uniform(0, 14)) for x in range(680, 392, -16)]
d.polygon(pts, fill=SLIME + (255,))
for k in range(12):
    x = rnd.uniform(420, 660); y = rnd.uniform(1200, 1270); r = rnd.uniform(5, 11)
    d.ellipse([x - r, y - r, x + r, y + r], fill=SLIME + (200,))
d.rounded_rectangle([515, 1300, 565, 1350], radius=8, fill=STEEL + (255,)); d.rectangle([470, 1318, 610, 1332], fill=STEEL + (255,))
d.line([(420, 1040), (430, 1270)], fill=(255, 255, 255, 120), width=8)   # glass highlight
save(im, "ep004-filter")

# ---------------- 5. fuel polishing loop
im, d = heat_canvas(top=(20, 60, 70), mid=(12, 40, 60), bot=(6, 16, 34))
for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(120, 220, 220, 22), width=1)
for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(120, 220, 220, 22), width=1)
inner = tank(im, (90, 900, 560, 1290), fuel_top=960, water_top=1200, slime=True, seed=2)
d = ImageDraw.Draw(im, "RGBA")
dirty = (150, 110, 60)
glow(im, lambda g: g.line([(200, 1180), (200, 820), (700, 820)], fill=dirty + (255,), width=22, joint="curve"), radius=8)
glow(im, lambda g: g.line([(880, 1060), (880, 1180), (620, 1180), (620, 1000), (470, 1000)], fill=AMBER + (255,), width=22, joint="curve"), radius=10)
d = ImageDraw.Draw(im, "RGBA")
pipe(d, [(200, 1180), (200, 820), (700, 820)], dirty, width=22)
pipe(d, [(880, 1060), (880, 1180), (620, 1180), (620, 1000), (470, 1000)], AMBER, width=22)
d.ellipse([640, 770, 740, 870], fill=CORAL + (255,), outline=WHITE + (255,), width=5)     # pump
for k in range(4):
    a = k * math.pi / 2 + 0.4; d.line([(690, 820), (690 + 32 * math.cos(a), 820 + 32 * math.sin(a))], fill=WHITE + (255,), width=6)
pipe(d, [(740, 820), (820, 820)], dirty, width=22, flow=False)
d.rounded_rectangle([810, 760, 950, 1070], radius=30, fill=(40, 70, 110, 255), outline=GOLD_L + (255,), width=5)  # filter/separator
for yy in range(790, 1000, 26): d.line([(830, yy), (930, yy)], fill=TURQ + (200,), width=5)
d.rounded_rectangle([830, 1000, 930, 1055], radius=18, fill=WATER + (255,))
save(im, "ep004-polish")

# ---------------- 6. calm CTA background
bg, _ = heat_canvas(top=(40, 30, 30), mid=(24, 24, 40), bot=(8, 12, 28))
save(Image.blend(bg, Image.open("assets/photos/ep004-filter.jpg").convert("RGBA"), 0.3), "ep004-cta")
print("ok")
