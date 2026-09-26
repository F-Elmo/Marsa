import sys
from PIL import Image
out, total_h = sys.argv[1], int(sys.argv[2])
pairs = sys.argv[3:]
canvas = Image.new("RGB", (1080, total_h))
for i in range(0, len(pairs), 2):
    f, off = pairs[i], int(pairs[i+1])
    t = Image.open(f).convert("RGB")
    t = t.resize((1080, round(t.height * 1080 / t.width)), Image.LANCZOS)
    canvas.paste(t, (0, off))
canvas.save(out, quality=95); print(out, canvas.size)
