# Merit Mantra portable pipeline - no Claude needed.
#   py -3.12 pipeline\auto.py make  [inbox\topic.txt]   topic -> script -> video  (newest inbox .txt when no file is given)
#   py -3.12 pipeline\auto.py write [inbox\topic.txt]   topic -> videos\<slug>\script.json only (to read or edit it first)
#   py -3.12 pipeline\auto.py build <slug>              script.json -> spec -> voices -> images -> render -> export
# Output: export\<date>_<Name>_Hinglish\ and export\<date>_<Name>_English\ (video, thumbnail, YouTube text, Instagram text)
import json, os, re, shutil, subprocess, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
ENGINE = ROOT / 'pipeline' / 'engine'
CFG = json.load(open(ROOT / 'config' / 'settings.json', encoding='utf-8'))
LOG = None

def log(*a):
    msg = ' '.join(str(x) for x in a); print(msg, flush=True)
    if LOG: LOG.write(msg + '\n'); LOG.flush()

def run(args, cwd=ROOT, check=True, live=False):
    log('$', ' '.join(str(a) for a in args))
    if live:   # show progress as it happens (voice, images, render)
        r = subprocess.run([str(a) for a in args], cwd=cwd, text=True, encoding='utf-8', errors='replace')
    else:
        r = subprocess.run([str(a) for a in args], cwd=cwd, text=True, encoding='utf-8', errors='replace', capture_output=True)
        if r.stdout: log(r.stdout[-4000:])
        if r.stderr: log(r.stderr[-2000:])
    if check and r.returncode: raise SystemExit(f'Step failed: {" ".join(str(a) for a in args)}\nSee the messages above (and videos\\<slug>\\auto_log.txt).')
    return r

def slugify(s): return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')[:40] or 'video'

def pick_topic(arg):
    inbox = ROOT / 'inbox'; inbox.mkdir(exist_ok=True); (inbox / 'done').mkdir(exist_ok=True)
    if arg: return Path(arg)
    cands = sorted([p for p in inbox.glob('*.txt') if p.name != 'TEMPLATE.txt'], key=lambda p: p.stat().st_mtime)
    if not cands: raise SystemExit('Put a topic .txt file in the inbox folder first (copy inbox\\TEMPLATE.txt).')
    return cands[-1]

def open_log(vd):
    global LOG
    LOG = open(vd / 'auto_log.txt', 'a', encoding='utf-8'); log(f'=== {datetime.datetime.now():%Y-%m-%d %H:%M}  {vd.name}')

def write_script(src):
    text = src.read_text(encoding='utf-8')
    m = re.search(r'(?im)^\s*topic\s*:\s*(.+)$', text) or re.search(r'(?im)^\s*title\s*:\s*(.+)$', text)
    slug = slugify(m.group(1) if m else src.stem)
    vd = ROOT / 'videos' / slug; vd.mkdir(parents=True, exist_ok=True); open_log(vd)
    shutil.copy(src, vd / 'input.txt')
    if (vd / 'script.json').exists():
        log(f'script.json already exists for {slug} - using it (delete it to write a new one).')
    elif CFG.get('script_writer', 'sarvam') == 'sarvam':
        run([PY, ROOT / 'pipeline' / 'writer.py', vd / 'input.txt', vd], live=True)
    else:
        raise SystemExit(f'script_writer is "manual" in config\\settings.json: write videos\\{slug}\\script.json yourself '
                         f'(copy examples\\radar-rain.script.json), then run BUILD_VIDEO.cmd {slug}')
    return vd

def build(vd):
    if not LOG: open_log(vd)
    if not (vd / 'script.json').exists(): raise SystemExit(f'No script.json in {vd} - write one first (see GUIDE.md).')
    run([PY, ROOT / 'pipeline' / 'layout.py', vd])
    run([PY, ENGINE / 'mm_check.py', vd])
    S = json.load(open(vd / 'spec.json', encoding='utf-8'))
    for lg in S['langs']:      # voice lines are bought once; timing is redone every run (free) so caption edits apply
        lines_dir = vd / 'audio' / lg / 'lines'
        if not all((lines_dir / f"{l['id']}.wav").exists() for l in S['lines']):
            run([PY, ENGINE / 'mm_audio.py', 'voice', vd, lg], cwd=vd, live=True)
        run([PY, ENGINE / 'mm_audio.py', 'narrate', vd, lg], cwd=vd)
    run([PY, ENGINE / 'mm_audio.py', 'assets', vd], cwd=vd, live=True)   # free stock images + house music/SFX
    run([PY, ROOT / 'pipeline' / 'layout.py', vd])            # re-layout now that the image shapes are known
    run([PY, ENGINE / 'mm_check.py', vd])
    run([PY, ENGINE / 'mm_build.py', 'sheet', vd], cwd=vd)
    if CFG.get('review_images', True) and sys.stdin.isatty() and not os.environ.get('MM_NO_REVIEW'):
        os.startfile(vd / 'media' / 'sheet.jpg')
        log('\nLook at the images that opened. To swap one: change its search phrase in videos\\%s\\script.json ("images"),' % vd.name)
        log('delete its line from videos\\%s\\media\\assets.json, close this window and run BUILD_VIDEO.cmd %s again.' % (vd.name, vd.name))
        try: input('If they look fine, press Enter to make the video... ')
        except EOFError: pass          # no keyboard attached (scheduled/unattended run): carry on
    run([PY, ENGINE / 'mm_build.py', 'all', vd], cwd=vd, live=True)  # plates, compose, mix, render, export
    log('=== DONE. Your videos are in the export folder.')

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'make'
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'build':
        if not arg: raise SystemExit('Usage: BUILD_VIDEO.cmd <slug>   (the folder name inside videos\\)')
        build(ROOT / 'videos' / arg)
    elif cmd == 'write':
        vd = write_script(pick_topic(arg)); log(f'\nScript written: videos\\{vd.name}\\script.json  ->  check it, then run BUILD_VIDEO.cmd {vd.name}')
    else:
        src = pick_topic(arg); vd = write_script(src); build(vd)
        if src.parent == ROOT / 'inbox': shutil.move(str(src), str(ROOT / 'inbox' / 'done' / src.name))

if __name__ == '__main__':
    main()
