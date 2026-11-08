# Turns a simple videos\<slug>\script.json (written by writer.py or by hand) into the full engine spec.json:
# plates, sections, shots, keyword overlays, flash/streak, CTA, thumbnail and music are laid out automatically.
#   py -3.12 pipeline\layout.py <video_dir>
# Run it again after the images are fetched (media\assets.json): it then picks cover / framed / cut-out per image.
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def jload(p): return json.load(open(p, encoding='utf-8'))

def image_kinds(vd, keys):
    # cover for tall photos, framed for wide ones, cut for transparent PNG cut-outs; framed until the images are fetched
    ap = vd / 'media' / 'assets.json'
    if not ap.exists(): return {k: 'framed' for k in keys}
    from PIL import Image
    A = jload(ap); kinds = {}
    for k in keys:
        if k not in A or not (vd / A[k]).exists(): continue          # not fetched: leave it out
        im = Image.open(vd / A[k])
        if im.mode in ('RGBA', 'LA') and im.getchannel('A').getextrema()[0] < 20: kinds[k] = 'cut'
        elif im.height >= im.width * 1.1: kinds[k] = 'cover'
        else: kinds[k] = 'framed'
    return kinds

def tidy_meta(m):
    # hashtags as one comma-separated line; build an Instagram caption if the writer left it out
    m = dict(m); tags = m.get('hashtags', '')
    if isinstance(tags, list): tags = ', '.join(tags)
    tags = ', '.join(t if t.startswith('#') else '#' + t for t in (x.strip() for x in tags.split(',')) if t)
    m['hashtags'] = tags
    if not m.get('instagram'):
        first = m.get('description', '').split('\n')[0].strip()
        m['instagram'] = f"{m.get('title', '')}\n\n{first}\n\n" + ' '.join(tags.replace(',', ' ').split()[:10])
    elif isinstance(m['instagram'], list): m['instagram'] = '\n'.join(m['instagram'])
    return m

def build(vd):
    vd = Path(vd); C = jload(vd / 'script.json'); cfg = jload(ROOT / 'config' / 'settings.json')
    langs = C.get('langs') or cfg['languages']
    lines = [dict(l) for l in C['lines']]
    cta = {'id': f'L{len(lines) + 1:02d}', **{lg: cfg['cta'][lg] for lg in langs}}
    lines.append(cta)
    ids = [l['id'] for l in lines]
    kinds = image_kinds(vd, list(C['images']))
    imgs = [k for k in C['images'] if k in kinds]
    plates = {'p_navy': {'kind': 'navy', 'glow': [0.5, 0.42]}, 'p_navy_warm': {'kind': 'navy', 'glow': [0.5, 0.3], 'glow2': [0.5, 0.55]}}
    for k in imgs:
        if kinds[k] == 'cut': plates[f'c_{k}'] = {'kind': 'cut', 'img': k, 'w': 900}
        elif kinds[k] == 'cover': plates[f'p_{k}'] = {'kind': 'cover', 'img': k}
        else: plates[f'p_{k}'] = {'kind': 'framed', 'img': k, 'fy': 0.42}

    twist, payoff = C.get('twist'), C.get('payoff')
    nchunk = lambda lid: min(len(next(l for l in lines if l['id'] == lid)[lg]['cap']) for lg in langs)
    def shot_for(i, l, cyc):
        photos = [k for k in imgs if kinds[k] != 'cut']           # a missing image falls back to a photo, never a cut-out
        key = l.get('img') if l.get('img') in kinds else (photos[cyc % len(photos)] if photos else None)
        sh = {'name': f's{i + 1:02d}', 'at': l['id'], 'push': [1.0, 1.08] if i % 2 == 0 else [1.08, 1.0]}
        if key and kinds[key] == 'cut':
            sh['plate'] = 'p_navy_warm' if i % 2 else 'p_navy'
            sh['cut'] = {'png': f'c_{key}', 'x': 30, 'y': 560, 'w': 1020, 'move': [-40, 30, 40, -30, -2, 2]}
        else:
            sh['plate'] = f'p_{key}' if key else 'p_navy'
        return sh

    # sections: hook (L01-L02), then groups of 3 lines; the twist and the payoff always open a new section
    groups, cur = [], []
    for i, l in enumerate(lines[:-1]):
        new = i == 2 or l['id'] in (twist, payoff) or (i > 2 and len(cur) >= 3)
        if new and cur: groups.append(cur); cur = []
        cur.append(l)
    groups.append(cur + [cta])
    sections, last_kw, cyc = [], -99, 0
    for gi, g in enumerate(groups):
        shots = []
        for l in g:
            i = ids.index(l['id'])
            if l is cta:
                shots.append({'name': 'cta', 'at': l['id'], 'plate': 'p_navy', 'push': [1.0, 1.04], 'cta': True,
                              'cta_at': f"{l['id']}:1" if nchunk(l['id']) > 1 else f"{l['id']}+0.6"})
                continue
            sh = shot_for(i, l, cyc); cyc += 1
            if l['id'] == twist: sh['flash'] = True
            if l['id'] == payoff: sh['streak'] = True
            kw = l.get('kw')
            if kw and all(kw.get(lg) for lg in langs) and (i - last_kw >= 2 or l['id'] in (twist, payoff)):
                words = len(kw[langs[0]].split())
                sh['kw'] = [{'at': f"{l['id']}:1" if nchunk(l['id']) > 1 else f"{l['id']}+0.3",
                             'text': {lg: kw[lg].upper() for lg in langs}, 'cls': 'punch' if words <= 2 else 'wide',
                             'top': 400}]
                last_kw = i
            shots.append(sh)
        sections.append({'id': f's{chr(97 + gi)}', 'at': shots[0]['at'], 'shots': shots})
    # up to 3 dissolves, spread out, never on the twist/payoff sections (those hard-cut with flash/streak)
    cand = [i for i, s in enumerate(sections) if 0 < i < len(sections) - 1 and s['at'] not in (twist, payoff)]
    for i in cand[::max(1, len(cand) // 3)][:3]: sections[i]['dissolve'] = True

    th = C['thumb']; tkey = th.get('img') if th.get('img') in kinds else (imgs[0] if imgs else None)
    # long headlines get smaller type so line1 stays on 1-2 lines and line2 on one
    longest = lambda v: max(len(x) for x in (v.values() if isinstance(v, dict) else [v]))
    size1 = 130 if longest(th['line1']) <= 12 else (104 if longest(th['line1']) <= 18 else 84)
    size2 = 84 if longest(th['line2']) <= 16 else (70 if longest(th['line2']) <= 22 else 58)
    thumb = {'line1': th['line1'], 'line2': th['line2'], 'sub': th['sub'], 'size1': size1, 'size2': size2}
    if tkey and kinds[tkey] == 'cut':
        thumb.update(plate='p_navy_warm', cuts=[{'png': f'c_{tkey}', 'x': 150, 'y': 760, 'w': 780}])
    elif tkey:
        plates['p_thumb'] = dict(plates[f'p_{tkey}'], grade={'bright': 0.65}); thumb['plate'] = 'p_thumb'
    else:
        thumb['plate'] = 'p_navy_warm'

    n = len(lines)
    music = [{'track': 'bgm_001', 'at': 'L01', 'gain': -18},
             {'track': 'bgm_003', 'at': ids[min(4, n - 1)], 'gain': -11},
             {'track': 'bgm_002', 'at': ids[max(5, int(n * 0.75))], 'gain': -12}]
    name = re.sub(r'[^A-Za-z0-9-]+', '-', C['name']).strip('-') or 'Video'
    spec = {'slug': vd.name, 'name': name, 'langs': langs, 'voice': {lg: cfg['voice'][lg] for lg in langs},
            'beats': [x for x in (twist, payoff) if x], 'lines': [{k: l[k] for k in ['id'] + langs} for l in lines],
            'images': C['images'],   # always all of them, so a newly added or swapped image still gets fetched
            'plates': plates, 'thumb': thumb, 'sections': sections, 'payoff': payoff or ids[-2], 'music': music,
            'meta': {lg: tidy_meta(C['meta'][lg]) for lg in langs}}
    json.dump(spec, open(vd / 'spec.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('layout ->', vd / 'spec.json', f'({len(sections)} sections, {sum(len(s["shots"]) for s in sections)} shots, {len(imgs)} images)')

if __name__ == '__main__':
    build(sys.argv[1])
