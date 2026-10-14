# Creative Tracks Marine — reel runbook

> **USE PIPELINE v2 (below) FOR EVERY NEW EPISODE.** The owner rejected the old v1 look (still photos + Ken Burns +
> robotic TTS) on 2026-10-14 as "very poor". v1 (engine/reel.py, Kokoro) is kept only as a fallback if vidIQ is unavailable.
> Never repeat a topic or reuse the same footage/animation as an earlier episode. Reference: episodes/013-bilge-pump.json.

## Pipeline v2 — real HD footage + animated diagram + pro voice (vidIQ)
Budget: vidIQ plan has 150 credits/month (renews on the 7th). Per video: voice ~14, compose ~15, b-roll ~6,
thumbnail QC 2. REUSE the music track (below) instead of generating new music (25 credits) unless credits > 100.
Check `vidiq_balance` first; if < 40 credits, make the video with v1 and tell the owner credits ran out.

1. **Topic & script** (see sections 1–2 of v1 below for topic rules and fact-checking). 140–155 words, ~58 s.
   Hook in the first sentence = a question or surprising claim. End with a question for comments + "follow Creative Tracks Marine".
   Hook title on screen: max ~28 characters per line, 2 lines (avoid single orphan words).
2. **Voice:** `vidiq_voiceover_generate` voice "Brian" `nPczCjzI2devNBz1zQrb` (owner wants a clear male English voice).
   Note returned duration. Caption timing: split by paragraph; estimate per-word time = (duration − pauses)/words.
3. **Footage:** `vidiq_generate_broll` for 6–8 shots (yachts, marina, engine room, water, mechanic…). Its links are 360p:
   open each Pexels page in Claude in Chrome and regex the HTML for `videos.pexels.com/video-files/<id>/..._1080_19..mp4`
   (or 2160/1440 portrait). Credit photographers in the episode JSON.
4. **Animated diagram (the explanation, 15–25 s):** write a PIL script that renders 1080x1920 30fps MP4s showing the
   mechanism moving (see engine/v2/bilge_anim.py: hull cross-section, rising water, flow dashes, labels, PASS/FAIL states,
   checklist card). Brand colours navy (9,24,54), gold (196,156,74), turquoise (18,196,204). Encode with ffmpeg libx264.
   Push to `media/NNN/` on this branch, then import each raw.githubusercontent.com URL with `vidiq_video_upload`.
   Logo badge: media/013/logo_badge.png (reuse).
5. **Compose:** `vidiq_compose` 1080x1920: scenes = footage + animations cut to the script; music
   https://ai-music-tracks.s3.us-east-1.amazonaws.com/5a296911-89e4-4313-9b4a-f1a47c445d03/3600b9e8-a118-4428-8d9a-893ad6316687.wav
   ducked under voice; overlays: logo badge whole video (top), hook title 0.2–~6.5 s, word-group captions (≤5 words,
   ≤45 overlays, y≈0.75), end text "FOLLOW FOR A NEW BOAT EXPLAINER EVERY 2 DAYS". Max 50 scenes / 50 overlays. See engine/v2/build.py.
6. **QC:** `vidiq_edit_media extract_thumbnail` at ~4 timestamps (hook, diagram, caption, end); view each by navigating a
   Chrome tab to the image URL and screenshotting. Check text never overlaps, labels correct, nothing in bottom 250 px.
7. **Deliver:** `vidiq_video_upload` the composed MP4 to get a durable link; send the owner the link + title + EN/AR
   captions + hashtags + cover text (SendUserMessage). If `vidiq_instagram_connected_accounts` lists the CTM account,
   the owner has allowed publishing — publish with `vidiq_instagram_publish_reel`; otherwise just deliver.
8. **Save:** episodes/NNN-slug.json (script, shots, captions, compose plan, caption_en/ar, hashtags), tick topics.md,
   commit + push to `ctm-reels` (never touch other branches of this repo).

---
# Pipeline v1 (fallback only)

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
Voice: Kokoro `am_michael` (clear American male), speed **1.0** — the owner asked (ep 009) for a clearer voice: do NOT speed it up; trim words instead.

## 1. Pick the topic
Open `topics.md`. Take the first unchecked topic, unless the previous episode had the same format or category —
then take the next one that differs. Episode number = highest in `episodes/` + 1 (3 digits).

## 2. Research & write the script (accuracy matters — CTM are engineers)
- Check facts you are not certain of with WebSearch (manufacturer pages, reputable marine sources). No invented numbers;
  prefer qualitative claims ("better fuel economy") over precise figures unless well sourced. No brand bashing.
- Plain English for non-experts; explain every technical word the first time.
- Target 130–145 spoken words → ~60 s at speed 1.0. Short sentences, one idea per phrase.
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
**Owner request (ep 009): the video must look REAL — use real photos for most shots.** Illustrated diagrams only as a
last resort for one "how it works" shot, never as the main look.

Real-photo pipeline (works from the sandbox even though image CDNs are blocked):
- Search free photos with Openverse via Composio remote bash (it has open internet):
  `curl -s "https://api.openverse.org/v1/images/?q=QUERY&license=cc0,pdm,by&page_size=20&size=large"` (prefer cc0/pdm;
  `by` is fine but credit the author in the caption and `photo_credits`).
- Write the wanted URLs to `fetch/requests.json` (`[{"name": "x.jpg", "url": "..."}]`; for Wikimedia use the
  `/thumb/.../1920px-NAME` URL), commit + push to ctm-reels. The GitHub Action `fetch-media` downloads them into
  `fetch/raw/` and commits back within ~1 min: `sleep 60; git pull --rebase`. Check `fetch/log.txt`.
- Grade with a script like `episodes/art/009_photos.py` (`cover` for portrait, `band` = big landscape strip over a blurred copy).
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
