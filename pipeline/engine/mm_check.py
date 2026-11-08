# Validates a Merit Mantra video spec before voicing/rendering.  py -3.12 pipeline\engine\mm_check.py <video_dir>
import json, re, sys
from pathlib import Path
DIAGRAMS = {'wave', 'pulses', 'bounce', 'distance', 'colorbar', 'doppler', 'couplet'}
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿]')

def check(vd):
    S = json.load(open(Path(vd) / 'spec.json', encoding='utf-8')); errs = []; warns = []
    langs = S.get('langs', [])
    for k in ['slug', 'name', 'langs', 'voice', 'lines', 'images', 'plates', 'thumb', 'sections', 'music', 'meta']:
        if k not in S: errs.append(f'missing top-level key: {k}')
    if errs: return errs, warns
    if not re.fullmatch(r'[A-Za-z0-9-]+', S['name']): errs.append('name must be letters/digits/hyphens only (used in file names)')
    ids = [l['id'] for l in S['lines']]; nchunks = {}
    for l in S['lines']:
        for lg in langs:
            if lg not in l: errs.append(f'{l["id"]}: missing language {lg}'); continue
            caps = l[lg].get('cap', [])
            if not l[lg].get('tts'): errs.append(f'{l["id"]}.{lg}: empty tts')
            for c in caps:
                if len(c) > 40: errs.append(f'{l["id"]}.{lg}: caption phrase over 40 chars: "{c}"')
                if c != c.lower(): warns.append(f'{l["id"]}.{lg}: captions should be lowercase: "{c}"')
            nchunks.setdefault(l['id'], []).append(len(caps))
    def ref(r, where):
        if isinstance(r, (int, float)): return
        m = re.match(r'(L\d+|end)(?::(\d+))?([+-][\d.]+)?$', str(r))
        if not m: errs.append(f'{where}: bad time ref "{r}"'); return
        if m.group(1) == 'end': return
        if m.group(1) not in ids: errs.append(f'{where}: unknown line {m.group(1)}'); return
        if m.group(2) is not None and int(m.group(2)) >= min(nchunks[m.group(1)]):
            errs.append(f'{where}: "{r}" chunk index too high (line has {min(nchunks[m.group(1)])} phrases in its shortest language)')
    def txt(v, where):
        if isinstance(v, dict):
            for lg in langs:
                if lg not in v: errs.append(f'{where}: text missing language {lg}')
    for pid, p in S['plates'].items():
        if p.get('img') and p['img'] not in S['images']: errs.append(f'plate {pid}: unknown image {p["img"]}')
        if p['kind'] not in ('navy', 'framed', 'cover', 'cut'): errs.append(f'plate {pid}: bad kind {p["kind"]}')
    for c in S['thumb'].get('cuts', []):
        if c['png'] not in S['plates']: errs.append(f'thumb: unknown cut {c["png"]}')
    if S['thumb'].get('plate') not in S['plates']: errs.append('thumb: unknown plate')
    for k in ['line1', 'line2', 'sub']: txt(S['thumb'].get(k, ''), f'thumb.{k}')
    names = set(); last = -1
    for sec in S['sections']:
        ref(sec['at'], f'section {sec["id"]}')
        for sh in sec['shots']:
            w = f'{sec["id"]}/{sh["name"]}'; ref(sh['at'], w)
            if (sec['id'], sh['name']) in names: errs.append(f'{w}: duplicate shot name')
            names.add((sec['id'], sh['name']))
            if sh.get('plate') and sh['plate'] not in S['plates']: errs.append(f'{w}: unknown plate {sh["plate"]}')
            if sh.get('cut') and sh['cut']['png'] not in S['plates']: errs.append(f'{w}: unknown cut {sh["cut"]["png"]}')
            if sh.get('diagram'):
                d = sh['diagram']
                if d['type'] not in DIAGRAMS: errs.append(f'{w}: unknown diagram {d["type"]}')
                for a in d.get('ats', []): ref(a, w + ' diagram')
                for k, v in d.get('text', {}).items(): txt(v, w + ' diagram text')
            for kw in sh.get('kw', []): ref(kw['at'], w + ' kw'); txt(kw['text'], w + ' kw')
            for tg in sh.get('tags', []): ref(tg['at'], w + ' tag'); txt(tg['text'], w + ' tag')
            if sh.get('data'): ref(sh['data']['at'], w + ' data')
    if S['sections'][0]['shots'][0]['at'] != 'L01': errs.append('first shot must start at L01')
    for m in S['music']:
        ref(m['at'], 'music')
        if m['track'] not in ('bgm_001', 'bgm_002', 'bgm_003'): errs.append(f'music: unknown track {m["track"]}')
    for lg in langs:
        mt = S['meta'].get(lg)
        if not mt: errs.append(f'meta: missing {lg}'); continue
        for k in ['title', 'description', 'hashtags']:
            if not mt.get(k): errs.append(f'meta.{lg}: missing {k}')
        if EMOJI.search(mt.get('title', '')) or '|' in mt.get('title', ''): errs.append(f'meta.{lg}.title: no emoji or symbols in the title')
        if len(mt.get('title', '')) > 100: errs.append(f'meta.{lg}.title: over 100 characters')
    words = {lg: sum(len(' '.join(l[lg]['cap']).split()) for l in S['lines'] if lg in l) for lg in langs}
    for lg, n in words.items():
        if not 150 <= n <= 290: warns.append(f'{lg}: {n} spoken words (aim 180-250 for a 55-85 s short)')
    return errs, warns

if __name__ == '__main__':
    e, w = check(sys.argv[1])
    for x in w: print('WARN ', x)
    for x in e: print('ERROR', x)
    print('OK' if not e else f'{len(e)} error(s)')
    sys.exit(1 if e else 0)
