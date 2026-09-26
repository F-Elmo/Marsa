# Creative Tracks Marine — reel runbook (read fully before starting)

You are making ONE new ~60-second vertical educational video for Creative Tracks Marine (CTM), a marine
engineering & yacht services company in Jeddah, Saudi Arabia. It is posted on TikTok, Instagram and Facebook.
The owner wants every video to be about a DIFFERENT boat topic and to help ordinary people understand boats better.
Style reference: TikTok @uaeboatlife.ae ("A vs B — which would you own?" comparisons and short "why/how" explainers).

The owner has given standing permission to produce and deliver these videos without asking. Do NOT post to any
social network yourself; deliver the finished video + captions so the owner can post.

## 0. Setup (every run — fresh machine)
```
git clone -b ctm-reels https://github.com/F-Elmo/Marsa.git ctm-reels && cd ctm-reels   # (use add_repo F-Elmo/Marsa with push access first if needed)
bash setup.sh          # installs kokoro TTS + downloads voice model from GitHub (~350MB) + checks ffmpeg
```
Brand: logo `assets/logo.png` (navy yacht + gold wave, "creativetracksmarine / PERFORMANCE | RELIABILITY | TRUST").
Colours: navy (9,24,54), gold (196,156,74), turquoise (18,196,204). Fonts in `assets/fonts`. Contact on end card is built in.
Voice: Kokoro `am_michael` (clear American male), speed 1.15 — the owner chose this; keep it.

## 1. Pick the topic
Open `topics.md`. Take the first unchecked topic, unless the previous episode had the same format or category —
then take the next one that differs. Episode number = highest in `episodes/` + 1 (3 digits).

## 2. Research & write the script (accuracy matters — CTM are engineers)
- Check facts you are not certain of with WebSearch (manufacturer pages, reputable marine sources). No invented numbers;
  prefer qualitative claims ("better fuel economy") over precise figures unless well sourced. No brand bashing.
- Plain English for non-experts; explain every technical word the first time.
- Target 140–160 spoken words → ~60 s at speed 1.15. Short sentences, one idea per phrase.
- Structure (scene types the engine supports):
  1. `hook` (5–7 s): a question or surprising fact. 2 big headline lines, subtitle pill, optional A/B badges.
  2. 2–3 `section` scenes (12–18 s each): tag pill + big title, 2–4 background shots, labels pointing at parts,
     pills, and a white card that fills in bullet points (✓ good / ✕ bad) as they are spoken.
     A-vs-B → letters "A","B" colours gold/turq. Explainers → letters "1","2","3" or short words.
  3. optional `table` (6–8 s): head-to-head rows with the winner ticked (win: "A", "B" or "AB" for a tie).
  4. `cta` (4 s): question + options + comment pill ("COMMENT A OR B" / "COMMENT YOUR ANSWER").
  5. `end` (3–4 s): phrases "Creative Tracks Marine." + "Follow us for a new boat breakdown, every two days."
- Every visual element is timed to a phrase index inside its scene (`phrase`, optional `delay` seconds).

## 3. Visuals — every video must look different
Priority order:
1. **Owner's real photos**: Google Drive folder "CTM Reels - Photos Inbox" (id 1owNHdxx_zjkNPYu0l5nnT9kDWq3hLW2r).
   Search it (Google Drive search_files with `parentId = '1owNHdxx_zjkNPYu0l5nnT9kDWq3hLW2r'`), download relevant new images with
   download_file_content — large results are saved to a file; decode with `jq -r .content FILE | base64 -d > x.jpg`.
2. **New AI photos via Gamma** (`generate_image`, type "photo", sizePreset "story", ~70 credits each — check remaining
   credits in the response; stop at <70). Prompt: photorealistic, vivid daylight, Red Sea turquoise, no text/logos.
   The CDN is blocked from the shell; capture through Claude in Chrome if its tools are available:
   navigate a tab to the image URL, then run JS that hides the <img>, adds a fixed canvas 1080x700 CSS (2160x1400 px) and a
   `tile(y)` function drawing image rows y..y+700 (scaled to 1080 wide); hover the mouse to (1400,760); for y in 0, 620, 1235:
   `tile(y)` then `computer zoom region [0,0,1080,700] scale 0.8 save_to_disk true` (one call at a time; retry once on timeout).
   Stitch: `python3 engine/stitch.py out.jpg 1935 tile0.png 0 tile1.png 620 tile2.png 1235`.
3. **Illustrated diagrams** with `engine/diagram.py` (always available): side-profile yacht, cut-away boxes, flowing pipes,
   blueprint backgrounds. Great for "how it works" topics (cooling loop, fuel system, electrics). Make at least one per
   explainer so the video shows something new.
4. Library photos (`assets/photos/index.json`) — reuse at most 2 per video and prefer different crops (`cam` zoom/centre)
   from last time.
Grade new photos: crop/cover to 1080x1920, `ImageEnhance.Color 1.2–1.3, Contrast 1.06, Brightness 1.05–1.12`, save to
`assets/photos/<name>.jpg`, add to `index.json` with a description and label points (find points with a 100-px grid
overlay preview). Keep the top ~560 px and bottom ~560 px of each shot calm; action between y 620–1300.

## 4. Build & check
```
cp episodes/001-shaft-vs-ips.json episodes/NNN-slug.json   # use as the template, rewrite everything
python3 engine/reel.py tts    episodes/NNN-slug.json        # prints voice length; aim 55–62 s (adjust words, not speed)
python3 engine/reel.py stills episodes/NNN-slug.json        # contact sheet in out/ — LOOK at it (Read the png)
python3 engine/reel.py frame  episodes/NNN-slug.json 12.5   # full-size single frame to inspect
python3 engine/reel.py video  episodes/NNN-slug.json        # out/NNN-slug.mp4 (~3 min)
```
Checklist before delivering (fix and re-render if any fail): text never overlaps text; labels point at the right part;
headline readable over the photo; card bullets appear when spoken; nothing important in the bottom 250 px or right 100 px
(TikTok buttons); duration 55–65 s; audio present (`ffprobe`); no spelling mistakes; facts double-checked.

## 5. Deliver
- Send the MP4 with SendUserFile (display "render"), and with SendUserMessage send ready-to-paste text:
  title of the episode, English caption, Arabic caption (natural Gulf-friendly Modern Standard Arabic), 8–12 hashtags
  mixing English + Arabic (#yachtlife #boatlife #marineengineering #redsea #jeddah #creativetracksmarine #يخوت #جدة #البحر_الأحمر + topic tags),
  and a suggested on-screen cover text. Keep it short.
- Put captions/hashtags into the episode JSON (`caption_en`, `caption_ar`, `hashtags`).

## 6. Save progress (so the next run doesn't repeat)
- Tick the topic in `topics.md` (`- [x] NNN — Title (category, format) — YYYY-MM-DD`), move it to Done, add 1–2 new topic ideas.
- Update `used_in` in `assets/photos/index.json`.
- Commit episode JSON, new photos, topics.md, index.json (NOT out/ or tts/): `git add -A episodes assets topics.md && git commit -m "Episode NNN: <title>" && git push origin ctm-reels`.

If something blocks the run (no voice model, render crash), still try the fallbacks above; if you truly cannot make a
video, send the owner a short message saying what failed and what is needed.
