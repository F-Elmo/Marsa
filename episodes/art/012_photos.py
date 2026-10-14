"""Grade real photos for episode 012 (trim tabs explained) into 1080x1920 library shots.
Sources were downloaded by the fetch-media GitHub Action into fetch/raw/ (see fetch/requests.json).
Run from repo root: python3 episodes/art/012_photos.py
Two layouts:
  cover(src, fx, fy, zoom)      fill the 9:16 frame, focus point (fx, fy) as fractions of the source
  band(src, y_center, width)    landscape photo shown large across the middle, over a blurred, darkened copy of itself
"""
import sys; sys.path.insert(0, "engine")
from diagram import W, H, ROOT
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np, os

RAW = os.path.join(ROOT, "fetch/raw")
def grade(im, col=1.22, con=1.06, bri=1.06):
    im = ImageEnhance.Color(im).enhance(col); im = ImageEnhance.Contrast(im).enhance(con); return ImageEnhance.Brightness(im).enhance(bri)
def load(n): return Image.open(os.path.join(RAW, n)).convert("RGB")
def cover(src, fx=0.5, fy=0.5, zoom=1.0):
    im = load(src); s = max(W / im.width, H / im.height) * zoom
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(0, im.width * fx - W / 2), im.width - W); y = min(max(0, im.height * fy - H / 2), im.height - H)
    return im.crop((int(x), int(y), int(x) + W, int(y) + H))
def band(src, yc=960, width=1080, fx=0.5):
    im = load(src)
    bg = cover(src, fx, 0.5, 1.15).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    s = width / im.width; fg = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    if fg.width > W:
        x0 = int(min(max(0, fg.width * fx - W / 2), fg.width - W)); fg = fg.crop((x0, 0, x0 + W, fg.height))
    m = Image.new("L", fg.size, 255); d = ImageDraw.Draw(m); f = 40   # feather top/bottom edges
    for i in range(f): d.line([(0, i), (fg.width, i)], fill=int(255 * i / f)); d.line([(0, fg.height - 1 - i), (fg.width, fg.height - 1 - i)], fill=int(255 * i / f))
    bg.paste(fg, ((W - fg.width) // 2, int(yc - fg.height / 2)), m); return bg
def save(im, name, **g):
    grade(im, **g).save(os.path.join(ROOT, "assets/photos", name + ".jpg"), quality=90); print("saved", name)



save(band("tt-race11.jpg", yc=1000, width=1900, fx=0.6), "ep012-hook")                    # race boat skimming on plane (CC BY-SA PattayaPatrol)
save(band("tt-ib762.jpg", yc=900, width=1500, fx=0.5), "ep012-transom")                       # flat transom + sterndrive at a boat show (CC BY-SA MB-one)
save(band("tt-restinga.jpg", yc=980, width=1900, fx=0.5), "ep012-plane")                  # small boat accelerating, bow up (CC0 Wilfredor)
save(band("tt-race-blue.jpg", yc=760, width=2300, fx=0.5), "ep012-spray")                 # powerboat through chop, spray (CC BY-SA PattayaPatrol)
save(cover("tt-say.jpg", fx=0.5, fy=0.45, zoom=1.0), "ep012-helm")                           # helm console seen from the stern (CC BY-SA Matti Blume)
save(band("tt-douro2.jpg", yc=980, width=2400, fx=0.33), "ep012-cruise")                   # motor yacht cruising, wake behind (CC BY Michael Gaylard)
save(band("tt-ionian.jpg", yc=980, width=2200, fx=0.45), "ep012-wakes")                    # boats running along the coast, aerial (CC BY-SA Nathannn20)
cta = cover("tt-aonang.jpg", fx=0.5, fy=0.5, zoom=1.0)
save(cta, "ep012-aerial")                                                                  # turquoise water + boat wakes, aerial (CC0 Denys Nevozhai)
save(ImageEnhance.Brightness(cta.filter(ImageFilter.GaussianBlur(10))).enhance(0.7), "ep012-cta")
