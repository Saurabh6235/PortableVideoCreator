# How to write a Merit Mantra video spec (`videos/<slug>/spec.json`)

One spec = one topic = a Hinglish **and** an English short (same visuals, two voices, two caption tracks, two upload texts).
Worked example: `videos/radar-rain/spec.json`. House style: `style-sheet.md`. Validate with `py -3.12 pipeline\engine\mm_check.py videos\<slug>`.

## Script (`lines`)
- 17–21 lines, 180–250 spoken words per language (55–85 s). Ref-1 structure: **hook** (the user's hook, verbatim if given) → stakes → **twist line** ("lekin/par asli jaadu…") → mechanism with one everyday analogy → the interesting fact → **payoff** line → **CTA** (last line, always):
  - hi: `ऐसी ही कॉन्सेप्चुअल क्लैरिटी के लिए, सब्सक्राइब करें मेरिट मंत्रा।` / cap `["aisi hi conceptual clarity ke liye", "subscribe karein merit mantra"]`
  - en: `For more conceptual clarity like this, subscribe to Merit Mantra.` / cap `["for more conceptual clarity like this", "subscribe to merit mantra"]`
- `hi.tts` in **Devanagari** (English science words written in Devanagari, numbers as words: "सौ किलोमीटर"). `hi.cap` = romanized lowercase Hinglish phrases of the same words, 3–6 words each, ≤ 32 chars (max 40), numbers as digits.
- `en.tts` natural spoken English; `en.cap` lowercase phrases of the same words.
- Every science claim must be correct; prefer safe wording ("less than a millisecond") to precise numbers you are unsure of.
- `beats`: the twist line id and the payoff line id (a 0.25 s pause before each).

## Time references
`"L05"` = start of line 5 · `"L05:2"` = start of its 3rd caption phrase (index from 0; must exist in **both** languages, so use an index below the smaller phrase count) · `"L05:2+0.3"` / `"L05-0.2"` = offset in seconds · `"end"` = end of voice.

## Images (`images`)
Key → search phrase for free stock search (`media-use resolve --type image`). 8–12 images. Ask for concrete photographable things ("tornado supercell storm", "ambulance siren lights night", "radar antenna dish"). Cut-out objects (dish, dome, bird, plane) often come back as transparent PNGs. Never rely on an image containing text.

## Plates (`plates`) — graded 1080×1920 backgrounds made from images
- `{"kind":"cover","img":"rain","fx":0.5,"fy":0.5,"grade":{"bright":0.8}}` full-bleed crop (vertical or big images)
- `{"kind":"framed","img":"tornado","fy":0.42}` small/landscape image shown full width over its own blur
- `{"kind":"navy","glow":[0.5,0.42],"glow2":[0.5,0.5]}` brand background for diagrams/keywords (glow2 = warm orange)
- `{"kind":"cut","img":"dish","w":900}` transparent PNG object with orange rim glow (only for PNG cut-outs)

## Sections & shots
Sections ≈ story beats (6–8). A section starts at its first shot's `at`. `"dissolve": true` = 1 s cross-fade into it (+ whoosh) — use for 3 section changes max; others hard-cut. Each shot lasts until the next shot's `at`; target 2.5–4 s per shot (one per line is fine; split long lines).
Shot fields:
- `name` (unique in section), `at`, `plate`, `push` ([1.0,1.08] default slow push-in)
- `cut`: `{"png":"c_dish","x":90,"y":700,"w":900,"move":[x0,y0,x1,y1,rot0,rot1]}` (left/top px; keep subjects between y 250 and 1330)
- `kw`: keyword overlays `[{"at":"L06:1","text":{"hi":"REFLECTION 🔁","en":"REFLECTION 🔁"},"cls":"wide|punch","top":400,"until":"L07"}]` — ALL CAPS, 1–4 words + one emoji, every 6–10 s; `punch` for 1–2 big words, `wide` otherwise; top 330–480 (or 760 for a centre punch)
- `tags`: small labels `[{"at":"L13:1","text":{...},"x":200,"y":470,"warm":true}]`
- `data`: number counter above the captions `{"at":"L02:2","to":100,"prefix":"< ","unit":"km","label":{...}}`
- `flash: true` (white flash + boom; use on the twist), `streak: true` (light streak + boom; use on the payoff)
- `cta: true, "cta_at":"L19:1"` on the last shot (seal + SUBSCRIBE button)
- `diagram`: SVG animations drawn in code — `wave` (travelling wave), `pulses` (`x`,`y`,`icon`; expanding arcs from a point), `bounce` (radar pulse passes small drops, echoes off big drops), `distance` (radar ↔ cloud out-and-back), `colorbar` (`rows`: [[hex, key]…], `ats`: one ref per row, `text`: key → {hi,en}), `doppler` (moving source with bunched waves), `couplet` (green/red rotation pair). New topics may need new diagram types → add them to `diag()` in `pipeline/engine/mm_build.py` and to `DIAGRAMS` in `mm_check.py`.

## Thumbnail (`thumb`) — frame 0, also the exported thumbnail
`{"plate":"p_thumb","cuts":[{"png":"c_dish","x":150,"y":760,"w":780}],"line1":{hi,en},"line2":{hi,en},"sub":{hi,en},"size1":130,"size2":84}` — line1 white, line2 yellow (with one emoji), sub = short hook at the bottom.

## Music (`music`)
`[{"track":"bgm_001","at":"L01","gain":-18},{"track":"bgm_003","at":"<mechanism line>","gain":-11},{"track":"bgm_002","at":"<twist/payoff section>","gain":-12}]` (dark tension → orchestral build → uplifting). `payoff`: the payoff line id (the riser lands there).

## Upload text (`meta`, per language)
- `title`: ONE title, ≤ 70 chars ideally (max 100), keyword first, a question works well, **no emoji, no `|`, no hashtags**. English title = the user's title if given.
- `description`: 2–3 short paragraphs, keywords early (topic, the hidden science terms), ends with the subscribe line.
- `hashtags`: 12–16 hashtags separated by commas: `#Topic, #KeyTerm, …, #Shorts, #MeritMantra`.
- `instagram`: hook line + 2 lines + CTA + 8–10 hashtags (spaces).
The engine writes `<name>_YouTube.txt` as: title, blank line, description, blank line, hashtags (no headers).
