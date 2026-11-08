# Merit Mantra Shorts: Style Sheet (default for every edit)

**Version 1.0 · 3 Nov 2026 · Canvas 1080 × 1920, 30 fps**

This is the default for every video unless you say otherwise for a specific edit. It merges two references:

- **Ref 1** (5 shorts from *scientific dot think*: uso3Rd_wt70, 5MtDiOFXlDU, AN0ATVg_7dU, 3MVMryHQL3Y, VoxNTq8a1Xw). Use it for **content, delivery, dialogue and subtitles**.
- **Ref 2** (your channel, *Merit Mantra*: uvoOLe3m5HU, 1qBPbRJVKqs, i6FxuLpyajE, 9Akf6T3r5YQ, F3-_5JugVLA). Use it for **visuals, color, on-screen graphics and thumbnails**, so the channel stays consistent.

Every number below was measured from the downloaded files: frame sampling, pixel color sampling, Whisper word timings, Demucs voice/music separation and EBU R128 loudness. Raw data is in `reference/analysis/`. Where a value is a judgment call rather than a measurement, it says so.

---

## 0. Quick rules (read before every edit)

1. **Voice starts at 0.00–0.15 s.** No silent intro. The thumbnail card can sit under the first words, but it never delays them.
2. **Keep speech continuous: about 92% of runtime is voice.** No pause longer than 0.25 s, except one deliberate beat before the payoff (max 0.5 s).
3. **Bottom subtitles always on:** a phrase bar, 3–6 words, white on navy `#151F31`, popping on instantly.
4. **New visual every 2.5 s on average** (range 1.2–4.0 s). Use hard cuts inside a section, and a 1.0 s dissolve only when the topic changes. Never hold one image longer than 4 s without a zoom, overlay or text change.
5. **Look:** cinematic, saturated, deep-navy shadows (`#03060E`), electric blue (`#1073C7`), warm orange glow (`#EF880A`) for energy.
6. **Keyword overlays** go mid-frame, 1–4 words, in caps, every 6–10 s, with a pop sound effect.
7. **Mix:** voice on top, music 15 dB below it, final export at −14 LUFS.
8. **Length 55–70 s.** End on the 1.2–1.5 s Merit Mantra fire-seal end card.

---

## 1. Fonts

The references are burned-in video. The typefaces below are the closest **free Google Fonts** matches to the letterforms, so HyperFrames can load them. Sizes are in px on the 1080 × 1920 canvas.

| Element | Font (closest match) | Weight | Size | Color | Notes |
|---|---|---|---|---|---|
| **Subtitle bar** (Ref 1) | **Montserrat** (Ref 1 looks like Proxima Nova Semibold) | 600 | **58 px** (measured ascender height 42 px, x-height 31 px) | `#FFFFFF` | Lowercase, romanized Hinglish, no end punctuation. Letter-spacing 0. |
| **Hook title bar** (optional, Ref 1 uso3Rd_wt70) | **Libre Bodoni** (regular-contrast serif) | 400 | 64 px | `#FFFFFF` | Sentence case + one emoji, e.g. `Chip mein sona kyun? 🤔`. Shown for the whole video. |
| **Keyword overlay, wide** (Ref 2 "SAME PERSON…", "CAN THIS CHANGE WEATHER?!") | **Montserrat** | 700 | 100 px (cap height 71 px) | `#FFFFFF` | ALL CAPS. Soft shadow `0 4px 18px rgba(0,0,0,.55)`. |
| **Keyword overlay, punch** (Ref 2 "SMOKE?❌", "IT'S WATER😋") | **Oswald** | 700 | 150–190 px | `#FFFFFF` | ALL CAPS, condensed. 6 px black stroke (`paint-order: stroke`) or strong shadow, plus one emoji or a red ❌ `#FF3006`. |
| **Data label** (Ref 2 "1670 km/h at equator") | Montserrat | 700 number / 500 unit | 64 px number, 34 px unit, 22 px qualifier | `#FFFFFF` at 85% | Centered just above the subtitle bar, baseline y = 1310. Ref 2 put it at the very bottom (y ≈ 1850), but the YouTube title/channel overlay covers that area, and the subtitle bar now sits there. Number counts up over 0.6 s. |
| **Small caption tag** (Ref 2 "EQUATOR → OUTWARD PUSH", "TINY ICE CRYSTALS") | Montserrat | 600 | 30 px | `#FFFFFF` at 90% | ALL CAPS, tracking +2%, placed near the subject. |
| **Thumbnail headline** (Ref 2) | **Montserrat** (closest to the heavy rounded sans in your thumbnails) | 800 | 110–150 px | Fill `#FBE414`, stroke `#6B1000` | 8–10 px stroke, skew −6°, glow `0 0 24px rgba(239,136,10,.6)`. Some words in white `#FFFFFF`. |
| **Emoji** | Noto Color Emoji | n/a | Same as cap height × 1.2 | n/a | One per title or overlay, at the end of the line: 😱 🤔 😳 😋 ❌ |

---

## 2. Colors and grading

### Brand palette (sampled from Ref 2 frames and thumbnails)

| Token | Hex | Use |
|---|---|---|
| `--space-black` | `#03060E` | Shadows and background base (30% of pixels in 1qBPbRJVKqs) |
| `--deep-navy` | `#042147` | Mid-shadows, gradients |
| `--ocean-blue` | `#0A4282` | Dominant mid-tone in science/space visuals |
| `--electric-blue` | `#1073C7` | Glows, rim light, arrows, energy lines |
| `--sky-blue` | `#62A6E2` | Highlights in sky/air scenes |
| `--fire-orange` | `#EF880A` | Heat, motion arrows, thumbnail glow |
| `--hot-red` | `#FF3006` | ❌ marks, warnings, "danger" accents |
| `--thumb-yellow` | `#FBE414` | Thumbnail headline fill |
| `--thumb-outline` | `#6B1000` | Thumbnail headline stroke (dark oxblood) |
| `--caption-navy` | `#151F31` | Subtitle bar and title bar (Ref 1, measured, opaque) |
| `--white` | `#FFFFFF` | All on-video text |

### Grade (measured averages, Ref 2)

- **Mean luma:** 0.28–0.46 on a 0–1 scale. Moody, not bright. Target **0.33**.
- **Mean saturation:** 0.33–0.66. Target **0.45** (Ref 1 real footage is lower, 0.22–0.44).
- **Black point (5th percentile):** 0.04–0.09 in space/dark scenes. Crush to near `#03060E` with a slight blue tint.
- **White point (95th percentile):** 0.60–0.72. **Never clip highlights.** Keep peak luma ≤ 0.75 except glows.
- **Look:** teal/blue shadows, warm orange/yellow highlights, glowing rim light on subjects, soft bloom on bright edges.
- **FFmpeg starting point** for real footage or stock that needs to match:
  `eq=contrast=1.08:saturation=1.20:gamma=0.96,colorbalance=bs=0.06:bm=0.03:rh=0.04:gh=0.01`
  Check the result against `reference/analysis/1qBPbRJVKqs/sheet_1fps.jpg`.

---

## 3. Layout (how the 1080 × 1920 frame is used)

```
y=0     ┌──────────────────────────────┐
        │ [optional title bar 0–148]   │  #151F31, serif title + emoji (Ref 1)
y≈190   │                              │
        │   HERO VISUAL (full-bleed)   │  AI cinematic image/clip, subject centered
y≈440   │   keyword overlay zone       │  y 440–1000 (23–52% of height), centered
y≈1000  │                              │
        │                              │
y≈1250  │   data label zone 1250–1330  │  numbers/units, centered
y=1357  ├──────────────────────────────┤
        │ subtitle bar 1357–1443       │  full-width #151F31, 86 px (2 lines: 1357–1495)
y=1443  ├──────────────────────────────┤
        │ (YouTube UI zone, keep clear │  no text below y=1500
y=1920  └──────────────────────────────┘
```

- **Full-bleed, single subject, centered.** Ref 2 uses one hero object per shot: Earth, plane, engine, F1 car or person, filling 60–90% of the width.
- **No split screens** in either reference. The closest thing is the Ref 2 **before/after vertical divide**: a 4 px glowing seam at x = 540, with a cool left side and a warm right side. Use it only for comparisons.
- **Diagrams:** Ref 2 uses whiteboard-on-white (`#F4F4F4`) or chalkboard (`#1F4A3A`) scenes for formulas and vectors. Hand-drawn line style, black or white strokes 6–8 px.
- **B-roll:** Ref 1 is real macro and lab footage. Ref 2 is AI-generated images and clips. **Default: AI-generated cinematic visuals (Ref 2 look).** Use real footage when a real-world process is the point, color-graded per §2.
- **Zooms:** every still or AI clip gets a slow **push-in from 1.00 to 1.08 scale over the shot** (linear, or ease-in-out sine). On emphasis words, add a **punch-in from 1.00 to 1.12 over 0.20 s** with `cubic-bezier(0.2, 0.8, 0.2, 1)` and hold.
- **Logo:** the Merit Mantra seal goes **top-right on the thumbnail card only**: 150 px diameter at x 860–1010, y 80–230. It is not in the video body.
- **Safe margins:** 60 px left and right, 120 px from the right edge for anything near the YouTube buttons, nothing below y = 1500 except the data label.

---

## 4. Motion

| Item | Value | Source |
|---|---|---|
| **Hard cut (default)** | Every shot change inside a section. Hard cuts land **on the word** that names the new thing. | Ref 1 hard cuts, 1.9–3.6 s mean shot |
| **Cross-dissolve** | **Only between sections or topics** (about 5–6 per video), **1.0 s**, ease-in-out (allowed 0.8–1.2 s). A 1 s dissolve on every 2.5 s shot would blur the whole video. | Ref 2 measured median 1.0–1.4 s |
| **Morph/match dissolve** | Same subject at a new scale, e.g. Earth zoom to continent. Duration 1.2 s. | Ref 2 1qBPbRJVKqs |
| **Light-flash transition** | A horizontal blue lens streak `#1073C7` across the frame for 0.4 s, for "energy" reveals. | Ref 2 1qBPbRJVKqs at 31 s |
| **Keyword overlay in** | Fade + scale 0.85 → 1.00 over **0.25 s**, `cubic-bezier(0.34, 1.56, 0.64, 1)` (slight overshoot) | Ref 2 |
| **Keyword overlay out** | Fade 0.20 s, or a blur-dissolve with the next shot | Ref 2 |
| **Glitch/scan word** (e.g. "DIFFERENT") | 2–3 frames of RGB split ±6 px plus an icy gradient `#BFE6FF → #FFFFFF`, then settle | Ref 2 1qBPbRJVKqs at 17 s |
| **Arrows and lines** | Draw-on (stroke-dashoffset) over **0.5 s**, ease-out, electric blue or white, 8 px stroke, glowing | Ref 2 |
| **Number count-up** | 0 → value over **0.6 s**, ease-out | Ref 2 "1670 km/h" |
| **Subtitles** | **No animation.** Hard swap on the frame the phrase starts. | Ref 1 (verified frame by frame) |
| **Something changes on screen** | At least **every 1.5 s**: a new subtitle phrase, overlay, cut or punch-in | Ref 1 subtitle phrases change every 0.9–1.6 s |

---

## 5. Captions (subtitles)

Measured in Ref 1, and verified frame by frame at 10 fps.

- **Style:** full-width opaque bar, color **`#151F31`**, x 0–1080. A rounded pill with 16 px corner radius and a 24 px side margin is allowed when the phrase is short (< 22 characters).
- **Bar geometry:** the **top edge is fixed at y = 1357**, so the bar never jumps. One line is **86 px tall (y 1357–1443)**. Two lines are **138 px tall (y 1357–1495)**, with line-height **0.92** (tight). Inner padding is 19 px top, 13 px bottom and ≥ 60 px left/right. (Measured: 1 line 1357–1443 in 5MtDiOFXlDU; 2 lines 138 px in uso3Rd_wt70.)
- **Text:** Montserrat 600, 58 px, `#FFFFFF`, centered.
- **Words per caption:** **3–6** (typically 5). Max **32 characters per line**. Wrap to 2 lines only if unavoidable, and never use 3 lines.
- **Case and language:** lowercase **romanized Hinglish** exactly as spoken (`ek second mein poora purple`). Keep numbers as digits (`3300 digree selsiyas`). No full stops or commas. Keep `?` only on real questions.
- **Timing:** each caption is on screen **0.9–1.6 s** (≈ 1.5 s at 3.3 words/s). It appears at the first word's start time from Whisper and stays until the next caption replaces it, with no gap between captions.
- **Highlight words:** **none in the subtitle bar** (Ref 1 is all white). Emphasis goes in the **keyword overlay** (§1, §4), so the bar stays clean.
- **Hook title bar** (optional): if used, the whole video has a 148 px `#151F31` bar at the top with the hook question in Libre Bodoni 64 px + emoji.

---

## 6. Sound design

Measured with Demucs (voice vs. everything else) and EBU R128 loudness.

| Item | Value |
|---|---|
| **Final loudness** | **−14 LUFS integrated**, true peak **−1.0 dBTP** (Ref 1 ranged −11 to −21; YouTube plays back at −14) |
| **Voice** | Dominant. Compress 3:1, de-ess, high-pass 80 Hz. |
| **Voice actor (TTS)** | Sarvam `bulbul:v4-flash`, `hi-IN`, pace 1.2, 44100 Hz, Devanagari input. **1st `anand_hi_documentary`**, 2nd `shubh_hi_stories_dramatic`. Samples + settings in `voices\` (user choice, 2026-11-03). |
| **Music bed level** | **15 dB below the voice** (Ref 1 measured 9–18.5 dB below, median ≈ 13; Ref 2 14.5–21 dB) |
| **Music start** | **0.00 s**, under the first word. Never a music-only intro. |
| **Music build** | Raise the bed **+8 dB** over 1 s at the **mechanism/payoff turn (30–45% of runtime)**, then hold. Ref 1 VoxNTq8a1Xw rose from −37 to −27 dB at 28 s of 73 s. |
| **Music style** | Dark, warm, cinematic-tech pulse with a steady beat. **95–125 BPM** (measured 96, 117, 123). Bass-heavy: spectral centroid 550–900 Hz. Not bright, not vocal. |
| **Music end** | Ride out under the end card, 0.5 s fade. |
| **SFX density** | **About 1 per 6–10 s in total** (measured 0.5–1.7 per 10 s). Sparse, never on every cut. For a 60 s video that's 6–10 SFX: overlay pops + ≤ 3 whooshes + ≤ 2 booms. |
| **Pop / click** | When a keyword overlay or data label appears, on the same frame. Short (< 80 ms), bright (> 4 kHz), peak −14 dBFS. |
| **Whoosh** | On section-change dissolves only, max 3 per video. Starts 0.3 s before the dissolve midpoint, peak −18 dBFS. |
| **Boom / hit** | On the big reveal or payoff number. Low (< 200 Hz), peak −12 dBFS, with a 0.1 s music dip under it. Max 2 per video. |
| **Riser** | 1.5 s riser into the payoff line, ending exactly on the payoff word. |

---

## 7. Pacing and hook

### Delivery (Ref 1)
- **Voice from 0.00–0.15 s** (measured 0.06–0.14 s in all 5).
- **Voice is on for 92–93% of the runtime.** Pauses ≥ 0.15 s happen only **0.1–0.6 times per 10 s**, and the longest is 0.38 s. Your current videos measured 60–76% voice, with 3–6 pauses per 10 s and the first word at 0.4–1.5 s. **This is the biggest change.**
- **Rate:** about **3.1–3.8 words/s** (Hindi/Hinglish; Whisper word counts on the 3 transcripts that came through cleanly). Brisk and conversational, like explaining to a friend.
- **Tone:** curious, slightly dramatic, second person ("dekho", "socho", "tum"). Short clauses that run into each other.
- **Length:** 55–70 s (Ref 1: 64–75 s; yours: 36–52 s).

### Script structure (Ref 1 pattern)
1. **Hook, 0–3 s:** an ordinary thing plus a shocking claim, or a big number plus "kyon?".
   - `Dekho ek mamooli sa silver screw…`
   - `3300 digree selsiyas… rocket ka nozzle pighalta kyon nahi?`
   - `Engineer is poori prakriya ko arabon dollar ka scam kyon bolte hain`
2. **Stakes, 3–10 s:** what would go wrong, or why it matters ("agar cooling ek second bhi ruk jaye…").
3. **Twist, about 10–15 s:** "lekin / par / sach to ye hai…".
4. **Context or history, 15–30 s:** the origin story, a person or an era (Humphry Davy, the Industrial Revolution).
5. **Mechanism, 30–50 s:** how it works, with one everyday **analogy** ("bilkul kisi air conditioner ki evaporator coil ki tarah").
6. **Payoff, last 10 s:** "yahi vajah hai…", "ye ab tak ka sabse brilliant…", then the end card. An optional CTA line is `subscribe kar do`.

### Shot pacing
- **Average shot or visual length: 2.5 s** (Ref 1 measured 1.9–3.6 s mean; yours 3.6–9 s). Range 1.2–4.0 s.
- **First 3 s:** at least **2 visual changes**: the thumbnail card, then the hero visual punch-in, then the first cut on the key noun.
- **Keyword overlay:** every **6–10 s**, on the words that carry the idea.
- **Faster in the hook and the payoff** (1.2–2 s shots). Slower in the mechanism section (3–4 s, with zooms and diagram draws).

### Hook frames (your format, fixed)
- **0.00–0.40 s:** **thumbnail card** full-frame (your Ref 2 thumbnail art) with the **voice already speaking**. This keeps channel consistency without the 0.4–1.5 s silence your current videos have.
- **0.40 s:** cross-dissolve of 0.3 s, then a slow push-in on the hero visual.
- **About 1.5 s:** the first data label or keyword pops in, with a pop SFX.

---

## 8. Thumbnail (Ref 2: keep for consistency)

- **Format:** a 1080 × 1920 card, used as **frame 0 of the video** and as the YouTube thumbnail.
- **Composition:** AI-generated dramatic scene. Either your **face with a shocked expression** (open mouth, wide eyes, bottom-right third) or the **hero object** with motion streaks. Background is dark red/black fire-and-embers or a deep-space blue, with a glowing **orange arrow** `#EF880A` pointing at the key object.
- **Headline:** 2–4 lines, **top 15–35%** of the frame, Montserrat 800, **`#FBE414` fill + `#6B1000` 8–10 px stroke**, skew −6°, with 1–2 key words in white. Add one emoji (😱 😳 🤔).
- **Sub-headline:** the bottom 78–92% band (y 1500–1770), same style at 60% size, a question in Hinglish (`Equator pe weight kam ho jata hai?`).
- **Logo:** the Merit Mantra seal, top-right, 150 px.
- **Before/after topics:** a vertical split with a glowing seam, labels in Montserrat 700 32 px white, e.g. "North Pole / Equator".

---

## 9. End card and export

- **End card:** the Merit Mantra fire seal on black `#000000`, **1.2–1.5 s** (measured 1.2–1.7 s), fire burn-in, music tail fading 0.5 s.
- **Render:** 1080 × 1920, 30 fps.
- **Upload master:** upscale to **2160 × 3840** with lanczos (your current uploads are 4K, which gets a higher YouTube bitrate). H.264 High, CRF 16, `-preset slow`, `yuv420p`, AAC 320 kb/s 48 kHz.

---

## 10. Checklist before export

- [ ] First word at ≤ 0.15 s; the thumbnail card lasts ≤ 0.4 s
- [ ] No voice gap > 0.25 s (except one ≤ 0.5 s beat before the payoff)
- [ ] Subtitles: `#151F31` bar, white Montserrat 600 58 px, 3–6 words, lowercase Hinglish, hard swaps
- [ ] Average shot ≤ 2.5 s; hard cuts inside sections, 1.0 s dissolves only between sections; nothing static > 4 s
- [ ] Keyword overlay every 6–10 s, each with a pop SFX
- [ ] Nothing in the YouTube UI zone (below y = 1500); data labels sit above the subtitle bar
- [ ] Grade: shadows navy, highlights ≤ 0.75 luma, saturation ≈ 0.45
- [ ] Music 15 dB under the voice, starts at 0 s, +8 dB build at 30–45%
- [ ] ≤ 3 whooshes, ≤ 2 booms; about 1 SFX per 6–10 s in total
- [ ] −14 LUFS, −1 dBTP
- [ ] End card 1.2–1.5 s; total length 55–70 s
