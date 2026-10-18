"""Render text overlays (captions, hook, end card) as cropped RGBA PNGs + manifest for the local ffmpeg composer.
Every line is measured and shrunk to fit MAXW, so nothing wraps or orphans (fix for vidIQ compose auto-wrapping)."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
FONT = "/home/claude/ctm-reels/assets/fonts/montserrat-latin-800-normal.woff"
MAXW = 960

def block(lines, size, fill, stroke, sw, lh=1.12):
    while True:
        f = ImageFont.truetype(FONT, size)
        ws = [f.getbbox(l, stroke_width=sw) for l in lines]
        if max(b[2] - b[0] for b in ws) <= MAXW or size < 30: break
        size -= 2
    asc, desc = f.getmetrics(); lh_px = int(size * lh)
    W = max(b[2] - b[0] for b in ws) + 2 * sw + 8; H = lh_px * (len(lines) - 1) + asc + desc + 2 * sw + 8
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((W / 2, sw + 4 + i * lh_px), l, font=f, fill=fill, anchor="ma", stroke_width=sw, stroke_fill=stroke)
    return im, size

def main(timing, outdir, total):
    T = json.load(open(timing)); man = []
    def add(name, im, cx, cy, st, du):
        im.save(f"{outdir}/{name}.png"); man.append({"file": f"{name}.png", "x": int(cx - im.width / 2), "y": int(cy - im.height / 2), "start": st, "end": round(st + du, 2)})
    im, s = block(["HARD VS ABLATIVE", "ANTIFOULING PAINT"], 84, (255, 255, 255), (9, 24, 58), 7); add("hook", im, 540, 520, 0.2, 6.4)
    im, s2 = block(["FOLLOW FOR A NEW", "BOAT EXPLAINER", "EVERY 2 DAYS"], 72, (236, 200, 120), (9, 24, 58), 7); add("end", im, 540, 560, 57.9, total - 57.9)
    caps = T["caps"]; sizes = []
    for i, (st, du, txt) in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else total
        du = min(round(nxt - st, 2), du + 0.6)
        im, s = block([txt], 60, (255, 255, 255), (0, 0, 0), 7); sizes.append(s)
        add(f"cap{i:02d}", im, 540, 1520, st, du)
    json.dump(man, open(f"{outdir}/manifest.json", "w"), indent=0)
    print("hook", s, "end", s2, "caption sizes", min(sizes), max(sizes), len(man))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
