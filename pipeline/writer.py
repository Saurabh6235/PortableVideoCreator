# Writes videos\<slug>\script.json from a topic file with Sarvam's chat model (pay per use, roughly Rs 1 per script).
#   py -3.12 pipeline\writer.py <topic.txt> <video_dir>
# Pay-as-you-go caps each reply at 4096 tokens, so the script is written in small steps:
#   1. outline (lines as ideas, image searches, thumbnail)  2. the lines, 4 at a time, in both languages  3. upload text
import json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.load(open(ROOT / 'config' / 'settings.json', encoding='utf-8'))
LANGS = CFG['languages']

BRIEF = """You write scripts for "Merit Mantra", an Indian YouTube Shorts / Instagram Reels channel of 60-80 second science explainers.
Voice: a confident, friendly Indian narrator speaking Hinglish (Hindi with everyday English science words), plus an English version.
Structure (Ref-1): HOOK (the user's hook, verbatim if given) -> stakes / why it matters -> a TWIST line ("lekin asli raaz..." / "but here's the twist") ->
the mechanism, step by step, with ONE everyday Indian analogy -> the interesting fact -> a PAYOFF line that answers the hook.
Do NOT write a subscribe/CTA line: it is added automatically after the payoff.
Every science claim must be correct. If unsure of an exact number, use safe wording ("lagbhag", "about", "less than a second").
Reply with JSON only."""

def load_env():
    env = ROOT / '.env'
    for line in env.read_text(encoding='utf-8').splitlines() if env.exists() else []:
        k, sep, v = line.partition('=')
        if sep and k.strip() and not k.strip().startswith('#'): os.environ.setdefault(k.strip(), v.strip())

def ask(client, prompt, tries=3):
    for t in range(tries):
        try:
            # reasoning tokens count against max_tokens (4096 on pay-as-you-go); the default effort reasons least
            r = client.chat.completions(model=CFG.get('sarvam_chat_model', 'sarvam-105b-conversations'), max_tokens=4096, temperature=0.5,
                                        response_format={'type': 'json_object'},
                                        messages=[{'role': 'system', 'content': BRIEF}, {'role': 'user', 'content': prompt}])
            txt = r.choices[0].message.content or ''
            if not txt.strip():
                raise ValueError(f'empty reply (finish: {r.choices[0].finish_reason}, tokens: {r.usage.completion_tokens})')
            txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt.strip())
            return json.loads(txt[txt.find('{'):txt.rfind('}') + 1])
        except Exception as e:
            print(f'  retry {t + 1}: {str(e)[:200]}', flush=True); time.sleep(3)
    raise SystemExit('Sarvam chat did not return valid JSON. Try again, or write script.json by hand (see GUIDE.md).')

DEVANAGARI = re.compile('[ऀ-ॿ]')

def fix_caps(caps):
    # re-chunk the line's caption words evenly: phrases of up to 6 words / 28 characters, never a lone 1-word tail, at least 2
    words = ' '.join(' '.join(str(c).lower().split()) for c in caps).split()
    out, cur = [], []
    for w in words:
        if cur and (len(' '.join(cur + [w])) > 28 or len(cur) >= 6): out.append(cur); cur = []
        cur.append(w)
    if cur:
        if len(cur) == 1 and out and len(' '.join(out[-1] + cur)) <= 34: out[-1] += cur
        else: out.append(cur)
    if len(out) == 1 and len(out[0]) >= 2: h = (len(out[0]) + 1) // 2; out = [out[0][:h], out[0][h:]]
    return [' '.join(x) for x in out]

def en_caps(tts): return fix_caps([re.sub(r"[^\w\s'?%-]", ' ', tts.lower())])

def write(topic_file, vd):
    load_env()
    if not os.environ.get('SARVAM_API_KEY'): raise SystemExit('SARVAM_API_KEY is missing: run INSTALL.cmd again or put it in the .env file.')
    from sarvamai import SarvamAI
    client = SarvamAI(api_subscription_key=os.environ['SARVAM_API_KEY'])
    topic = Path(topic_file).read_text(encoding='utf-8')
    vd = Path(vd); vd.mkdir(parents=True, exist_ok=True)

    print('1/3 outline...', flush=True)
    O = ask(client, f"""Topic file from the channel owner:
---
{topic}
---
Plan the short. Return JSON with exactly these keys:
"name": 2-4 English words joined by hyphens for file names (e.g. "Plane-Window-Hole"),
"images": an object of 8-10 entries, key = short lowercase word, value = a stock-photo search phrase for a REAL PHOTOGRAPH of a concrete thing, ending with the word "photo" (never diagrams, charts, infographics, illustrations or anything with text; objects like a plane, dish or bird often come as transparent cut-outs),
"outline": a list of 16-18 items {{"id": "L01".., "idea": one sentence in English of what this line says, "img": one of the image keys}} following the structure; L01 is the hook,
"twist": the id of the twist line, "payoff": the id of the payoff line (the last outline item),
"thumb": {{"img": an image key, "line1": {{"hi": "...", "en": "..."}}, "line2": {{"hi": "...", "en": "..."}}, "sub": {{"hi": "...", "en": "..."}}}}
  thumbnail text in CAPS romanized Hinglish (hi) / English (en): line1 2-3 words, line2 2-4 words ending with one emoji, sub a short hook question with one emoji.""")
    outline = O['outline']; ids = [o['id'] for o in outline]

    print(f'2/3 writing {len(outline)} lines...', flush=True)
    lines = []
    for i in range(0, len(outline), 4):
        batch = outline[i:i + 4]
        done = '\n'.join(f"{l['id']}: {l['hi']['tts']}" for l in lines[-4:]) or '(none yet)'
        R = ask(client, f"""Topic:
{topic}
Full outline: {json.dumps(outline, ensure_ascii=False)}
Lines written so far (for continuity):
{done}
Now write ONLY these lines: {json.dumps(batch, ensure_ascii=False)}
Return {{"lines": [{{"id": "...", "hi": {{"tts": "...", "cap": [...]}}, "en": {{"tts": "...", "cap": [...]}}, "kw": {{"hi": "...", "en": "..."}} or null}}]}}
Rules:
- hi.tts: the Hinglish line written in DEVANAGARI script, never Roman letters (English science words also in Devanagari, numbers as words),
  8-16 words, spoken and punchy. Example hi.tts: "आसमान नीला क्यों दिखता है? और शाम को वही आसमान ऑरेंज कैसे हो जाता है?"
- hi.cap: the same words romanized in lowercase Hinglish, split into phrases of 3-6 words (max 30 characters each), numbers as digits.
- en.tts: the same line in natural spoken English; en.cap: its lowercase phrases of 3-6 words.
- hi.cap and en.cap must each have at least 2 phrases.
- kw: an on-screen keyword for roughly every second line: 1-3 words in CAPS plus one emoji (hi in romanized Hinglish, en in English); otherwise null.""")
        got = {l['id']: l for l in R.get('lines', [])}
        roman = {i: l['hi']['tts'] for i, l in got.items() if 'hi' in LANGS and not DEVANAGARI.search(l['hi'].get('tts', ''))}
        if roman:   # the model sometimes answers in Roman letters: convert just those lines to Devanagari (the voice needs it)
            D = ask(client, f"""Rewrite each of these Hinglish lines in DEVANAGARI script, same words and meaning, English science words
also written in Devanagari (e.g. "sunlight" -> "सनलाइट"), numbers as Hindi words. Example: "Aasmaan neela kyun dikhta hai?" -> "आसमान नीला क्यों दिखता है?"
Lines: {json.dumps(roman, ensure_ascii=False)}
Return {{"<id>": "<devanagari line>", ...}} for every id.""")
            for i, t in D.items():
                if i in got and DEVANAGARI.search(str(t)): got[i]['hi']['tts'] = str(t)
        dcaps = {i: l['hi']['cap'] for i, l in got.items() if 'hi' in LANGS and any(DEVANAGARI.search(str(c)) for c in l['hi'].get('cap', []))}
        if dcaps:   # captions must be romanized Hinglish: convert any phrase the model wrote in Devanagari
            D = ask(client, f"""Rewrite these caption phrases in romanized lowercase Hinglish (Latin letters only, same words, same number of phrases).
Example: ["आसमान नीला क्यों", "दिखता है?"] -> ["aasmaan neela kyun", "dikhta hai?"]
Phrases: {json.dumps(dcaps, ensure_ascii=False)}
Return {{"<id>": ["...", "..."], ...}} for every id.""")
            for i, caps in D.items():
                if i in got and isinstance(caps, list) and not any(DEVANAGARI.search(str(c)) for c in caps): got[i]['hi']['cap'] = caps
        for o in batch:
            l = got.get(o['id'])
            if not l: raise SystemExit(f'Sarvam skipped line {o["id"]} - run WRITE_SCRIPT again.')
            if 'hi' in LANGS and any(DEVANAGARI.search(str(c)) for c in l['hi']['cap']):
                raise SystemExit(f'{o["id"]}: captions are still in Devanagari - run WRITE_SCRIPT again.')
            if 'en' in LANGS:    # English captions = exactly the spoken words (the model tends to shorten them)
                l['en']['cap'] = en_caps(l['en']['tts'])
            for lg in LANGS:
                l[lg]['cap'] = fix_caps(l[lg]['cap'])
            if 'hi' in LANGS and not DEVANAGARI.search(l['hi']['tts']):
                raise SystemExit(f'{o["id"]}: Hindi line is still not in Devanagari - run WRITE_SCRIPT again.')
            line = {'id': o['id'], **{lg: l[lg] for lg in LANGS}, 'img': o.get('img'), 'kw': l.get('kw')}
            lines.append(line); print('  ', o['id'], line[LANGS[0]]['tts'][:70], flush=True)

    print('3/3 upload text...', flush=True)
    M = ask(client, f"""The finished script (English): {json.dumps([l['en']['tts'] if 'en' in l else l['hi']['tts'] for l in lines], ensure_ascii=False)}
Original topic file:
{topic}
Write upload text. Return {{"hi": {{...}}, "en": {{...}}}} where each has:
"title": ONE title, max 70 characters, keyword first, a question works well, no emoji, no "|", no hashtags (hi = romanized Hinglish, en = English; use the user's English title if the topic file gives one),
"description": 2-3 short paragraphs naming the topic and the hidden science terms early, ending with a line asking viewers to subscribe to Merit Mantra,
"hashtags": 12-16 hashtags separated by commas, including #Shorts and #MeritMantra,
"instagram": a hook line, 2 short lines, a subscribe line and 8-10 hashtags separated by spaces.""")

    script = {'name': O.get('name', vd.name), 'images': O['images'], 'thumb': O['thumb'], 'twist': O.get('twist'),
              'payoff': O.get('payoff', ids[-1]), 'langs': LANGS, 'lines': lines, 'meta': {lg: M[lg] for lg in LANGS}}
    json.dump(script, open(vd / 'script.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('script ->', vd / 'script.json')

if __name__ == '__main__':
    write(sys.argv[1], sys.argv[2])
