"""Creative Tracks Marine - spec-driven reel engine.
Usage:
  python3 engine/reel.py tts      episodes/NNN-slug.json      # voice + timing
  python3 engine/reel.py stills   episodes/NNN-slug.json 3,10,20 # contact sheet -> out/NNN-slug_stills.png
  python3 engine/reel.py video    episodes/NNN-slug.json      # -> out/NNN-slug.mp4
Run from the repo root. See RUNBOOK.md for the spec format.
"""
import math, json, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda *p: os.path.join(ROOT, *p)
W, H, FPS = 1080, 1920, 30
NAVY = (9, 24, 54); GOLD = (196, 156, 74); GOLD_L = (236, 200, 120)
TURQ = (18, 196, 204); WHITE = (255, 255, 255); CORAL = (240, 96, 84); INK = (20, 32, 60)
COLORS = {"gold": GOLD, "turq": TURQ, "coral": CORAL, "navy": NAVY, "white": WHITE}
FG_ON = {"gold": NAVY, "turq": WHITE, "coral": WHITE, "navy": WHITE, "white": NAVY}
FONTS = {"o": "assets/fonts/oswald-latin-%d-normal.woff", "m": "assets/fonts/montserrat-latin-%d-normal.woff"}
_fc = {}
def font(k, wt, sz):
    key = (k, wt, int(sz))
    if key not in _fc: _fc[key] = ImageFont.truetype(A(FONTS[k] % wt), int(sz))
    return _fc[key]
def fit(k, wt, sz, s, maxw):
    while sz > 20 and font(k, wt, sz).getlength(s) > maxw: sz -= 2
    return font(k, wt, sz)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def back(x):
    x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ TTS
def do_tts(spec, slug):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(A("tts/kokoro-v1.0.onnx"), A("tts/voices-v1.0.bin"))
    voice = spec.get("voice", "am_michael"); speed = spec.get("speed", 1.15); SR = 24000
    def trim(a, th=0.008):
        idx = np.where(np.abs(a) > th)[0]
        return a[max(0, idx[0] - 240): idx[-1] + 960] if len(idx) else a
    track = [np.zeros(int(0.3 * SR))]; t = 0.3; timing = []
    for sc in spec["scenes"]:
        st = {"start": t, "phrases": []}
        for pi, p in enumerate(sc["phrases"]):
            a, _ = k.create(p, voice=voice, speed=speed, lang="en-us"); a = trim(a)
            st["phrases"].append({"text": p, "start": t, "end": t + len(a) / SR})
            track.append(a); t += len(a) / SR
            gap = 0.2 if pi < len(sc["phrases"]) - 1 else 0.45
            track.append(np.zeros(int(gap * SR))); t += gap
        timing.append(st)
    os.makedirs(A("out"), exist_ok=True)
    sf.write(A("out", slug + ".wav"), np.concatenate(track), SR)
    json.dump({"total": t, "scenes": timing}, open(A("out", slug + ".timing.json"), "w"), indent=1)
    print(f"voice: {t:.1f}s  ->  video ~{t + 1.0:.1f}s")

# ------------------------------------------------------------------ render helpers
UP = 1.25
_ph = {}
def photo(name):
    if name not in _ph:
        _ph[name] = Image.open(A("assets/photos", name + ".jpg")).convert("RGB").resize((int(W * UP), int(H * UP)), Image.LANCZOS)
    return _ph[name]
def camc(cx, cy, s):
    s = max(1.0, s); hw, hh = W / (2 * s), H / (2 * s)
    return clamp(cx, hw, W - hw), clamp(cy, hh, H - hh), s
def cam(name, c):
    cx, cy, s = camc(*c); hw, hh = W / (2 * s), H / (2 * s)
    box = tuple(v * UP for v in (cx - hw, cy - hh, cx + hw, cy + hh))
    return photo(name).resize((W, H), Image.BILINEAR, box=box).convert("RGBA")
def tf(p, c):
    cx, cy, s = camc(*c); return ((p[0] - cx) * s + W / 2, (p[1] - cy) * s + H / 2)
def grad_overlay(top=150, bottom=170, top_h=620, bot_h=760, col=(4, 16, 40)):
    a = np.zeros((H, W), np.uint8)
    a[:top_h] = np.linspace(top, 0, top_h).astype(np.uint8)[:, None]
    b = np.linspace(0, bottom, bot_h).astype(np.uint8)[:, None]
    a[H - bot_h:] = np.maximum(a[H - bot_h:], b)
    lay = Image.new("RGBA", (W, H), col + (0,)); lay.putalpha(Image.fromarray(a)); return lay
SCRIM = grad_overlay(); SCRIM_STRONG = grad_overlay(top=225, top_h=820, bottom=190)
def lay_draw(base, fn):
    rgb = base.convert("RGB"); fn(ImageDraw.Draw(rgb, "RGBA")); base.paste(rgb.convert("RGBA"))
def text(d, xy, s, f, fill, anchor="mm", alpha=1.0, shadow=True):
    if alpha <= 0.01: return
    if shadow:
        for dx, dy, a in ((0, 5, 90), (3, 4, 110)):
            d.text((xy[0] + dx, xy[1] + dy), s, font=f, fill=(0, 10, 30, int(a * alpha)), anchor=anchor)
    d.text(xy, s, font=f, fill=tuple(fill[:3]) + (int(255 * alpha),), anchor=anchor)
def pill(d, cx, cy, s, f, bg, fg, alpha=1.0, padx=28, h=None):
    if alpha <= 0.01: return
    tw = f.getlength(s); h = h or int(f.size * 1.7)
    cx = clamp(cx, 60 + tw / 2 + padx, 1020 - tw / 2 - padx)
    d.rounded_rectangle([cx - tw / 2 - padx, cy - h / 2, cx + tw / 2 + padx, cy + h / 2], radius=h // 2, fill=bg + (int(245 * alpha),))
    text(d, (cx, cy + 1), s, f, fg, alpha=alpha, shadow=False)
def badge(d, c, r, letter, alpha=1.0, bg=GOLD, fg=NAVY):
    if r < 4 or alpha <= 0.01: return
    a = int(255 * alpha)
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=bg + (a,), outline=WHITE + (a,), width=max(3, r // 14))
    text(d, (c[0], c[1] + r * 0.03), letter, fit("o", 700, r * 1.15, letter, r * 1.5), fg, alpha=alpha, shadow=False)
def icon(d, c, ok, alpha, r=21):
    if alpha <= 0.01: return
    a = int(255 * alpha); col = TURQ if ok else CORAL
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col + (a,))
    if ok: d.line([(c[0] - 9, c[1] + 1), (c[0] - 3, c[1] + 8), (c[0] + 10, c[1] - 8)], fill=WHITE + (a,), width=6, joint="curve")
    else:
        d.line([(c[0] - 7, c[1] - 7), (c[0] + 7, c[1] + 7)], fill=WHITE + (a,), width=6)
        d.line([(c[0] - 7, c[1] + 7), (c[0] + 7, c[1] - 7)], fill=WHITE + (a,), width=6)
LOGO = Image.open(A("assets/logo.png")).convert("RGBA")
LOGO_SM = LOGO.resize((330, int(330 * LOGO.height / LOGO.width)), Image.LANCZOS)
def logo_pill(img, alpha=1.0):
    if alpha <= 0.01: return
    lw, lh = LOGO_SM.size; x0, y0 = (W - lw) // 2, 130
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x0 - 26, y0 - 14, x0 + lw + 26, y0 + lh + 14], radius=26, fill=(255, 255, 255, int(235 * alpha)))
    lg = LOGO_SM.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * alpha)))
    lay.alpha_composite(lg, (x0, y0)); img.alpha_composite(lay)
def leader(d, p, lab_xy, label, prog):
    if prog <= 0: return
    a = ease(prog); x0, y0 = p; x1, y1 = lab_xy
    mx, my = lerp(x0, x1, a), lerp(y0, y1, a)
    d.line([(x0, y0), (mx, my)], fill=WHITE + (int(255 * a),), width=4)
    d.ellipse([x0 - 12, y0 - 12, x0 + 12, y0 + 12], outline=WHITE + (int(255 * a),), width=4)
    d.ellipse([x0 - 6, y0 - 6, x0 + 6, y0 + 6], fill=TURQ + (int(255 * a),))
    if prog > 0.45:
        pill(d, x1, y1, label, font("m", 800, 30), WHITE, NAVY, alpha=ease((prog - 0.45) / 0.55), padx=24, h=56)
def arrows(d, c_frame, t, alpha):
    if alpha <= 0.01: return
    x, y = c_frame; off = 170 + 22 * math.sin(t * 5)
    for sgn in (-1, 1):
        ax = x + sgn * off; a = int(255 * alpha)
        d.line([(ax - sgn * 70, y), (ax + sgn * 20, y)], fill=TURQ + (a,), width=14)
        d.polygon([(ax + sgn * 60, y), (ax + sgn * 10, y - 36), (ax + sgn * 10, y + 36)], fill=TURQ + (a,))

# ------------------------------------------------------------------ renderer
class Reel:
    def __init__(self, spec, slug):
        self.spec = spec; self.slug = slug
        self.tm = json.load(open(A("out", slug + ".timing.json")))
        sc = self.tm["scenes"]
        self.B = [0.0] + [s["start"] - 0.15 for s in sc[1:]] + [self.tm["total"] + 1.0]
        self.T = self.B[-1]
        self.blur = None
        self.end_bg = self.build_end_bg()
    def ph(self, si, i, delay=0.0):
        ps = self.tm["scenes"][si]["phrases"]; i = min(i, len(ps) - 1)
        return ps[i]["start"] + delay

    def shots_bg(self, si, shots, t):
        XS = 0.35; spans = []
        for k, sh in enumerate(shots):
            s0 = self.B[si] if k == 0 else self.ph(si, sh.get("phrase", 0), sh.get("offset", -0.1))
            spans.append(s0)
        spans.append(self.B[si + 1] + 0.4)
        def cam_at(k, tt):
            sh = shots[k]; c0, c1 = sh.get("cam", [[540, 960, 1.0], [540, 960, 1.12]])
            p = ease_io((tt - spans[k]) / max(0.1, spans[k + 1] - spans[k]))
            return tuple(lerp(c0[j], c1[j], p) for j in range(3))
        k = max([i for i in range(len(shots)) if spans[i] <= t] or [0])
        c = cam_at(k, t); img = cam(shots[k]["photo"], c)
        if k > 0 and t - spans[k] < XS:
            img = Image.blend(cam(shots[k - 1]["photo"], cam_at(k - 1, t)), img, ease_io((t - spans[k]) / XS))
        return img, k, c, spans[k]

    def s_hook(self, si, t):
        sc = self.spec["scenes"][si]
        img, _, c, _ = self.shots_bg(si, sc.get("shots", [{"photo": sc.get("photo", "hero"), "cam": sc.get("cam", [[540, 960, 1.0], [540, 960, 1.16]])}]), t)
        img.alpha_composite(SCRIM); logo_pill(img, ease(t / 0.4))
        lines = sc["lines"]
        def fg(d):
            for i, ln in enumerate(lines):
                a = back((t - 0.15 - i * 0.4) / 0.45)
                text(d, (W / 2, 400 + i * 150 + (1 - a) * 60), ln, fit("o", 700, 132, ln, 960), GOLD_L if i % 2 else WHITE, alpha=clamp(a))
            if sc.get("subtitle"):
                s = sc["subtitle"]; a3 = ease((t - self.ph(si, s.get("phrase", 1))) / 0.35)
                pill(d, W / 2, 1480, s["text"], fit("m", 700, 33, s["text"], 880), WHITE, NAVY, alpha=a3)
            if sc.get("badges"):
                bd = sc["badges"]; ab = back((t - self.ph(si, bd.get("phrase", 2))) / 0.4); L = bd["letters"]
                n = len(L); gap = 260 if n == 2 else 220
                for j, letter in enumerate(L):
                    x = W / 2 + (j - (n - 1) / 2) * gap; col = bd.get("colors", ["gold", "turq", "coral", "navy"])[j]
                    badge(d, (x, 1320), int(64 * clamp(ab, 0, 1.2)), letter, alpha=clamp(ab), bg=COLORS[col], fg=FG_ON[col])
                if n == 2: text(d, (W / 2, 1325), "vs", font("o", 600, 46), WHITE, alpha=clamp(ab))
        lay_draw(img, fg); return img

    def s_section(self, si, t):
        sc = self.spec["scenes"][si]; lt = t - self.B[si]
        img, k, c, s0 = self.shots_bg(si, sc["shots"], t)
        img.alpha_composite(SCRIM_STRONG); logo_pill(img)
        col = sc.get("color", "gold"); sh = sc["shots"][k]
        def fg(d):
            a = back(lt / 0.45)
            pill(d, W / 2, 330, sc["tag"], font("m", 800, 30), COLORS[col], FG_ON[col], alpha=clamp(a), padx=26, h=54)
            text(d, (W / 2, 440 + (1 - clamp(a)) * 50), sc["title"], fit("o", 700, 118, sc["title"], 960), WHITE, alpha=clamp(a))
            for lb in sh.get("labels", []):
                fp = tf(lb["pt"], c); off = lb.get("off", [0, -200])
                lw = font("m", 800, 30).getlength(lb["text"]) / 2
                st = self.ph(si, lb.get("phrase", 0), lb.get("delay", 0.3))
                leader(d, fp, (clamp(fp[0] + off[0], 84 + lw, 996 - lw), fp[1] + off[1]), lb["text"], (t - st) / 0.55)
            for pl in sh.get("pills", []):
                pc = pl.get("color", "turq")
                pill(d, pl["pos"][0], pl["pos"][1], pl["text"], fit("m", 800, 34, pl["text"], 860), COLORS[pc], FG_ON[pc],
                     alpha=clamp(back((t - s0 - pl.get("delay", 0.2)) / 0.4)))
            if sh.get("arrows"):
                arrows(d, tf(sh["arrows"], c), t, clamp(back((t - s0 - 0.2) / 0.4)))
            if sc.get("card"): self.card(d, si, sc, t)
        lay_draw(img, fg); return img

    def card(self, d, si, sc, t):
        cd = sc["card"]; items = cd["items"]; col = sc.get("color", "gold")
        times = [self.ph(si, it["phrase"], it.get("delay", 0.2)) for it in items]
        a = ease((t - times[0] + 0.15) / 0.35)
        if a <= 0: return
        hgt = 92 + 58 * len(items); y0 = cd.get("y", min(1360, 1690 - hgt)); y = y0 + (1 - a) * 50
        d.rounded_rectangle([56, y, W - 56, y + hgt], radius=30, fill=(255, 255, 255, int(240 * a)))
        d.rounded_rectangle([56, y + 20, 68, y + hgt - 20], radius=6, fill=COLORS[col] + (int(255 * a),))
        badge(d, (120, y + 50), 30, sc.get("letter", ""), alpha=a, bg=COLORS[col], fg=FG_ON[col])
        text(d, (166, y + 50), cd.get("title", sc["title"]), fit("o", 700, 44, cd.get("title", sc["title"]), 780), NAVY, anchor="lm", alpha=a, shadow=False)
        for i, (it, tt) in enumerate(zip(items, times)):
            ia = ease((t - tt) / 0.3); yy = y + 112 + i * 58; ok = it.get("ok", True)
            icon(d, (110 - (1 - ia) * 20, yy), ok, ia)
            text(d, (146 - (1 - ia) * 20, yy), it["text"], fit("m", 700, 33, it["text"], 820), INK if ok else (175, 52, 40), anchor="lm", alpha=ia, shadow=False)

    def s_table(self, si, t):
        sc = self.spec["scenes"][si]; lt = t - self.B[si]
        if self.blur is None:
            img = cam(sc.get("photo", "hero"), (540, 960, 1.1)).filter(ImageFilter.GaussianBlur(18))
            img.alpha_composite(Image.new("RGBA", (W, H), NAVY + (125,))); self.blur = img
        img = self.blur.copy(); logo_pill(img)
        cols = sc.get("cols", [{"letter": "A", "color": "gold"}, {"letter": "B", "color": "turq"}])
        X = [660, 850] if len(cols) == 2 else [600, 740, 880]
        def fg(d):
            a = back(lt / 0.4)
            text(d, (W / 2, 400), sc.get("title", "HEAD TO HEAD"), fit("o", 700, 116, sc.get("title", "HEAD TO HEAD"), 960), WHITE, alpha=clamp(a))
            for cc, x in zip(cols, X):
                badge(d, (x, 560), 48, cc["letter"], alpha=clamp(a), bg=COLORS[cc["color"]], fg=FG_ON[cc["color"]])
            rows = sc["rows"]; step = min(124, 760 / max(1, len(rows)))
            for i, r in enumerate(rows):
                st = self.ph(si, r["phrase"], r.get("delay", 0)); ra = ease((t - st) / 0.3); y = 690 + i * step
                if ra <= 0: continue
                d.rounded_rectangle([56 - (1 - ra) * 60, y - 52, 960, y + 52], radius=22, fill=(255, 255, 255, int(240 * ra)))
                text(d, (96, y), r["text"], fit("m", 800, 38, r["text"], X[0] - 150), NAVY, anchor="lm", alpha=ra, shadow=False)
                for cc, x in zip(cols, X):
                    if cc["letter"] in r["win"]:
                        pa = back((t - st - 0.15) / 0.35); rr = 32 * clamp(pa, 0, 1.25)
                        if rr > 3:
                            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=COLORS[cc["color"]] + (255,))
                            d.line([(x - 12, y + 1), (x - 3, y + 11), (x + 14, y - 10)], fill=WHITE + (int(255 * clamp(pa)),), width=7, joint="curve")
                    else:
                        d.line([(x - 15, y), (x + 15, y)], fill=(170, 180, 195, int(255 * ra)), width=5)
        lay_draw(img, fg); return img

    def s_cta(self, si, t):
        sc = self.spec["scenes"][si]; lt = t - self.B[si]; dur = self.B[si + 1] - self.B[si]
        img = cam(sc.get("photo", "hero"), (540, 960, lerp(1.14, 1.24, lt / dur)))
        img.alpha_composite(Image.new("RGBA", (W, H), NAVY + (95,))); img.alpha_composite(SCRIM); logo_pill(img)
        def fg(d):
            if sc.get("top"):
                a0 = back(lt / 0.4); text(d, (W / 2, 390), sc["top"], fit("o", 600, 66, sc["top"], 960), WHITE, alpha=clamp(a0))
            q = sc["question"]; a = back((t - self.ph(si, sc.get("question_phrase", 1))) / 0.4)
            for i, ln in enumerate(q):
                text(d, (W / 2, 530 + i * 150), ln, fit("o", 700, 140 if i == 0 else 110, ln, 960), GOLD_L if i else WHITE, alpha=clamp(a))
            opts = sc.get("options", []); yb = 530 + len(q) * 150 + 130
            ab = back((t - self.ph(si, sc.get("question_phrase", 1), 0.3)) / 0.4)
            for j, o in enumerate(opts):
                x = W / 2 + (j - (len(opts) - 1) / 2) * (380 if len(opts) == 2 else 300)
                pul = 1 + 0.07 * math.sin(lt * 7 + j * math.pi)
                badge(d, (x, yb), int((112 if len(opts) <= 2 else 90) * clamp(ab, 0, 1.2) * pul), o["letter"], alpha=clamp(ab), bg=COLORS[o.get("color", "gold")], fg=FG_ON[o.get("color", "gold")])
                text(d, (x, yb + 190), o["label"], fit("o", 700, 50, o["label"], 330), WHITE, alpha=clamp(ab))
            ca = back((t - self.ph(si, len(sc["phrases"]) - 1)) / 0.4)
            pill(d, W / 2, max(1300, yb + 330) + math.sin(lt * 5) * 5, sc.get("comment", "COMMENT BELOW"), fit("m", 800, 44, sc.get("comment", "COMMENT BELOW"), 820), GOLD, NAVY, alpha=clamp(ca), padx=46, h=92)
        lay_draw(img, fg); return img

    def build_end_bg(self):
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 800) / H) ** 2)
        k = np.clip(r / 0.8, 0, 1)[..., None]
        arr = (np.array([255, 255, 255]) * (1 - k) + np.array([226, 240, 244]) * k).astype(np.uint8)
        im = Image.fromarray(arr).convert("RGBA"); d = ImageDraw.Draw(im)
        for j in range(3):
            d.line([(x, 1560 + j * 34 + 22 * math.sin(x / 140 + j)) for x in range(0, W + 10, 10)], fill=GOLD + (255 - j * 70,), width=5 - j)
        return im

    def s_end(self, si, t):
        lt = t - self.B[si]; img = self.end_bg.copy()
        a = ease(lt / 0.6); sc_ = lerp(0.92, 1.0, back(lt / 0.7))
        lw = int(900 * sc_); lg = LOGO.resize((lw, int(lw * LOGO.height / LOGO.width)), Image.LANCZOS)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(lg, ((W - lg.width) // 2, 760 - lg.height // 2))
        def fg(d):
            a2 = ease((lt - 0.8) / 0.5)
            text(d, (W / 2, 1060), "Follow for a new boat breakdown every 2 days", font("m", 700, 32), NAVY, alpha=a2, shadow=False)
            a3 = ease((lt - 0.5) / 0.5)
            pill(d, W / 2, 1170, "info@creativetracksmarine.com", font("m", 700, 34), NAVY, WHITE, alpha=a3, padx=34, h=74)
            text(d, (W / 2, 1265), "+966 54 832 0484   ·   Jeddah, Red Sea", font("m", 600, 32), (90, 100, 120), alpha=a3, shadow=False)
        lay_draw(img, fg); return img

    def scene(self, si, t):
        ty = self.spec["scenes"][si]["type"]
        return {"hook": self.s_hook, "section": self.s_section, "table": self.s_table, "cta": self.s_cta, "end": self.s_end}[ty](si, t)

    def render(self, t):
        n = len(self.spec["scenes"])
        for i in range(n):
            if self.B[i] <= t < self.B[i + 1] or i == n - 1:
                cur = self.scene(i, t)
                if i > 0 and t - self.B[i] < 0.3:
                    cur = Image.blend(self.scene(i - 1, t), cur, ease_io((t - self.B[i]) / 0.3))
                return cur

def main():
    mode, path = sys.argv[1], sys.argv[2]
    spec = json.load(open(path)); slug = os.path.splitext(os.path.basename(path))[0]
    if mode == "tts": return do_tts(spec, slug)
    r = Reel(spec, slug)
    if mode == "stills":
        ts = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [r.T * f for f in (0.03, 0.1, 0.25, 0.4, 0.55, 0.7, 0.82, 0.9, 0.98)]
        ims = [r.render(x).convert("RGB").resize((360, 640)) for x in ts]
        sh = Image.new("RGB", (370 * len(ims), 640), "white")
        for i, im in enumerate(ims): sh.paste(im, (i * 370, 0))
        sh.save(A("out", slug + "_stills.png")); print("stills ->", A("out", slug + "_stills.png")); return
    if mode == "frame":
        r.render(float(sys.argv[3])).convert("RGB").save(A("out", slug + "_frame.png")); return
    n = int(r.T * FPS); out = A("out", slug + ".mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", A("out", slug + ".wav"), "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.5:LRA=7,apad[a]", "-map", "0:v", "-map", "[a]", "-shortest",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(r.render(i / FPS).convert("RGB").tobytes())
        if i % 300 == 0: print(f"{i}/{n}", flush=True)
    ff.stdin.close(); ff.wait(); print("video ->", out, f"{r.T:.1f}s")

if __name__ == "__main__":
    main()
