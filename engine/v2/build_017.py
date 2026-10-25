"""Ep 017 local build (vidIQ credits 1): Kokoro voice + real Pexels footage + underwater-blueprint cavitation animations, ffmpeg compose.
Run from repo root after: engine/reel.py tts episodes/017-propeller-cavitation.json ; engine/v2/cav_anim.py media/017
  python3 engine/v2/build_017.py  -> out/017-propeller-cavitation.mp4"""
import json, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
SLUG = "017-propeller-cavitation"; R = "fetch/raw/"; M = "media/017/"; WD = "out/b017/"
TOTAL = 61.5
SCENES = [  # src, source start, duration, crop centre (fraction of width, for landscape clips)
    (R + "ep017-prop-underwater.mp4", 0.6, 1.8, 0.40),
    (R + "ep017-engine-calm.mp4", 2.0, 1.8, 0.5),
    (R + "ep017-wake-dramatic.mp4", 1.0, 1.8, 0.5),
    (M + "cav_wing.mp4", 0, 6.2, 0.5),
    (M + "cav_boil.mp4", 0, 3.8, 0.5),
    (M + "cav_bubbles.mp4", 0, 4.1, 0.5),
    (M + "cav_collapse.mp4", 0, 5.1, 0.5),
    (R + "ep017-shipyard-props.mp4", 3.0, 2.2, 0.62),
    (M + "cav_pits.mp4", 0, 3.9, 0.5),
    (M + "cav_signs.mp4", 0, 5.1, 0.5),
    (M + "cav_causes.mp4", 0, 2.8, 0.5),
    (R + "ep017-prop-weeds.mp4", 1.0, 1.7, 0.40),
    (M + "cav_causes.mp4", 4.5, 1.5, 0.5),
    (R + "ep017-prop-underwater.mp4", 5.2, 1.8, 0.36),
    (M + "cav_fix.mp4", 0, 8.8, 0.5),
    (R + "ep017-speedboat-aerial.mp4", 2.5, 3.2, 0.58),
    (R + "ep017-wake-auckland.mp4", 3.0, 2.6, 0.5),
    (R + "ep017-yacht-sunset-drone.mp4", 3.0, 3.3, 0.52),
]
assert abs(sum(s[2] for s in SCENES) - TOTAL) < 0.01, sum(s[2] for s in SCENES)
FONT = "assets/fonts/montserrat-latin-800-normal.woff"
def sh(c): subprocess.run(c, shell=True, check=True)

def block(lines, size, fill, stroke, sw, maxw=960, lh=1.12):
    while True:
        f = ImageFont.truetype(FONT, size); bb = [f.getbbox(l, stroke_width=sw) for l in lines]
        if max(b[2] - b[0] for b in bb) <= maxw or size < 30: break
        size -= 2
    asc, desc = f.getmetrics(); lp = int(size * lh)
    w = max(b[2] - b[0] for b in bb) + 2 * sw + 8; h = lp * (len(lines) - 1) + asc + desc + 2 * sw + 8
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines): d.text((w / 2, sw + 4 + i * lp), l, font=f, fill=fill, anchor="ma", stroke_width=sw, stroke_fill=stroke)
    return im

def captions():
    tm = json.load(open(f"out/{SLUG}.timing.json")); caps = []
    for sc in tm["scenes"]:
        for p in sc["phrases"]:
            groups = []
            for clause in re.split(r"(?<=[.,?])\s+", p["text"]):  # never run a group across punctuation
                words = clause.split(); n = len(words); k = max(1, -(-n // 5))
                groups += [words[round(i * n / k): round((i + 1) * n / k)] for i in range(k)]
            chars = [sum(len(w) + 1 for w in g) for g in groups]; t = p["start"]; dur = p["end"] - p["start"]
            for g, c in zip(groups, chars):
                d = dur * c / sum(chars); caps.append([round(t, 2), round(d, 2), " ".join(g).upper().rstrip(".,")]); t += d
    return caps

def overlays():
    os.makedirs(WD + "ovl", exist_ok=True); man = []
    def add(name, im, cx, cy, st, en):
        im.save(f"{WD}ovl/{name}.png"); man.append({"file": f"{name}.png", "x": int(cx - im.width / 2), "y": int(cy - im.height / 2), "start": round(st, 2), "end": round(en, 2)})
    add("hook", block(["THAT PROP RUMBLE?", "IT COULD BE BOILING"], 92, (255, 255, 255), (9, 24, 58), 8), 540, 560, 0.2, 5.3)
    add("end", block(["FOLLOW FOR A NEW", "BOAT EXPLAINER", "EVERY 2 DAYS"], 76, (236, 200, 120), (9, 24, 58), 7), 540, 620, 58.3, TOTAL)
    caps = captions()
    for i, (st, du, txt) in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else TOTAL
        add(f"cap{i:02d}", block([txt], 60, (255, 255, 255), (0, 0, 0), 7), 540, 1500, st, min(nxt, st + du + 0.5))
    json.dump(man, open(WD + "ovl/manifest.json", "w"), indent=0)
    return man, caps

def segments():
    os.makedirs(WD, exist_ok=True); F = 0.2; parts = []
    for i, (src, ss, dur, cx) in enumerate(SCENES):
        d = dur + (F if i < len(SCENES) - 1 else 0); o = f"{WD}s{i:02d}.mp4"
        vf = (f"scale=-2:{H}:flags=lanczos,crop={W}:{H}:'max(0,min(iw-{W},iw*{cx}-{W}/2))':0,fps={FPS},setsar=1,format=yuv420p,"
              f"eq=saturation=1.08:contrast=1.03")
        sh(f'ffmpeg -y -loglevel error -ss {ss} -i {src} -t {d:.3f} -an -vf "{vf}" -c:v libx264 -preset veryfast -crf 17 {o}')
        parts.append(o)
    # join with 0.2 s cross-dissolves
    fc = []; cur = "[0:v]"; off = 0.0
    for i in range(1, len(parts)):
        off += SCENES[i - 1][2]; nxt = f"[x{i}]"
        fc.append(f"{cur}[{i}:v]xfade=transition=fade:duration={F}:offset={off - 0.0:.3f}{nxt}"); cur = nxt
    ins = " ".join(f"-i {p}" for p in parts)
    open(WD + "join.txt", "w").write(";".join(fc))
    sh(f'ffmpeg -y -loglevel error {ins} -filter_complex_script {WD}join.txt -map "{cur}" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p {WD}joined.mp4')

def final(man):
    ins = f"-i {WD}joined.mp4 -i out/{SLUG}.wav -i {R}ctm-music.wav -i media/013/logo_badge.png " + " ".join(f"-i {WD}ovl/{o['file']}" for o in man)
    fc = ["[3:v]scale=367:163[lg]", "[0:v][lg]overlay=356:86[v0]"]
    for k, o in enumerate(man):
        fc.append(f"[v{k}][{k + 4}:v]overlay={o['x']}:{o['y']}:enable='between(t,{o['start']},{o['end']})'[v{k + 1}]")
    fc.append(f"[2:a]aresample=48000,atrim=0:{TOTAL},volume='if(lt(t,58.0),0.13,0.34)':eval=frame,afade=t=out:st={TOTAL - 1.6}:d=1.6[m]")
    fc.append("[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[vo]")
    fc.append(f"[vo][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    open(WD + "fc.txt", "w").write(";".join(fc))
    sh(f'ffmpeg -y -loglevel error {ins} -filter_complex_script {WD}fc.txt -map "[v{len(man)}]" -map "[a]" -t {TOTAL} '
       f'-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart out/{SLUG}.mp4')

if __name__ == "__main__":
    import sys
    man, caps = overlays(); print(len(man), "overlays,", len(caps), "captions")
    if "--ovl" in sys.argv: sys.exit()
    if "--final" not in sys.argv: segments()
    final(man); print("->", f"out/{SLUG}.mp4")
