import json
paras = [
 "There's one pump on your boat that decides if it's still floating tomorrow. And most owners never check it.",
 "It's the bilge pump. The bilge is the lowest part of the hull. Any water that gets in, from rain, a dripping shaft seal, or a loose hose, ends up there.",
 "Down in the bilge sits an electric pump with a float switch. As the water rises, the float lifts, the pump switches on, and pushes the water overboard.",
 "But here's the problem. If the float jams with oil and dirt, or the battery goes flat, the pump never starts. And a boat can quietly sink, right at the dock.",
 "So make sure you have three things: a clean float switch, a backup pump mounted higher, and a high-water alarm.",
 "Once a month, lift the float by hand, and listen for the pump.",
 "When did you last test yours? Tell us in the comments, and follow Creative Tracks Marine for more."]
TOTAL = 57.97; PAUSE = 0.55
words = [p.split() for p in paras]; nw = sum(len(w) for w in words)
per = (TOTAL - PAUSE * (len(paras) - 1)) / nw
# caption chunks: split each paragraph into groups of ~3-4 words, breaking at punctuation
caps = []; t = 0.0
for pi, ws in enumerate(words):
    chunk = []
    for i, w in enumerate(ws):
        chunk.append(w)
        end = w[-1] in ",.?:" or len(chunk) >= 4
        if end or i == len(ws) - 1:
            dur = len(chunk) * per
            caps.append((round(t, 2), round(dur, 2), " ".join(chunk).rstrip(",").upper()))
            t += dur; chunk = []
    if pi < len(paras) - 1: t += PAUSE
print(len(caps), "caps; end", round(t, 2))
starts = []; t = 0
for pi, ws in enumerate(words):
    starts.append(round(t, 2)); t += len(ws) * per + PAUSE
print("para starts", starts)
json.dump(caps, open("caps.json", "w"))
