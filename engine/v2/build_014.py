"""Compose plan for episode 014 (hard vs ablative antifouling). Caption timing from ffmpeg silencedetect on the
voiceover (speech segments below), words inside a segment timed by character count."""
import json, sys
SEG = [  # (start, end, text) - speech segments between detected pauses
 (0.00, 1.86, "Two boats, same marina."), (2.53, 4.70, "A year later,|one hull is clean,"),
 (5.10, 6.79, "and the other|is covered in barnacles."), (7.35, 9.54, "The difference? / The antifouling."),
 (10.26, 13.23, "Antifouling is|the special paint|below the waterline."), (13.83, 17.18, "It slowly releases|a biocide, / usually copper,"), (17.62, 19.91, "that stops weed and|barnacles from settling."),
 (20.57, 22.76, "Ablative paint works|like a bar of soap."), (23.46, 24.88, "As water flows past,"),
 (25.18, 27.07, "the surface|slowly wears away,"), (27.46, 29.18, "exposing fresh biocide."), (29.76, 30.44, "No build-up,"),
 (30.93, 33.06, "and it keeps working|after time|out of the water."), (33.76, 35.24, "Hard paint stays put."),
 (35.82, 37.46, "It dries to a tough film"), (37.62, 39.50, "that leaches biocide|from inside."),
 (40.03, 42.24, "You can scrub it|and polish it smooth,"), (42.47, 43.72, "so fast boats love it."),
 (44.42, 45.55, "But the layers build up,"), (45.83, 47.67, "and eventually|they must be stripped."),
 (48.31, 50.21, "So, a cruiser|that's hauled out"), (50.34, 51.49, "or dry-stored often?"), (52.04, 52.65, "Ablative."),
 (53.07, 55.79, "A fast boat, or a diver|cleans the hull often?"), (56.39, 56.86, "Hard."),
 (57.35, 58.59, "Which one|is on your boat?"), (59.09, 60.19, "Tell us in the comments,"),
 (60.56, 63.00, "and follow Creative|Tracks Marine for more.")]
caps = []
for s, e, txt in SEG:
    groups = [g.split() for g in txt.split("|")]          # "|" marks a forced caption break
    tot = sum(len(w) + 1 for g in groups for w in g if w != "/"); t = s
    for g in groups:
        d = (e - s) * sum(len(w) + 1 for w in g if w != "/") / tot
        txt2 = " ".join(g).replace(", /", " /").replace(" / ", "\n").rstrip(",.").upper()   # "/" = line break
        caps.append((round(t, 2), round(d, 2), txt2))
        t += d
# extend each caption to the next one's start (no flicker during short pauses, max +0.5 s)
out = []
for j, (t, d, x) in enumerate(caps):
    nxt = caps[j + 1][0] if j + 1 < len(caps) else 63.9
    out.append((t, round(min(nxt - t, d + 0.5), 2), x))
U = json.load(open(sys.argv[1]))           # uploaded animation URLs
PX = "https://videos.pexels.com/video-files/"
SC = [  # (source, duration, startFrom)
 (PX + "36222111/15361152_1440_2560_60fps.mp4", 2.5, 1), (PX + "10703906/10703906-hd_1080_1920_30fps.mp4", 2.5, 0),
 (PX + "33873175/14375401_1440_2560_60fps.mp4", 2.3, 3), (PX + "36507896/15480433_1440_2560_30fps.mp4", 2.9, 1),
 (PX + "38942633/16564275_1440_2560_30fps.mp4", 6.1, 0), (U["intro"], 4.1, 0), (U["ablative"], 9.4, 0),
 (PX + "38359735/16289197_1440_2560_30fps.mp4", 3.8, 1), (U["hard"], 8.8, 0),
 (PX + "32077428/13673742_1080_1920_60fps.mp4", 2.0, 2), (U["buildup"], 3.9, 0),
 (PX + "28852955/12495916_1440_2560_30fps.mp4", 4.5, 2), (PX + "13915515/13915515-uhd_1440_2560_30fps.mp4", 4.5, 1),
 (PX + "12554795/12554795-uhd_1440_2560_60fps.mp4", 6.7, 2)]
scenes = []
for i, (src, d, sf) in enumerate(SC):
    sc = {"source": src, "duration": d, "type": "video"}
    if sf: sc["startFromSeconds"] = sf
    if i: sc["transitionIn"] = {"kind": "fade", "duration": 0.2}
    scenes.append(sc)
TOTAL = round(sum(s["duration"] for s in scenes), 2)
CAP = {"fontSize": 54, "lineHeight": 1.05, "fontWeight": 900, "color": "#FFFFFF", "strokeWidth": 7, "strokeColor": "#000000", "textAlign": "center"}
ov = [{"kind": "image", "src": "https://raw.githubusercontent.com/F-Elmo/Marsa/ctm-reels/media/013/logo_badge.png", "start": 0,
       "duration": TOTAL, "position": {"x": 0.33, "y": 0.045, "width": 0.34, "height": 0.083}},
      {"kind": "text", "text": "HARD vs ABLATIVE\nANTIFOULING", "start": 0.2, "duration": 6.6,
       "position": {"x": 0.05, "y": 0.2, "width": 0.9, "height": 0.16},
       "style": {"fontSize": 82, "fontWeight": 900, "color": "#FFFFFF", "strokeWidth": 6, "strokeColor": "#09183A", "textAlign": "center", "lineHeight": 1.1}},
      {"kind": "text", "text": "FOLLOW FOR A NEW\nBOAT EXPLAINER EVERY 2 DAYS", "start": 60.3, "duration": round(TOTAL - 60.3, 2),
       "position": {"x": 0.06, "y": 0.22, "width": 0.88, "height": 0.14},
       "style": {"fontSize": 64, "fontWeight": 900, "color": "#ECC878", "strokeWidth": 6, "strokeColor": "#09183A", "textAlign": "center", "lineHeight": 1.1}}]
for t, d, x in out:
    ov.append({"kind": "text", "text": x, "start": t, "duration": d, "position": {"x": 0.05, "y": 0.755, "width": 0.9, "height": 0.075}, "style": CAP})
print("scenes", len(scenes), "total", TOTAL, "captions", len(out), "overlays", len(ov), file=sys.stderr)
print("longest caption", max(len(x) for _, _, x in out), max(out, key=lambda c: len(c[2]))[2], file=sys.stderr)
json.dump({"scenes": scenes, "overlays": ov, "captions": out}, open(sys.argv[2], "w"), indent=1)
