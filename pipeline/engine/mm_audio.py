# Merit Mantra engine - voice + narration + asset fetching (needs network)
#   py -3.12 engine\mm_audio.py voice   <video_dir> <lang> [L01,L05]   Sarvam TTS per line
#   py -3.12 engine\mm_audio.py narrate <video_dir> <lang>             join lines -> narration + timing
#   py -3.12 engine\mm_audio.py assets  <video_dir>                    stock images (+ shared music/SFX)
import base64, json, os, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]          # the MeritMantra-Portable folder
def load_env():
    env = ROOT / '.env'
    for line in env.read_text(encoding='utf-8').splitlines() if env.exists() else []:
        k, sep, v = line.partition('=')
        if sep and k.strip() and not k.strip().startswith('#'): os.environ.setdefault(k.strip(), v.strip())

def spec_of(vd): return json.load(open(Path(vd) / 'spec.json', encoding='utf-8'))

def voice(vd, lang, only=None):
    load_env()
    from sarvamai import SarvamAI
    S = spec_of(vd); cfg = S['voice'][lang]
    client = SarvamAI(api_subscription_key=os.environ['SARVAM_API_KEY'])
    out = Path(vd) / 'audio' / lang / 'lines'; out.mkdir(parents=True, exist_ok=True)
    speakers = [cfg['speaker']] + cfg.get('fallback_speakers', [])
    used = None
    for l in S['lines']:
        if only and l['id'] not in only: continue
        for sp in ([used] if used else speakers):
            try:
                r = client.text_to_speech.convert(text=l[lang]['tts'], language_code=cfg['language'], model=cfg.get('model', 'bulbul:v4-flash'),
                                                  speaker=sp, pace=cfg.get('pace', 1.2), speech_sample_rate=44100)
                (out / f"{l['id']}.wav").write_bytes(base64.b64decode(''.join(r.audios)))
                used = sp; print(l['id'], 'ok', sp, flush=True); break
            except Exception as e:
                print(l['id'], 'speaker', sp, 'failed:', str(e)[:200], flush=True)
        else:
            raise SystemExit(f'voice failed for {l["id"]}')
    json.dump({'speaker_used': used}, open(Path(vd) / 'audio' / lang / 'voice_used.json', 'w'))

def narrate(vd, lang):
    S = spec_of(vd); SR = 48000; beats = set(S.get('beats', []))
    base = Path(vd) / 'audio' / lang
    t = 0.05; out = [np.zeros(int(0.05 * SR), np.float32)]; timing = []
    for l in S['lines']:
        x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(base / 'lines' / f"{l['id']}.wav"), '-ac', '1', '-ar', str(SR),
                                          '-af', 'silenceremove=stop_periods=-1:stop_duration=0.12:stop_threshold=-38dB', '-f', 'f32le', '-'],
                                         capture_output=True).stdout, np.float32)
        idx = np.where(np.abs(x) > 0.01)[0]; x = x[max(0, idx[0] - int(0.02 * SR)):idx[-1] + int(0.04 * SR)]
        if l['id'] in beats: out.append(np.zeros(int(0.25 * SR), np.float32)); t += 0.25
        timing.append({'id': l['id'], 'start': round(t, 3), 'end': round(t + len(x) / SR, 3), 'cap': l[lang]['cap']})
        out.append(x); t += len(x) / SR; out.append(np.zeros(int(0.10 * SR), np.float32)); t += 0.10
    raw = base / 'raw.f32'; np.concatenate(out).astype(np.float32).tofile(raw)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', str(raw), str(base / 'narration.wav')], check=True)
    raw.unlink()
    caps = []
    for s in timing:
        n = [max(1, len(re.sub(r'[^a-z0-9]', '', c.lower()))) for c in s['cap']]; T = s['end'] - s['start']; acc = s['start']
        for c, k in zip(s['cap'], n):
            d = T * k / sum(n); caps.append({'line': s['id'], 'text': c, 'start': round(acc, 3), 'end': round(acc + d, 3)}); acc += d
    for i in range(len(caps) - 1): caps[i]['end'] = caps[i + 1]['start']
    words = sum(len(' '.join(s['cap']).split()) for s in timing); speech = sum(s['end'] - s['start'] for s in timing)
    json.dump({'lines': timing, 'captions': caps, 'voice_end': timing[-1]['end'], 'words_per_sec': round(words / speech, 2)},
              open(base / 'timing.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(lang, 'narration done; voice_end', timing[-1]['end'], 'wps', round(words / speech, 2))

def assets(vd):
    S = spec_of(vd); vd = Path(vd); media = vd / 'media'; media.mkdir(exist_ok=True)
    env = dict(os.environ, HEYGEN_NO_ANALYTICS='1')
    mp = vd / 'media' / 'assets.json'; got = json.load(open(mp)) if mp.exists() else {}
    for key, intent in S['images'].items():
        if key in got and (vd / got[key]).exists(): continue
        r = subprocess.run(f'npx --yes hyperframes@0.9.5 media-use resolve --type image --intent "{intent}" --project .', shell=True,
                           cwd=vd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        m = re.search(r'resolved \S+ \S+ (\S+) \(', r.stdout)
        if m: got[key] = m.group(1).replace('\\', '/'); print(key, '->', got[key], flush=True)
        else: print(key, 'FAILED', r.stdout[-300:], r.stderr[-300:], flush=True)
        json.dump(got, open(mp, 'w'), indent=1)
    # shared music / SFX / brand from the house kit
    kit = ROOT / 'pipeline' / 'kit'
    for sub in ['audio', 'brand']:
        if (kit / sub).exists():
            shutil.copytree(kit / sub, vd / 'kit' / sub, dirs_exist_ok=True)
    print('assets done')

if __name__ == '__main__':
    cmd, vd = sys.argv[1], sys.argv[2]
    if cmd == 'voice': voice(vd, sys.argv[3], sys.argv[4].split(',') if len(sys.argv) > 4 else None)
    elif cmd == 'narrate': narrate(vd, sys.argv[3])
    elif cmd == 'assets': assets(vd)
