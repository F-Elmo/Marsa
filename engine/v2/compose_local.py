"""ffmpeg-only composer (fallback when vidIQ compose has no credits). Run on any box with open internet:
  python3 compose_local.py plan.json out.mp4
plan.json: {"scenes":[{"src","dur","start"}], "fade":0.25, "voice":url, "music":url, "music_vol":0.14,
            "logo":{"src","x","y","w","h"}, "ovl_base":url_prefix, "manifest":url}"""
import json, os, subprocess, sys, urllib.request
W, H, FPS = 1080, 1920, 30
def sh(c): print("+", c[:160]); subprocess.run(c, shell=True, check=True)
def get(url, out):
    if not os.path.exists(out):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        open(out, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    return out

def main(plan, out, step="all"):
    P = json.load(open(plan)); os.makedirs("seg", exist_ok=True); F = P["fade"]
    sc = P["scenes"]
    if step in ("all", "segs"):
        for i, s in enumerate(sc):
            src = get(s["src"], f"seg/src{i}.mp4"); d = s["dur"] + (F if i < len(sc) - 1 else 0)
            o = f"seg/s{i:02d}.mp4"
            if os.path.exists(o): continue
            sh(f'ffmpeg -y -loglevel error -ss {s.get("start",0)} -i {src} -t {d:.3f} -an -vf "scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p" -c:v libx264 -preset veryfast -crf 18 {o}')
    if step in ("all", "join"):
        # low-memory join: body pieces + short crossfade pieces, then concat (stream copy)
        T = 0.2; fr = lambda x: int(round(x * FPS)); parts = []
        enc = "-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -r 30"
        for i, s in enumerate(sc):
            a = 0 if i == 0 else fr(T); b = fr(s["dur"])
            o = f"seg/b{i:02d}.mp4"; parts.append(o)
            sh(f'ffmpeg -y -loglevel error -i seg/s{i:02d}.mp4 -vf "trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS" {enc} {o}')
            if i < len(sc) - 1:
                o = f"seg/t{i:02d}.mp4"; parts.append(o)
                sh(f'ffmpeg -y -loglevel error -i seg/s{i:02d}.mp4 -i seg/s{i+1:02d}.mp4 -filter_complex "[0:v]trim=start_frame={b}:end_frame={b+fr(T)},setpts=PTS-STARTPTS[a];[1:v]trim=end_frame={fr(T)},setpts=PTS-STARTPTS[b];[a][b]blend=all_expr='A*(1-N/{fr(T)-1})+B*(N/{fr(T)-1})',format=yuv420p[v]" -map "[v]" {enc} {o}')
        open("seg/list.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
        sh("cd seg && ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy joined.mp4")
    if step in ("all", "final"):
        man = json.loads(urllib.request.urlopen(P["manifest"]).read()); os.makedirs("ovl", exist_ok=True)
        for o in man: get(P["ovl_base"] + o["file"], "ovl/" + o["file"])
        L = P["logo"]; get(L["src"], "ovl/logo.png"); get(P["voice"], "seg/voice.mp3"); get(P["music"], "seg/music.wav")
        total = sum(s["dur"] for s in sc)
        ins = "-i seg/joined.mp4 -i seg/voice.mp3 -stream_loop -1 -i seg/music.wav -i ovl/logo.png " + " ".join(f"-i ovl/{o['file']}" for o in man)
        fc = [f"[3:v]scale={L['w']}:{L['h']}[lg]", f"[0:v][lg]overlay={L['x']}:{L['y']}[v0]"]
        for k, o in enumerate(man):
            st, en = o["start"], o["end"]; fi = min(0.12, (en - st) / 3)
            fc.append(f"[{k+4}:v]format=rgba,fade=t=in:st={st}:d={fi}:alpha=1,fade=t=out:st={en-fi:.3f}:d={fi}:alpha=1[o{k}]") if o["file"] in ("hook.png", "end.png") else fc.append(f"[{k+4}:v]format=rgba[o{k}]")
            fc.append(f"[v{k}][o{k}]overlay={o['x']}:{o['y']}:enable='between(t,{st},{en})'[v{k+1}]")
        vlast = f"[v{len(man)}]"
        fc.append(f"[2:a]volume={P['music_vol']},afade=t=out:st={total-1.5}:d=1.5[m]")
        fc.append(f"[1:a]volume=1.0[vo]")
        fc.append(f"[vo][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        open("seg/fc.txt", "w").write(";".join(fc))
        sh(f'ffmpeg -y -loglevel error {ins} -filter_complex_script seg/fc.txt -map "{vlast}" -map "[a]" -t {total} -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart {out}')

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "all")
