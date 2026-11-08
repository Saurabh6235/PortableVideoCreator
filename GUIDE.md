# Merit Mantra Video Pipeline: Portable Edition (no Claude needed)

This folder makes **Merit Mantra YouTube Shorts / Instagram Reels** from one topic file. Each topic gives you a **Hinglish** and an **English** version, each with a 4K video, a thumbnail and ready-to-paste YouTube and Instagram text.

It runs on any Windows 10/11 laptop. It needs **no Claude subscription and no other monthly subscription**.

---

## 1. What it costs

| Part | What it uses | Cost |
|---|---|---|
| Rendering, captions, animations, music mix, 4K export | HyperFrames (open-source CLI), FFmpeg, Python on your laptop | **Free** |
| Background music and sound effects | Included in `pipeline\kit\audio` | **Free** |
| Stock images | HyperFrames image search with a **free** HeyGen account | **Free** |
| Voice (Anand, Hindi + English) | Sarvam AI text-to-speech | **Pay per use**, about ₹2–4 per topic (both languages). No monthly fee. New Sarvam accounts get ₹100 free credit. |
| Script writing (optional) | Sarvam chat model `sarvam-105b-conversations` | **Pay per use**, about ₹0.5–1 per script. Or write the script yourself for free (section 6). |

A full topic (two videos) costs roughly **₹3–5** in Sarvam credits. Nothing else is billed.

---

## 2. Moving it to your laptop

1. Copy the whole `MeritMantra-Portable` folder to the laptop, using a USB drive, Google Drive or anything else. Put it anywhere, for example `D:\MeritMantra-Portable` or `C:\Users\<you>\MeritMantra-Portable`.
   - Avoid folders synced by OneDrive while a video renders, because syncing slows rendering down.
   - **Note:** the `.env` file inside holds your Sarvam API key. If you give this folder to anyone else, delete `.env` first.
2. You need:
   - Windows 10 or 11 with **winget**. It comes with Windows 11. On Windows 10, install "App Installer" from the Microsoft Store.
   - An internet connection.
   - About **3 GB** of free disk space: tools, the render browser, and room for the videos.

---

## 3. One-click install

Double-click **`INSTALL.cmd`**. It works through these steps one by one and skips anything already installed:

1. **Python 3.12**: winget package `Python.Python.3.12`.
2. **Node.js LTS**: `OpenJS.NodeJS.LTS`.
3. **FFmpeg**: `Gyan.FFmpeg`.
4. **Python packages**: `sarvamai`, `numpy`, `pillow`, `httpx` (from `setup\requirements.txt`).
5. **HyperFrames CLI 0.9.5** (pinned, so videos always render the same way) and its **render browser** (a headless Chrome, about 150 MB).
6. **HeyGen sign-in.** A browser window opens; sign in or create a **free** account. This is only used for the free stock-image search, and it is never charged.
7. **Your Sarvam API key.**
   - Get it at https://dashboard.sarvam.ai under API keys.
   - Paste it when asked. The input is hidden.
   - It is saved in `.env` in this folder.

If the installer says something is still missing, close the window, open a **new** one and run `INSTALL.cmd` again. Freshly installed tools only show up in a new window.

**Check at any time:** double-click **`CHECK_SETUP.cmd`**. It only reports and never changes anything.

---

## 4. Make a video (automatic)

1. Open the `inbox` folder. Copy `TEMPLATE.txt` to a new file, for example `sky-blue.txt`, and fill it in:
   ```
   Topic: Why Is the Sky Blue?
   Title: Why Is the Sky Blue and Sunsets Orange?
   Hook: "Aasmaan neela kyun dikhta hai? Aur shaam ko wahi aasmaan orange kaise ho jaata hai?"
   Hidden science: Rayleigh scattering, wavelength of light, longer sunlight path at sunset.
   Interesting fact: On Mars the daytime sky looks butterscotch and the sunset looks blue.
   ```
   Only `Topic:` is required, but the more you give, the better the script.
2. Double-click **`MAKE_VIDEO.cmd`**. It takes the newest `.txt` in `inbox` and runs these steps:
   1. **Script**: Sarvam writes the Hinglish and English script, keywords, image searches, thumbnail text and upload text, in about 1 minute.
   2. **Layout**: shots, keyword pop-ups, flash on the twist, light streak on the payoff, the subscribe ending, and music, all automatic.
   3. **Voices**: Anand, Hindi and English, with exact caption timing.
   4. **Images**: free stock search. A contact sheet of the images opens. If they look fine, press **Enter**. To swap one, see section 7.
   5. **Render**: both languages, upscaled to 4K, at −14 LUFS loudness. This takes about 3–5 minutes per language.
3. Your files appear in **`export\<date>_<Name>_Hinglish\`** and **`export\<date>_<Name>_English\`**:
   - `Merit-Mantra_<Name>_<Lang>.mp4`: upload this. It is 2160×3840.
   - `..._thumbnail.jpg`: the YouTube Shorts thumbnail and Instagram cover. It is also the first frame of the video.
   - `..._YouTube.txt`: title, a blank line, description, a blank line, hashtags. Paste them in that order.
   - `..._Instagram.txt`: the Reel caption.

The topic file then moves to `inbox\done\`.

---

## 5. Recommended: check the script before rendering

The AI writer is good but not perfect. It can choose a weak analogy or round a number wrongly. For best quality, work in two steps:

1. Double-click **`WRITE_SCRIPT.cmd`**. It only writes `videos\<slug>\script.json`. The window shows the slug, for example `why-is-the-sky-blue`.
2. Open `script.json` in Notepad (or VS Code) and read the lines. Fix any wording or fact, and save. Section 6 explains the fields.
3. Double-click **`BUILD_VIDEO.cmd`** and type the slug. It builds everything from your edited script.

---

## 6. Free mode: write the script yourself

To spend nothing on script writing, set `"script_writer": "manual"` in `config\settings.json`, then:

1. Make a folder `videos\<your-slug>\`, for example `videos\why-is-the-sky-blue\`. Use lowercase letters and hyphens.
2. Copy `examples\radar-rain.script.json` into it as `script.json` and replace the content. It is a complete, working example.
3. Run `BUILD_VIDEO.cmd <your-slug>`.

**`script.json` fields:**

| Field | What to write |
|---|---|
| `name` | File-name title, letters and hyphens only, for example `Sky-Blue` |
| `images` | 8–10 entries, `"key": "stock photo search phrase"`, for example `"sunset": "orange sunset over city skyline"`. Use concrete, photographable things with no text in the picture. Objects like a plane, dish or bird often come back as transparent cut-outs, which look great. |
| `thumb` | `img` (an image key), `line1` (white, 2–3 words), `line2` (yellow, 2–4 words plus one emoji), `sub` (a short hook question). Each has `"hi"` and `"en"` text. |
| `lines` | 15–18 lines, from the hook to the payoff. **Do not write the subscribe line**: it is added automatically from `config\settings.json`. |
| `lines[].hi.tts` | The Hinglish line in **Devanagari**. This is what the voice reads. Write numbers as words. |
| `lines[].hi.cap` | The same words romanized in lowercase, split into 2 or more phrases of 3–6 words (30 characters or fewer each). These are the on-screen captions. |
| `lines[].en.tts` / `en.cap` | The English line and its lowercase caption phrases (2 or more). |
| `lines[].img` | (optional) which image to show for this line |
| `lines[].kw` | (optional) an on-screen keyword in CAPS plus an emoji, for example `{"hi": "SCATTERING 🌈", "en": "SCATTERING 🌈"}`, or `null`. Roughly every second line is good. |
| `twist` / `payoff` | The ids of the twist line ("lekin asli raaz…") and the payoff line (the answer). They get a short pause, a flash or a light streak, and a boom. |
| `meta.hi` / `meta.en` | `title` (70 characters or fewer, no emoji, no `|`), `description` (2–3 paragraphs ending with the subscribe line), `hashtags` (12–16, comma-separated, include `#Shorts, #MeritMantra`), `instagram` (caption with 8–10 hashtags). |

Script structure that works: **hook** → why it matters → **twist** → the mechanism step by step with **one everyday Indian analogy** → interesting fact → **payoff**. That's 180–250 spoken words, about 55–85 seconds.

---

## 7. Swap an image you don't like

1. Open `videos\<slug>\script.json` and change that image's search phrase under `"images"`.
2. Open `videos\<slug>\media\assets.json` and delete that image's line.
3. Run `BUILD_VIDEO.cmd <slug>` again. Voices are reused, not re-bought: only the changed image is fetched again.

You can also put your **own picture** in `videos\<slug>\media\` and point its line in `assets.json` at it, for example `"sunset": "media/my_sunset.jpg"`.

---

## 8. Settings (`config\settings.json`)

| Setting | Meaning |
|---|---|
| `languages` | `["hi", "en"]` makes both. Use `["hi"]` for Hinglish only, which halves the voice cost and the render time. |
| `script_writer` | `"sarvam"` (automatic) or `"manual"` (you write `script.json`) |
| `sarvam_chat_model` | `sarvam-105b-conversations`: fast and cheap. **Don't** use `sarvam-105b` here; it spends its whole reply budget "thinking" and returns nothing. |
| `review_images` | `true` opens the image sheet and waits for Enter. `false` goes straight to rendering. |
| `voice.hi.speaker` | `anand_hi_documentary` (default) or `shubh_hi_stories_dramatic` (your second choice). Samples are in the `voices\` folder. |
| `voice.*.pace` | Speaking speed. 1.2 is the channel default; higher is faster. |
| `cta` | The subscribe ending in both languages: voice text plus captions. |

**Re-voicing:** delete the folder `videos\<slug>\audio\<hi|en>\lines` and run `BUILD_VIDEO.cmd <slug>`.
- **Changed only the captions (`cap`)?** No re-voicing is needed. The timing is recomputed on every build, for free.
- **Changed a line's spoken text (`tts`)?** Delete just that line's file, for example `audio\hi\lines\L05.wav`. Only that line is voiced again.

---

## 9. Folder map

```
MeritMantra-Portable\
  INSTALL.cmd        one-click installer
  CHECK_SETUP.cmd    checks everything (changes nothing)
  MAKE_VIDEO.cmd     topic in inbox  -> finished videos
  WRITE_SCRIPT.cmd   topic in inbox  -> script.json only (to review it first)
  BUILD_VIDEO.cmd    script.json     -> finished videos
  GUIDE.md           this guide
  .env               your Sarvam API key (created by INSTALL.cmd; keep it private)
  config\settings.json   languages, voices, pace, writer, subscribe line
  inbox\             put topic .txt files here (TEMPLATE.txt = format); done\ = used topics
  videos\<slug>\     everything for one topic: input.txt, script.json, spec.json, audio, media, builds, auto_log.txt
  export\            finished videos, thumbnails and upload text
  examples\          radar-rain.script.json (hand-written example), radar-rain.spec.json (full engine spec)
  pipeline\auto.py       the conductor (make / write / build)
  pipeline\writer.py     Sarvam script writer
  pipeline\layout.py     script.json -> spec.json (shots, keywords, music, thumbnail)
  pipeline\engine\       mm_audio.py (voice, timing, images), mm_build.py (plates, compose, mix, render, export), mm_check.py (validator)
  pipeline\kit\          house music, sound effects, end card, Merit Mantra seal
  pipeline\SPEC_GUIDE.md full spec format, for hand-tuning shots, diagrams, data counters
  docs\style-sheet.md    the channel's house style (fonts, colours, timings)
  voices\                voice samples + voices.json
  setup\                 install.ps1, requirements.txt
```

---

## 10. Advanced: hand-tune a video

`script.json` covers the creative part. For full control (custom diagrams, number counters, tags, exact shot timing), edit `videos\<slug>\spec.json` directly, using `pipeline\SPEC_GUIDE.md` and `examples\radar-rain.spec.json`. Then run each step yourself so the layout doesn't overwrite your edits:

```
py -3.12 pipeline\engine\mm_check.py videos\<slug>
py -3.12 pipeline\engine\mm_build.py all videos\<slug>
```

(Run these from inside `videos\<slug>`, or pass full paths. `BUILD_VIDEO.cmd` re-creates `spec.json` from `script.json` every time.)

---

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| "py is not recognized" / "ffmpeg is not recognized" | Open a **new** window and run `INSTALL.cmd` again. |
| `SARVAM_API_KEY is missing` | Run `INSTALL.cmd`, or create `.env` with the line `SARVAM_API_KEY=your-key`. |
| Error 402 from Sarvam | Your Sarvam credits ran out. Top up at dashboard.sarvam.ai. |
| Error 429 from Sarvam | Too many requests too fast. Wait a minute and run again. Finished steps are not repeated. |
| Script writer fails ("did not return valid JSON", "skipped line") | Run `WRITE_SCRIPT.cmd` again; the AI is sometimes inconsistent. Or write `script.json` yourself (section 6). |
| An image says FAILED | Its search phrase found nothing. Change it in `script.json` (section 7). |
| HeyGen sign-in expired | Run `INSTALL.cmd`; it signs you in again. |
| Render is very slow | Close other apps, and keep the laptop plugged in. The first render also downloads fonts. |
| Anything else | Read `videos\<slug>\auto_log.txt`. Every command and its output is logged there. |

Every step can be re-run safely: finished voices and images are reused, so a re-run only redoes what is missing.

---

## 12. What's different from the Claude version

The original project in `D:\AI Video Editor` (left untouched) used Claude to write and fact-check scripts, review images and invent new animated diagrams for each topic. This portable edition replaces that with:
- Sarvam's chat model (or you) for the script.
- An automatic layout made of photo shots, cut-outs, keyword pop-ups, a flash on the twist, a streak on the payoff, and the subscribe ending.

Videos are clean and on-brand, but simpler. They have no topic-specific animated diagrams unless you add them to the spec by hand (section 10). The scripts are good drafts, so give them a quick read (section 5).
