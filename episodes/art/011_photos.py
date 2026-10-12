"""Grade real photos for episode 011 (single vs twin engines) into 1080x1920 library shots.
Sources were downloaded by the fetch-media GitHub Action into fetch/raw/ (see fetch/requests.json).
Run from repo root: python3 episodes/art/011_photos.py
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



save(band("sv-brother.jpg", yc=980, width=2000, fx=0.55), "ep011-hook")                    # Red Sea dive boats at Small Brother island (CC BY-SA Alexander Vasenin)
save(band("sv-buster-f225.jpg", yc=980, width=1900, fx=0.3), "ep011-single")             # aluminium boat with one outboard at speed (CC0 Mikasarkijarvi)
save(cover("sv-yamaha-f350.jpg", fx=0.5, fy=0.52, zoom=1.0), "ep011-oneengine")            # single big outboard on display (CC BY-SA Rainmaker47)
save(band("sv-teal-single.jpg", yc=980, width=1900, fx=0.45), "ep011-light")               # small single-outboard boat (CC BY-SA PattayaPatrol)
save(band("sv-tow.jpg", yc=900, width=1700, fx=0.35), "ep011-tow")                         # lifeboat towing a boat (CC BY-SA M J Richardson)
save(band("sv-fiske-twin.jpg", yc=960, width=1080, fx=0.5), "ep011-twinprops", col=1.0)     # two propellers + two rudders in drydock (public domain, US Navy)
save(band("ob-twin-wake.jpg", yc=850, width=1500, fx=0.5), "ep011-twinwake")              # twin outboards + wake (CC0 mdburnette) - new tighter crop
save(band("sv-suzuki-boats.jpg", yc=980, width=1800, fx=0.4), "ep011-many")                # row of boats, outboards to service (CC BY-SA Wikisympathisant)
save(band("sv-helm.jpg", yc=960, width=1700, fx=0.6), "ep011-helm")                        # modern boat helm (CC BY Shixart1985)
cta = band("sv-redsea-boat.jpg", yc=960, width=1900, fx=0.55)
save(cta, "ep011-offshore")                                                                # lone boat on the open Red Sea, aerial (CC BY Yonatan Dodin)
save(ImageEnhance.Brightness(cta.filter(ImageFilter.GaussianBlur(10))).enhance(0.7), "ep011-cta")
