# Merit Mantra engine - plates, HyperFrames composition, mix, render, export (Windows PC)
#   py -3.12 engine\mm_build.py plates  <video_dir>
#   py -3.12 engine\mm_build.py compose <video_dir> <lang>     -> <video_dir>\build_<lang>\ (HyperFrames project)
#   py -3.12 engine\mm_build.py mix     <video_dir> <lang>
#   py -3.12 engine\mm_build.py render  <video_dir> <lang>     render + 4K master + thumbnail + upload text -> export\<date>_<Name>_<Lang>\
#   py -3.12 engine\mm_build.py all     <video_dir>            plates, then compose/mix/render for every language
import html, json, os, re, shutil, subprocess, sys, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / 'pipeline' / 'kit'
W, H = 1080, 1920
LANGNAME = {'hi': 'Hinglish', 'en': 'English'}

def jload(p): return json.load(open(p, encoding='utf-8'))

# =====================================================================================  PLATES
def plates(vd):
    import numpy as np
    from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
    vd = Path(vd); S = jload(vd / 'spec.json'); A = jload(vd / 'media' / 'assets.json')
    out = vd / 'plates'; out.mkdir(exist_ok=True)
    rng = np.random.default_rng(7)
    def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    def src(key): return Image.open(vd / A[key])
    def navy_bg(glow=(0.5, 0.42), glow_col='#1073C7', glow2=None, glow2_col='#EF880A'):
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.42) / H) ** 2)
        c0 = np.array(hexrgb('#0A2A5A'), np.float32); c1 = np.array(hexrgb('#03060E'), np.float32)
        t = np.clip(d / 0.62, 0, 1)[..., None]; img = c0 * (1 - t) + c1 * t
        for g, col in [(glow, glow_col), (glow2, glow2_col)]:
            if g:
                dd = np.sqrt(((x - g[0] * W) / W) ** 2 + ((y - g[1] * H) / W) ** 2); a = np.exp(-(dd / 0.39) ** 2)[..., None] * 0.5
                img = img + np.array(hexrgb(col), np.float32) * a
        xs = rng.integers(0, W, 420); ys = rng.integers(0, H, 420); b = rng.uniform(60, 220, 420)
        for xx, yy, bb in zip(xs, ys, b): img[yy, xx] = np.maximum(img[yy, xx], bb)
        return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    def grade(im, sat=1.2, con=1.08, navy=0.35, bright=1.0):
        im = ImageEnhance.Color(im.convert('RGB')).enhance(sat); im = ImageEnhance.Contrast(im).enhance(con)
        if bright != 1.0: im = ImageEnhance.Brightness(im).enhance(bright)
        a = np.asarray(im).astype(np.float32); l = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255
        sh = np.clip(1 - l * 2.2, 0, 1)[..., None] * navy; a = a * (1 - sh) + np.array(hexrgb('#03132E'), np.float32) * sh
        hl = np.clip((l - 0.6) * 2.5, 0, 1)[..., None] * 0.08; a = a * (1 - hl) + np.array(hexrgb('#FFB060'), np.float32) * hl
        a = np.minimum(a, 0.78 * 255 + (a - 0.78 * 255).clip(0) * 0.4)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    def vignette(im, s=0.55):
        y, x = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.7)) ** 2)
        v = (1 - np.clip(d - 0.45, 0, 1) * s)[..., None]
        return Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * v, 0, 255).astype(np.uint8))
    def cover(im, fx=0.5, fy=0.5):
        r = max(W / im.width, H / im.height); im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
        l = int((im.width - W) * fx); t = int((im.height - H) * fy); return im.crop((l, t, l + W, t + H))
    def framed(im, fy=0.42, p=None):
        g = grade(im, **p) if p else grade(im)
        bg = ImageEnhance.Brightness(cover(g).filter(ImageFilter.GaussianBlur(40))).enhance(0.55)
        r = W / im.width; fg = g.resize((W, int(im.height * r)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
        fh = fg.height; f = 80; ma = np.ones((fh, W), np.float32); ramp = np.linspace(0, 1, f); ma[:f] *= ramp[:, None]; ma[-f:] *= ramp[::-1][:, None]
        bg.paste(fg, (0, int(H * fy - fh / 2)), Image.fromarray((ma * 255).astype(np.uint8))); return vignette(bg)
    def cutout(im, w):
        c = im.convert('RGBA'); c = c.crop(c.getbbox()); r = w / c.width; c = c.resize((int(c.width * r), int(c.height * r)), Image.LANCZOS)
        rgb = grade(c.convert('RGB'), sat=1.15, con=1.05, navy=0.2).convert('RGBA'); rgb.putalpha(c.getchannel('A'))
        pad = 60; o = Image.new('RGBA', (c.width + 2 * pad, c.height + 2 * pad), (0, 0, 0, 0))
        gl = Image.new('RGBA', o.size, hexrgb('#EF880A') + (0,)); ga = Image.new('L', o.size, 0); ga.paste(c.getchannel('A'), (pad, pad))
        gl.putalpha(ga.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.5))); o.alpha_composite(gl); o.alpha_composite(rgb, (pad, pad)); return o
    for pid, p in S['plates'].items():
        k = p['kind']; gp = p.get('grade')
        if k == 'navy': im = navy_bg(tuple(p.get('glow', (0.5, 0.42))), p.get('glow_col', '#1073C7'), tuple(p['glow2']) if p.get('glow2') else None, p.get('glow2_col', '#EF880A'))
        elif k == 'framed': im = framed(src(p['img']), p.get('fy', 0.42), gp)
        elif k == 'cover':
            g = grade(src(p['img']), **gp) if gp else grade(src(p['img']))
            im = cover(g, p.get('fx', 0.5), p.get('fy', 0.5)).filter(ImageFilter.UnsharpMask(2, 50, 2))
            if p.get('blur'): im = im.filter(ImageFilter.GaussianBlur(p['blur']))
            im = vignette(im)
        elif k == 'cut': cutout(src(p['img']), p.get('w', 900)).save(out / f'{pid}.png'); continue
        im.convert('RGB').save(out / f'{pid}.jpg', quality=92)
        print('plate', pid)
    shutil.copy(KIT / 'brand' / 'seal.png', out / 'seal.png')

# =====================================================================================  COMPOSE
BASE_CSS = """
#root{position:absolute;inset:0;overflow:hidden;background:#03060E}
.shot{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden}
.push{position:absolute;left:0;top:0;width:1080px;height:1920px}
.plate{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}
.cut{position:absolute;display:block}
.kw{position:absolute;left:60px;width:960px;text-align:center}
.kw span{display:inline-block}
.punch{font-family:Oswald,sans-serif;font-weight:700;font-size:150px;line-height:1.0;color:#FFFFFF;-webkit-text-stroke:6px #000;paint-order:stroke fill;text-shadow:0 6px 24px rgba(0,0,0,.6);text-transform:uppercase}
.wide{font-family:Montserrat,sans-serif;font-weight:700;font-size:92px;line-height:1.04;color:#FFFFFF;text-shadow:0 4px 18px rgba(0,0,0,.55);text-transform:uppercase}
.tag{position:absolute;font-family:Montserrat,sans-serif;font-weight:600;font-size:30px;letter-spacing:.02em;color:rgba(255,255,255,.92);text-transform:uppercase;white-space:nowrap}
.tag span{display:inline-block;padding:10px 18px;border:2px solid rgba(98,166,226,.9);border-radius:10px;background:rgba(3,6,14,.55);box-shadow:0 0 18px rgba(16,115,199,.6)}
.tag.warm span{border-color:rgba(239,136,10,.95);box-shadow:0 0 18px rgba(239,136,10,.6)}
.flash{position:absolute;left:0;top:0;width:1080px;height:1920px;background:#FFFFFF}
.streak{position:absolute;left:-200px;width:1480px;height:10px;background:linear-gradient(90deg,rgba(16,115,199,0),#62A6E2 40%,#FFFFFF 50%,#62A6E2 60%,rgba(16,115,199,0));box-shadow:0 0 40px 16px rgba(16,115,199,.75)}
"""

class Scene:
    def __init__(s, sid, start, end, fade_in=0.0, underlay=''):
        s.id, s.start, s.end, s.fade_in, s.underlay = sid, start, end, fade_in, underlay
        s.html, s.js, s.z = [], [], 1
    def L(s, t): return round(t - s.start, 3)
    def shot(s, name, t0, t1, plate=None, push=(1.0, 1.08), inner=''):
        sid = f'{s.id}-shot-{name}'
        img = f'<img class="plate" src="assets/plates/{plate}.jpg" alt="">' if plate else ''
        s.html.append(f'<div id="{sid}" class="clip shot" data-start="{s.L(t0)}" data-duration="{round(t1 - t0, 3)}" style="z-index:{s.z}"><div id="{sid}-push" class="push">{img}{inner}</div></div>')
        s.z += 1
        if push: s.js.append(f'tl.fromTo("#{sid}-push",{{scale:{push[0]}}},{{scale:{push[1]},duration:{round(t1 - t0, 3)},ease:"none"}},{s.L(t0)});')
        return sid
    def kw(s, kid, text, t0, t1, cls='wide', top=420):
        eid = f'{s.id}-{kid}'
        s.html.append(f'<div id="{eid}" class="clip kw {cls}" data-start="{s.L(t0)}" data-duration="{round(t1 - t0, 3)}" style="top:{top}px;z-index:{s.z + 20}"><span id="{eid}-in">{html.escape(text)}</span></div>')
        s.js.append(f'tl.fromTo("#{eid}-in",{{opacity:0,scale:0.85}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(1.7)"}},{s.L(t0)});')
        s.js.append(f'tl.to("#{eid}-in",{{opacity:0,duration:0.2,ease:"power2.in"}},{round(s.L(t1) - 0.22, 3)});')
    def tag(s, kid, text, t0, t1, x, y, warm=False):
        eid = f'{s.id}-{kid}'
        s.html.append(f'<div id="{eid}" class="clip tag{" warm" if warm else ""}" data-start="{s.L(t0)}" data-duration="{round(t1 - t0, 3)}" style="left:{x}px;top:{y}px;z-index:{s.z + 20}"><span id="{eid}-in">{html.escape(text)}</span></div>')
        s.js.append(f'tl.fromTo("#{eid}-in",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.3,ease:"power3.out"}},{s.L(t0)});')
    def raw(s, h): s.html.append(h)
    def anim(s, js): s.js.append(js)
    def write(s, outdir):
        fade = f'tl.fromTo("#{s.id}-wrap",{{opacity:0}},{{opacity:1,duration:{s.fade_in},ease:"sine.inOut"}},0);' if s.fade_in else ''
        under = (f'<div id="{s.id}-under" class="clip" data-start="0" data-duration="{s.fade_in + 0.05}" style="position:absolute;inset:0;z-index:0">{s.underlay}</div>') if s.underlay else ''
        doc = f'''<template>
<style>{BASE_CSS}</style>
<div id="root" data-composition-id="{s.id}" data-width="1080" data-height="1920">
{under}
<div id="{s.id}-wrap" style="position:absolute;inset:0;z-index:1">
{chr(10).join(s.html)}
</div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{fade}
{chr(10).join(s.js)}
window.__timelines["{s.id}"] = tl;
</script>
</template>
'''
        open(outdir / 'compositions' / f'{s.id}.html', 'w', encoding='utf-8').write(doc)

# ---------- diagram library (SVG drawn in code, animated with GSAP). Each returns inner html; anims added to the scene.
GLOW = '<filter id="{id}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
def svg_wrap(sid, body, defs=''):
    return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{GLOW.format(id=sid + "-g")}{defs}</defs>{body}</svg>'

def radar_icon(x, y, s=1.0, col='#62A6E2'):
    # simple radar tower: mast + dome
    return (f'<g transform="translate({x},{y}) scale({s})"><rect x="-14" y="0" width="28" height="210" fill="#1B3558"/>'
            f'<path d="M -90 0 A 90 90 0 0 1 90 0 Z" fill="#E8EEF6" stroke="{col}" stroke-width="5"/>'
            f'<line x1="-90" y1="0" x2="90" y2="0" stroke="{col}" stroke-width="5"/></g>')

def diag(sc, sid, kind, t0, t1, P, txt):
    g = sid + '-g'; D = t1 - t0; L0 = sc.L(t0); A = sc.anim
    if kind == 'wave':
        pts = ' '.join(f'{x},{900 + 90 * __import__("math").sin(x / 60)}' for x in range(-200, 1300, 10))
        body = f'<polyline id="{sid}-w" points="{pts}" fill="none" stroke="#7FE7FF" stroke-width="10" filter="url(#{g})" stroke-dasharray="60 0"/>'
        A(f'tl.fromTo("#{sid}-w",{{x:-377}},{{x:0,duration:{round(D, 3)},ease:"none"}},{L0});')
        return svg_wrap(sid, body)
    if kind == 'pulses':
        x, y = P.get('x', 540), P.get('y', 1100)
        arcs = ''.join(f'<path id="{sid}-a{i}" d="M {x - 120} {y - 40} A 140 140 0 0 1 {x + 120} {y - 40}" fill="none" stroke="#7FE7FF" stroke-width="12" stroke-linecap="round" filter="url(#{g})" opacity="0"/>' for i in range(5))
        for i in range(5):
            A(f'tl.fromTo("#{sid}-a{i}",{{opacity:0.95,scale:0.4,svgOrigin:"{x} {y}"}},{{opacity:0,scale:5,svgOrigin:"{x} {y}",duration:1.6,ease:"none",repeat:{max(0, int(D / 1.6) - 1)}}},{round(L0 + i * 0.32, 3)});')
        return svg_wrap(sid, arcs + (radar_icon(x, y, 1.0) if P.get('icon', True) else ''))
    if kind == 'bounce':
        # radar left, small cloud droplets middle, big raindrops right; pulse goes out, echo comes back from big drops
        rx, ry = 150, 1040
        small = ''.join(f'<circle cx="{c[0]}" cy="{c[1]}" r="7" fill="#B9C7D8" opacity="0.8"/>' for c in [(430, 820), (480, 950), (520, 880), (450, 1060), (560, 1000), (500, 1150), (590, 860)])
        big = ''.join(f'<path d="M {c[0]} {c[1] - 34} C {c[0] + 22} {c[1] - 6}, {c[0] + 22} {c[1] + 22}, {c[0]} {c[1] + 22} C {c[0] - 22} {c[1] + 22}, {c[0] - 22} {c[1] - 6}, {c[0]} {c[1] - 34} Z" fill="#62A6E2" stroke="#BFE6FF" stroke-width="3"/>' for c in [(840, 840), (900, 960), (820, 1080), (930, 1150), (870, 760)])
        out = f'<path id="{sid}-out" d="M {rx + 60} 820 A 260 260 0 0 1 {rx + 60} 1260" fill="none" stroke="#7FE7FF" stroke-width="12" filter="url(#{g})" opacity="0"/>'
        back = f'<path id="{sid}-back" d="M 780 820 A 260 260 0 0 0 780 1260" fill="none" stroke="#F57700" stroke-width="12" filter="url(#{g})" opacity="0"/>'
        body = small + big + out + back + radar_icon(rx, ry, 0.8)
        loop = 2.2; n = max(1, int(D / loop))
        for k in range(n):
            t = round(L0 + 0.2 + k * loop, 3)
            A(f'tl.fromTo("#{sid}-out",{{opacity:1,x:0}},{{opacity:1,x:600,duration:1.0,ease:"none"}},{t});')
            A(f'tl.set("#{sid}-out",{{opacity:0}},{round(t + 1.0, 3)});')
            A(f'tl.fromTo("#{sid}-back",{{opacity:1,x:0}},{{opacity:1,x:-560,duration:1.0,ease:"none"}},{round(t + 1.0, 3)});')
            A(f'tl.set("#{sid}-back",{{opacity:0}},{round(t + 2.0, 3)});')
        return svg_wrap(sid, body)
    if kind == 'distance':
        body = (radar_icon(160, 1180, 0.7) + '<path d="M 760 760 C 700 700, 820 640, 880 700 C 940 650, 1040 700, 1010 770 C 1060 800, 1020 860, 960 850 L 780 850 C 720 850, 700 790, 760 760 Z" fill="#9FB3C8"/>'
                + ''.join(f'<line x1="{x}" y1="870" x2="{x - 14}" y2="930" stroke="#62A6E2" stroke-width="5"/>' for x in range(790, 1000, 40))
                + f'<line id="{sid}-go" x1="220" y1="1100" x2="840" y2="900" stroke="#7FE7FF" stroke-width="10" stroke-dasharray="1" pathLength="1" stroke-dashoffset="1"/>'
                + f'<line id="{sid}-ret" x1="840" y1="930" x2="220" y2="1130" stroke="#F57700" stroke-width="10" stroke-dasharray="1" pathLength="1" stroke-dashoffset="1"/>')
        A(f'tl.fromTo("#{sid}-go",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.8,ease:"none"}},{round(L0 + 0.2, 3)});')
        A(f'tl.fromTo("#{sid}-ret",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.8,ease:"none"}},{round(L0 + 1.0, 3)});')
        return svg_wrap(sid, body)
    if kind == 'colorbar':
        rows = P['rows']; body = ''
        for i, (col, key) in enumerate(rows):
            y = 760 + i * 170
            body += f'<g id="{sid}-r{i}" opacity="0"><rect x="200" y="{y}" width="150" height="120" rx="18" fill="{col}"/><text x="400" y="{y + 82}" font-family="Montserrat" font-weight="700" font-size="60" fill="#FFFFFF">{html.escape(txt[key])}</text></g>'
        for i, at in enumerate(P['_ats']):
            A(f'tl.fromTo("#{sid}-r{i}",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:0.3,ease:"power3.out"}},{sc.L(at)});')
        return svg_wrap(sid, body)
    if kind == 'doppler':
        # moving source: circles emitted at successive positions -> bunched in front, spread behind
        cx0, cy = 300, 960; body = ''
        for i in range(7):
            r = 60 + i * 70; x = cx0 + (6 - i) * 45
            body += f'<circle id="{sid}-c{i}" cx="{x}" cy="{cy}" r="{r}" fill="none" stroke="#7FE7FF" stroke-width="6" opacity="0"/>'
        body += f'<circle cx="{cx0 + 6 * 45 + 20}" cy="{cy}" r="34" fill="#F57700" filter="url(#{g})"/>'
        for i in range(7):
            A(f'tl.fromTo("#{sid}-c{i}",{{opacity:0}},{{opacity:0.9,duration:0.25}},{round(L0 + 0.15 + (6 - i) * 0.18, 3)});')
        return svg_wrap(sid, body)
    if kind == 'couplet':
        cx, cy = 540, 900
        body = (f'<ellipse cx="{cx - 130}" cy="{cy}" rx="150" ry="230" fill="#21C55D" opacity="0.85" filter="url(#{g})"/>'
                f'<ellipse cx="{cx + 130}" cy="{cy}" rx="150" ry="230" fill="#E5322D" opacity="0.85" filter="url(#{g})"/>'
                f'<g id="{sid}-rot"><path d="M {cx} {cy - 330} A 330 330 0 0 1 {cx + 330} {cy}" fill="none" stroke="#FFFFFF" stroke-width="12"/>'
                f'<path d="M {cx + 330} {cy - 40} L {cx + 330} {cy + 30} L {cx + 280} {cy - 10} Z" fill="#FFFFFF"/>'
                f'<path d="M {cx} {cy + 330} A 330 330 0 0 1 {cx - 330} {cy}" fill="none" stroke="#FFFFFF" stroke-width="12"/>'
                f'<path d="M {cx - 330} {cy + 40} L {cx - 330} {cy - 30} L {cx - 280} {cy + 10} Z" fill="#FFFFFF"/></g>')
        A(f'tl.fromTo("#{sid}-rot",{{rotation:0,svgOrigin:"{cx} {cy}"}},{{rotation:200,svgOrigin:"{cx} {cy}",duration:{round(D, 3)},ease:"none"}},{L0});')
        return svg_wrap(sid, body)
    raise SystemExit(f'unknown diagram {kind}')

def compose(vd, lang):
    vd = Path(vd); S = jload(vd / 'spec.json'); T = jload(vd / 'audio' / lang / 'timing.json')
    LS = {l['id']: l for l in T['lines']}
    def R(ref):  # "L05", "L05:2", "L05:2+0.3", "L05-0.2", "end"
        if isinstance(ref, (int, float)): return float(ref)
        m = re.match(r'(L\d+|end)(?::(\d+))?([+-][\d.]+)?$', ref)
        lid, ci, off = m.group(1), m.group(2), float(m.group(3) or 0)
        if lid == 'end': base = END_START
        elif ci is None: base = LS[lid]['start']
        else: base = [c for c in T['captions'] if c['line'] == lid][int(ci)]['start']
        return round(base + off, 3)
    def tx(v): return v[lang] if isinstance(v, dict) else v
    END_START = round(T['voice_end'] + 0.22, 3); TOTAL = round(END_START + 1.35, 3)
    out = vd / f'build_{lang}'; (out / 'compositions').mkdir(parents=True, exist_ok=True)
    (out / 'assets' / 'plates').mkdir(parents=True, exist_ok=True); (out / 'assets' / 'brand').mkdir(parents=True, exist_ok=True); (out / 'assets' / 'audio').mkdir(parents=True, exist_ok=True)
    for f in (vd / 'plates').iterdir(): shutil.copy(f, out / 'assets' / 'plates' / f.name)
    shutil.copy(KIT / 'brand' / 'endcard.mp4', out / 'assets' / 'brand' / 'endcard.mp4')
    for f in ['hyperframes.json', 'package.json']:
        if (KIT / 'brand' / f).exists(): shutil.copy(KIT / 'brand' / f, out / f)
    json.dump({'id': f'{S["slug"]}-{lang}', 'name': f'{S["slug"]}-{lang}'}, open(out / 'meta.json', 'w'))
    secs = S['sections']; scenes = []; pops = []; whooshes = []; booms = []
    # ---- thumbnail card 0 - 0.55
    th = S['thumb']; sc = Scene('thumb', 0.0, 0.55)
    sc.raw(f'<img class="plate" src="assets/plates/{th["plate"]}.jpg" alt="" style="z-index:0">')
    for c in th.get('cuts', []): sc.raw(f'<img class="cut" src="assets/plates/{c["png"]}.png" style="left:{c["x"]}px;top:{c["y"]}px;width:{c["w"]}px;z-index:2" alt="">')
    sc.raw('<img class="cut" src="assets/plates/seal.png" style="left:860px;top:80px;width:150px;z-index:4" alt="">')
    TT = 'font-family:Montserrat,sans-serif;font-weight:800;paint-order:stroke fill;-webkit-text-stroke:10px #6B1000;text-shadow:0 0 24px rgba(239,136,10,.6)'
    h1, h2 = tx(th['line1']), tx(th['line2']); sub = tx(th['sub'])
    sc.raw(f'<div style="position:absolute;left:30px;top:290px;width:1020px;text-align:center;z-index:5;transform:skewX(-6deg)"><div style="{TT};font-size:{th.get("size1", 140)}px;line-height:1.0;color:#FFFFFF;text-transform:uppercase">{html.escape(h1)}</div><div style="{TT};font-size:{th.get("size2", 88)}px;line-height:1.05;color:#FBE414;text-transform:uppercase">{html.escape(h2)}</div></div>')
    sc.raw(f'<div style="position:absolute;left:30px;top:1560px;width:1020px;text-align:center;z-index:5;transform:skewX(-6deg)"><div style="{TT};font-size:66px;line-height:1.05;color:#FBE414">{html.escape(sub)}</div></div>')
    scenes.append((sc, 0.0, 0.55, 20))
    # ---- sections
    starts = [R(s['at']) if i else 0.40 for i, s in enumerate(secs)]
    for i, s in enumerate(secs):
        a = starts[i]; b = starts[i + 1] if i + 1 < len(secs) else END_START
        dis = s.get('dissolve', False) and i > 0
        a0 = round(a - 0.5, 3) if dis else a
        under = ''
        if dis:
            prev = secs[i - 1]['shots'][-1]
            if prev.get('plate'): under += f'<img class="plate" src="assets/plates/{prev["plate"]}.jpg" alt="">'
            if prev.get('cut'): c = prev['cut']; under += f'<img class="cut" src="assets/plates/{c["png"]}.png" alt="" style="left:{c["x"]}px;top:{c["y"]}px;width:{c["w"]}px">'
            whooshes.append(a)
        sc = Scene(s['id'], a0, b, fade_in=1.0 if dis else 0.0, underlay=under)
        shots = s['shots']; sts = [a0] + [R(sh['at']) for sh in shots[1:]]
        for j, sh in enumerate(shots):
            t0 = sts[j]; t1 = sts[j + 1] if j + 1 < len(shots) else b
            inner = ''
            if sh.get('cut'):
                c = sh['cut']; cid = f'{s["id"]}-{sh["name"]}-cut'
                inner += f'<img id="{cid}" class="cut" src="assets/plates/{c["png"]}.png" style="left:{c["x"]}px;top:{c["y"]}px;width:{c["w"]}px" alt="">'
                if c.get('move'):
                    x0, y0, x1, y1, r0, r1 = (c['move'] + [0, 0])[:6]
                    sc.anim(f'tl.fromTo("#{cid}",{{x:{x0},y:{y0},rotation:{r0}}},{{x:{x1},y:{y1},rotation:{r1},duration:{round(t1 - t0, 3)},ease:"sine.inOut"}},{sc.L(t0)});')
            if sh.get('diagram'):
                d = dict(sh['diagram']); d['_ats'] = [R(x) for x in d.get('ats', [])]
                inner += diag(sc, f'{s["id"]}-{sh["name"]}-d', d['type'], t0, t1, d, {k: tx(v) for k, v in d.get('text', {}).items()})
            if sh.get('cta'):
                inner += ('<img id="cta-seal" class="cut" src="assets/plates/seal.png" style="left:300px;top:560px;width:480px" alt="">'
                          '<div id="cta-btn" style="position:absolute;left:250px;top:1120px;width:580px;height:130px;border-radius:65px;background:#E62117;box-shadow:0 0 40px rgba(230,33,23,.7);display:flex;align-items:center;justify-content:center;font-family:Montserrat,sans-serif;font-weight:800;font-size:58px;color:#FFFFFF">🔔 SUBSCRIBE</div>'
                          '<div id="cta-hand" style="position:absolute;left:700px;top:1190px;font-size:110px">👆</div>')
                ct = R(sh['cta_at']) if sh.get('cta_at') else t0 + 0.8
                sc.anim(f'tl.fromTo("#cta-seal",{{scale:0.6,opacity:0,rotation:-20}},{{scale:1,opacity:1,rotation:0,duration:0.5,ease:"back.out(1.8)"}},{sc.L(t0)});')
                sc.anim(f'tl.fromTo("#cta-btn",{{scale:0.5,opacity:0}},{{scale:1,opacity:1,duration:0.4,ease:"back.out(2)"}},{sc.L(ct)});')
                sc.anim(f'tl.fromTo("#cta-hand",{{opacity:0,x:120,y:120}},{{opacity:1,x:0,y:0,duration:0.4,ease:"power3.out"}},{round(sc.L(ct) + 0.4, 3)});')
                sc.anim(f'tl.to("#cta-btn",{{scale:0.92,duration:0.12,yoyo:true,repeat:1}},{round(sc.L(ct) + 0.85, 3)});')
                sc.anim(f'tl.set("#cta-btn",{{background:"#3A3A3A"}},{round(sc.L(ct) + 1.1, 3)});')
            sc.shot(sh['name'], t0, t1, sh.get('plate'), push=tuple(sh['push']) if 'push' in sh else (1.0, 1.08), inner=inner)
            if sh.get('flash'):
                sc.raw(f'<div id="{s["id"]}-flash" class="clip flash" data-start="{sc.L(t0)}" data-duration="0.3" style="z-index:90"></div>')
                sc.anim(f'tl.fromTo("#{s["id"]}-flash",{{opacity:1}},{{opacity:0,duration:0.28,ease:"power2.out"}},{sc.L(t0)});'); booms.append(t0)
            if sh.get('streak'):
                sc.raw(f'<div id="{s["id"]}-sw" class="clip" data-start="{sc.L(t0)}" data-duration="0.5" style="position:absolute;inset:0;z-index:80"><div id="{s["id"]}-streak" class="streak" style="top:900px"></div></div>')
                sc.anim(f'tl.fromTo("#{s["id"]}-streak",{{opacity:1,scaleX:0.2}},{{opacity:0,scaleX:1.2,duration:0.45,ease:"power2.out"}},{sc.L(t0)});'); booms.append(t0)
            for k, kwd in enumerate(sh.get('kw', [])):
                k0 = R(kwd['at']); k1 = R(kwd['until']) if kwd.get('until') else t1 - 0.05
                sc.kw(f'{sh["name"]}-k{k}', tx(kwd['text']), k0, k1, kwd.get('cls', 'wide'), kwd.get('top', 420)); pops.append(k0)
            for k, tg in enumerate(sh.get('tags', [])):
                sc.tag(f'{sh["name"]}-t{k}', tx(tg['text']), R(tg['at']), R(tg['until']) if tg.get('until') else t1, tg['x'], tg['y'], tg.get('warm', False))
            if sh.get('data'):
                dd = sh['data']; d0 = R(dd['at']); nid = f'{s["id"]}-{sh["name"]}-num'
                sc.raw(f'<div id="{nid}-box" class="clip" data-start="{sc.L(d0)}" data-duration="{round(t1 - d0, 3)}" style="position:absolute;left:0;width:1080px;top:1225px;text-align:center;z-index:60;font-family:Montserrat,sans-serif;color:rgba(255,255,255,.92)"><span style="font-weight:700;font-size:64px">{html.escape(dd.get("prefix", ""))}</span><span id="{nid}" style="font-weight:700;font-size:64px">0</span><span style="font-weight:500;font-size:34px"> {html.escape(dd.get("unit", ""))}</span><span style="font-weight:500;font-size:28px"> {html.escape(tx(dd.get("label", "")))}</span></div>')
                sc.anim(f'(function(){{const o={{v:0}};tl.fromTo(o,{{v:0}},{{v:{dd["to"]},duration:0.6,ease:"power2.out",onUpdate:function(){{document.querySelector("#{nid}").textContent=Math.round(o.v);}}}},{sc.L(d0)});}})();')
                pops.append(d0)
        scenes.append((sc, a0, b, 2 + i))
    for sc, *_ in scenes: sc.write(out)
    # ---- captions
    caps = T['captions']; groups = []
    for i, c in enumerate(caps):
        st = max(0.45, c['start']); en = min(END_START, c['end'] if i < len(caps) - 1 else T['voice_end'] + 0.15)
        if en - st < 0.2: continue
        fs = 58 if len(c['text']) <= 27 else (52 if len(c['text']) <= 31 else 46)
        groups.append(f'<div id="cap-{i}" class="clip cap" data-start="{round(st, 3)}" data-duration="{round(en - st, 3)}"><div class="bar"><span style="font-size:{fs}px">{html.escape(c["text"])}</span></div></div>')
    open(out / 'compositions' / 'captions.html', 'w', encoding='utf-8').write(f'''<template>
<style>
#root{{position:absolute;inset:0}}
.cap{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
.bar{{position:absolute;left:0;top:1357px;width:1080px;box-sizing:border-box;padding:19px 60px 13px;background:#151F31;text-align:center}}
.bar span{{font-family:Montserrat,sans-serif;font-weight:600;line-height:0.92;color:#FFFFFF;white-space:nowrap}}
</style>
<div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(groups)}
</div>
<script>window.__timelines["captions"] = gsap.timeline({{ paused: true }});</script>
</template>''')
    hosts = ''.join(f'<div id="{sc.id}" data-composition-id="{sc.id}" data-composition-src="compositions/{sc.id}.html" data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="{z}" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:{z}"></div>\n' for sc, a, b, z in scenes)
    open(out / 'index.html', 'w', encoding='utf-8').write(f'''<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(S["name"])} {lang} - Merit Mantra</title>
<style>html,body{{margin:0;background:#03060E}}</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920" data-fps="30">
<div id="bgfill" style="position:absolute;inset:0;background:#03060E;z-index:0"></div>
{hosts}<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{END_START}" data-track-index="30" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:30"></div>
<video id="endcard" class="clip" src="assets/brand/endcard.mp4" data-start="{END_START}" data-duration="1.35" data-media-start="0.45" data-track-index="40" muted playsinline style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;z-index:40"></video>
<audio id="mix" class="clip" src="assets/audio/final_mix.wav" data-start="0" data-duration="{TOTAL}" data-track-index="50" data-volume="1"></audio>
</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
</body></html>''')
    payoff = R(S.get('payoff', 'end'))
    mus = [{'track': m['track'], 'at': R(m['at']) if m['at'] != 'L01' else 0.0, 'gain': m['gain']} for m in S['music']]
    json.dump({'pops': sorted(pops), 'whooshes': whooshes, 'booms': sorted(set(booms)), 'riser_to': payoff, 'music': mus,
               'voice_end': T['voice_end'], 'end_start': END_START, 'total': TOTAL}, open(out / 'cues.json', 'w'), indent=1)
    print(lang, 'composed', len(scenes), 'scenes,', len(groups), 'captions, total', TOTAL)

# =====================================================================================  MIX
def mix(vd, lang):
    import numpy as np
    vd = Path(vd); out = vd / f'build_{lang}'; C = jload(out / 'cues.json'); KA = KIT / 'audio'
    SR = 48000; T = C['total']; N = int(T * SR)
    def load(f, ch=2):
        x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
        return x.reshape(-1, ch).copy()
    def lufs(x):
        p = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', str(x.shape[1]), '-i', '-', '-af', 'ebur128', '-f', 'null', '-'], input=x.astype(np.float32).tobytes(), capture_output=True)
        return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', p.stderr.decode())[-1])
    db = lambda g: 10 ** (g / 20)
    mixed = np.zeros((N, 2), np.float32)
    vp = out / 'voice_proc.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(vd / 'audio' / lang / 'narration.wav'), '-af', 'highpass=f=80,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,alimiter=limit=0.9', '-ar', str(SR), '-ac', '2', str(vp)], check=True)
    v = load(vp); v *= db(-16 - lufs(v)); mixed[:min(N, len(v))] += v[:N]; VL = -16.0
    def place(x, t, g=1.0):
        s = int(round(t * SR))
        if s < 0: x = x[-s:]; s = 0
        e = min(N, s + len(x)); mixed[s:e] += x[:e - s] * g
    def fade(x, fi=0.0, fo=0.0):
        x = x.copy(); n = len(x)
        if fi > 0: k = min(n, int(fi * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
        if fo > 0: k = min(n, int(fo * SR)); x[n - k:] *= np.linspace(1, 0, k)[:, None]
        return x
    M = C['music']; mus = np.zeros((N, 2), np.float32)
    for i, m in enumerate(M):
        a = m['at'] if i == 0 else m['at'] - 1.0; b = M[i + 1]['at'] + 0.5 if i + 1 < len(M) else T
        x = load(KA / f'{m["track"]}.wav'); x *= db(VL + m['gain'] - lufs(x))
        need = int((b - a) * SR)
        while len(x) < need: x = np.concatenate([x, x])
        x = fade(x[:need], 0 if i == 0 else 1.5, 1.5 if i + 1 < len(M) else 0.6)
        s = int(a * SR); mus[s:s + len(x)] += x[:N - s]
    for t in C['booms']:
        s = int((t - 0.02) * SR); k = min(int(0.35 * SR), N - s)
        if k > 0: env = np.ones(k); m1 = int(0.1 * SR); env[:m1] = db(-6); env[m1:] = np.linspace(db(-6), 1, k - m1); mus[s:s + k] *= env[:, None]
    mixed += mus
    pk = lambda x, p: x * db(p) / max(1e-6, np.abs(x).max())
    pop = load(KA / 'sfx_002.mp3'); whoosh = load(KA / 'sfx_001.mp3'); impact = load(KA / 'sfx_003.mp3'); boom = load(KA / 'sfx_004.mp3'); riser = load(KA / 'sfx_005.mp3')
    big = C['whooshes'] + C['booms']; pops = []
    for t in C['pops']:
        if (not pops or t - pops[-1] >= 5.5) and all(abs(t - b) > 1.5 for b in big): pops.append(t)
    for t in pops: place(pk(pop, -14), t - 0.12)
    place(pk(impact, -15), 0.45 - 0.75)
    for t in C['whooshes']: place(pk(fade(whoosh, 0, 0.8), -18), t - 0.63)
    for t in C['booms']: place(pk(boom, -12), t - 0.04)
    place(fade(pk(riser, -22), 1.5, 0.05)[:int(10 * SR)], C['riser_to'] - 10.0)
    mixed[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))[:, None]
    f32 = out / 'mix.f32'; mixed.astype(np.float32).tofile(f32)
    p = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(f32), '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}') + 1])
    af = f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(f32), '-af', af, '-ar', '48000', '-c:a', 'pcm_s16le', str(out / 'assets' / 'audio' / 'final_mix.wav')], check=True)
    f32.unlink(); vp.unlink()
    print(lang, 'mixed; pops at', pops)

# =====================================================================================  RENDER + EXPORT
def export_dir(S, lang):
    base = ROOT / 'export' / f'{datetime.date.today().isoformat()}_{S["name"]}_{LANGNAME.get(lang, lang)}'
    d = base; n = 2
    while d.exists() and (d / '.done').exists(): d = Path(f'{base}-{n}'); n += 1
    d.mkdir(parents=True, exist_ok=True); return d

def render(vd, lang):
    vd = Path(vd); S = jload(vd / 'spec.json'); out = vd / f'build_{lang}'
    env = dict(os.environ, CI='1', HEYGEN_NO_ANALYTICS='1')
    (out / 'renders').mkdir(exist_ok=True)
    subprocess.run('npx --yes hyperframes@0.9.5 render --quality delivery -o renders/video.mp4', shell=True, cwd=out, env=env, stdin=subprocess.DEVNULL)
    d = export_dir(S, lang); stem = f'Merit-Mantra_{S["name"]}_{LANGNAME.get(lang, lang)}'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out / 'renders' / 'video.mp4'), '-i', str(out / 'assets' / 'audio' / 'final_mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-vf', 'scale=2160:3840:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-af', 'alimiter=limit=0.84:level=false:attack=1:release=50',
                    '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', '-shortest', str(d / f'{stem}.mp4')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.2', '-i', str(out / 'renders' / 'video.mp4'), '-frames:v', '1', '-q:v', '2', str(d / f'{stem}_thumbnail.jpg')], check=True)
    m = S.get('meta', {}).get(lang)
    if m:
        open(d / f'{stem}_YouTube.txt', 'w', encoding='utf-8').write(f"{m['title']}\n\n{m['description']}\n\n{m['hashtags']}\n")
        if m.get('instagram'): open(d / f'{stem}_Instagram.txt', 'w', encoding='utf-8').write(m['instagram'] + '\n')
    (d / '.done').write_text('ok')
    print(lang, 'exported ->', d)

def sheet(vd):
    from PIL import Image, ImageDraw
    vd = Path(vd); A = jload(vd / 'media' / 'assets.json')
    Wd = Image.new('RGB', (1500, 1000 if len(A) <= 10 else 1500), (70, 70, 70)); d = ImageDraw.Draw(Wd)
    for k, (key, p) in enumerate(A.items()):
        i = Image.open(vd / p); sz = i.size; i = i.convert('RGBA'); bg = Image.new('RGBA', i.size, (70, 70, 70, 255)); bg.alpha_composite(i)
        i = bg.convert('RGB'); i.thumbnail((290, 440)); x = (k % 5) * 300; y = (k // 5) * 500
        Wd.paste(i, (x, y + 20)); d.text((x + 3, y + 3), f'{key} {sz[0]}x{sz[1]} {"PNG" if str(p).endswith(".png") else ""}', fill='yellow')
    Wd.save(vd / 'media' / 'sheet.jpg'); print('sheet ->', vd / 'media' / 'sheet.jpg')

if __name__ == '__main__':
    cmd, vd = sys.argv[1], sys.argv[2]
    if cmd == 'sheet': sheet(vd)
    elif cmd == 'plates': plates(vd)
    elif cmd == 'compose': compose(vd, sys.argv[3])
    elif cmd == 'mix': mix(vd, sys.argv[3])
    elif cmd == 'render': render(vd, sys.argv[3])
    elif cmd == 'all':
        plates(vd)
        for lang in jload(Path(vd) / 'spec.json')['langs']:
            compose(vd, lang); mix(vd, lang); render(vd, lang)
