"""Grade real photos for episode 010 (pre-departure checklist) into 1080x1920 library shots.
Sources were downloaded by the fetch-media GitHub Action into fetch/raw/ (see fetch/requests.json).
Run from repo root: python3 episodes/art/009_photos.py
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


save(band("pd-hurg44.jpg", yc=960, width=1900, fx=0.78), "ep010-hook")                   # boat on turquoise Red Sea (CC BY Tanya Dedyukhina)
save(band("pd-jeddah-sea.jpg", yc=960, width=1700, fx=0.5), "ep010-weather", col=1.1)     # stormy Red Sea, Jeddah (CC BY Ahmed Abdulbasit)
save(band("pd-hurg18.jpg", yc=960, width=2000, fx=0.58), "ep010-reefs")                   # boats + reef patches (CC BY Tanya Dedyukhina)
save(cover("pd-cleat.jpg", fx=0.45, fy=0.55, zoom=1.0), "ep010-cleat")                    # dock line on cleat (CC BY Shixart1985)
save(cover("pd-fuel.jpg", fx=0.6, fy=0.55, zoom=1.0), "ep010-fuel")                      # fuel pump on dock (CC BY Tony Webster)
save(cover("pd-lifejackets-ferry.jpg", fx=0.5, fy=0.5, zoom=1.0), "ep010-lifejackets")    # life jackets stowed (CC0 Michelle Frechette)
save(band("pd-lifejackets-cg.jpg", yc=960, width=1700, fx=0.55), "ep010-rescue")          # life-jacket demo (CC BY Coast Guard News)
save(band("pd-vhf.jpg", yc=960, width=1500, fx=0.5), "ep010-vhf")                         # marine VHF radio (CC BY PaterMcFly)
save(cover("pd-extinguisher.jpg", fx=0.5, fy=0.5, zoom=1.0), "ep010-extinguisher")        # fire extinguisher (CC0 ProjectManhattan)
save(band("pd-water.jpg", yc=960, width=1500, fx=0.5), "ep010-water")                     # water bottle (CC0 Steve Johnson)
cta = band("pd-hurg7.jpg", yc=960, width=1600).filter(ImageFilter.GaussianBlur(10))
save(ImageEnhance.Brightness(cta).enhance(0.7), "ep010-cta")                              # blurred open Red Sea (CC BY Tanya Dedyukhina)
