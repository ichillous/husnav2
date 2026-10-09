# Canvas layout from rows.py.
#   layout.py prep   -> make sure every screen in rows.py has an entry in canvas.json with its width (so tools/check.cjs measures it at that width)
#   layout.py        -> read heights.json (written by `node tools/check.cjs --heights`), then set every frame's size and position,
#                       the row titles, the notes beside the canvas, the order, and each file's $preview
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rows import ROWS
PROJ = os.path.join(HERE, '..', '..', 'project')
CJ = os.path.join(PROJ, 'canvas.json')
GAP, ROWGAP = 80, 440
USER_NOTE = ('note-uqkmha', 'OrgProgramEdit.dc.html', 871, 135)   # the user's sticky keeps its place relative to D9

def flags(kind):
    if kind in ('doc', 'phone'): return {}
    if kind in ('tv', 'strip'): return {'is_interactive': True}   # a fixed frame, like the TV itself; the clock runs in Play
    return {'expand': 'fill', 'is_interactive': True}

def frame_h(kind, natural):
    if kind == 'doc': return 1056
    if kind == 'tv': return 1920 if natural > 1500 else 1080
    if kind == 'strip': return 45   # the banner is one line: 44 plus its rule
    if kind == 'phone': return max(600, int(math.ceil(natural / 10.0) * 10))
    return max(600, int(math.ceil((natural + 20) / 20.0) * 20))

c = json.load(open(CJ, encoding='utf-8'))
mode = sys.argv[1] if len(sys.argv) > 1 else 'final'
files = [stem + '.dc.html' for _, _, items in ROWS for stem, _, _, _ in items]
on_disk = sorted(f for f in os.listdir(PROJ) if f.endswith('.dc.html'))
missing = [f for f in files if f not in on_disk]; extra = [f for f in on_disk if f not in files]
if missing or extra: print('WARNING missing files:', missing, 'files not in rows:', extra)
ROWS = [(k, t, [it for it in items if it[0] + '.dc.html' in on_disk]) for k, t, items in ROWS]
ROWS = [r for r in ROWS if r[2]]
files = [f for f in files if f in on_disk]

if mode == 'prep':
    for _, _, items in ROWS:
        for stem, title, w, kind in items:
            f = stem + '.dc.html'
            b = c['boards'].get(f) or {'x': 0, 'y': 0, 'h': 900}
            b['w'] = w
            c['boards'][f] = b
    for f in list(c['boards']):
        if f not in files: del c['boards'][f]
    c['order'] = files
    json.dump(c, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('prep ok:', len(files), 'boards')
    sys.exit(0)

raw = json.load(open(os.path.join(HERE, 'heights.json')))
old_d9 = dict(c['boards'].get(USER_NOTE[1], {}))
boards = {}; notes = c.get('notes', {}); y = 0
for key, rtitle, items in ROWS:
    x = 0; mh = 0
    roww = sum(w for _, _, w, _ in items) + GAP * (len(items) - 1)
    n = notes.get('t' + key) or {'kind': 'title1'}
    n.update({'x': 0, 'y': y - 300, 'text': rtitle, 'kind': 'title1', 'maxW': max(1440, min(roww, 6000))})
    n.pop('w', None)
    notes['t' + key] = n
    for stem, title, w, kind in items:
        f = stem + '.dc.html'
        h = frame_h(kind, raw[f])
        assert h <= 8000, (f, h)
        b = {'x': x, 'y': y, 'w': w, 'h': h, 'title': title}
        b.update(flags(kind))
        boards[f] = b
        x += w + GAP; mh = max(mh, h)
    y += mh + ROWGAP
# my two stickies sit to the left of the first rows
READ = ('How to read this canvas. Start with S1, the map: every screen, what can be pressed on it, and where each press leads. Then press Play on A1 and click through. '
        'Rows A to F are the screens by role, at desktop width. Row G shows the same screens on a phone. Row H is what a TV in the masjid shows: each frame is a real 1920 by 1080 screen, so press Play and choose Fit, and the clock and countdowns run. S2 is the design system. '
        'Public pages open signed out; the Viewer tweak on A2, A3, A5, A6 and A8 shows the signed-in member, and every other tweak is listed on the map in amber. '
        'Screens that show the term under way (the child’s page, attendance, rosters, tuition and payouts, the teacher’s workspace) are dated mid-November; everything else is Thursday, October 8, 2026. '
        'All organizations, people, prices and counts are fictional sample data.')
OPEN = ('Open decisions appear in [BRACKETS] on the screens. Yours to settle: the terms and privacy versions, dates and wording, which need counsel; '
        'review and support response times; the sender, support and alert addresses and the text-message number; how long records are kept; the company name and mailing address; which TV devices Husna tests and names, and the largest video a slide may carry.')
notes['sRead'] = dict(notes.get('sRead', {}), text=READ, w=640, x=-760, y=0)
notes['sOpen'] = dict(notes.get('sOpen', {}), text=OPEN, w=640, x=-760, y=1500, fill='orange')
# the user's sticky follows the artboard it was placed on
# the user's sticky about D9 moves off the reworked screen, to the free space under the small sheet beside it; my answer sits next to it
nid = USER_NOTE[0]; anchor = boards.get('UnsavedSheet.dc.html')
if nid in notes and anchor:
    notes[nid]['x'] = anchor['x']; notes[nid]['y'] = anchor['y'] + anchor['h'] + 120
    notes['sD9'] = {'text': 'Done on D9. Program setup is now two columns and about a third shorter. A save bar floats at the bottom of the window as soon as anything changes; it counts the changes and names the section they are in. The same bar is on Public profile, Create event and Add a child, and the step forms keep Back and Continue in view. Add a class moved to the end of the class list, and every settings row has one control in one column.',
                    'w': 400, 'x': anchor['x'] + 280, 'y': anchor['y'] + anchor['h'] + 120, 'fill': 'green'}
h1 = boards.get('TvPair.dc.html')
if h1:
    notes['sTV'] = dict(notes.get('sTV', {}), w=640, x=-760, y=h1['y'], fill='blue', text=(
        'New: TV displays. A masjid opens husna.app/tv on any screen with a browser, types the six-character code into its workspace (D34), and the screen follows the day by itself: '
        'the timetable or slides most of the day (H2 to H4), the adhan (H5), the countdown to the iqamah (H6), quiet during the prayer (H7), the Friday board from Thursday evening (H8), Ramadan (H9). '
        'The office can cover every screen with a message in seconds (D37, H10). If the connection drops the screen keeps the saved times for 30 days (H11). '
        'Times come from D32, Prayer times, which also feeds the public profile (A6). Each screen is set up on D35, where the preview is the real screen running. '
        'A school or nonprofit can pair a TV too; with no prayer times of its own, its screen shows slides, events and a clock.'))
notes['sFree'] = dict(notes.get('sFree', {}), w=640, x=-760, y=3000, fill='green', text=(
    'Husna is free. No plan, no platform fee, nothing taken from donations, tuition or payment links; the only charge anyone sees is Stripe’s own card processing, which goes to Stripe. '
    'In its place there is one quiet button, Buy the developer a coffee: for members and visitors in the footer, the phone menu and Account (A18), and for organizations at the foot of the workspace sidebar and in Settings (D38). '
    'It is one time, paid on Stripe’s page to Husna’s own account, and never interrupts anyone. The founder console shows what comes in on E12. '
    'Home masjid: a member chooses one masjid, from its page (A6), from Welcome (B9) or in Account (C17), and its adhan and iqamah times sit across the top of every page they open (C20). '
    'On a wide screen all five prayers are in view and only the countdown changes; on a phone, where they cannot fit, the line moves (G17). No home masjid, no banner. Only masjids have a Prayer times page (D32).'))
c['boards'] = boards; c['order'] = files; c['notes'] = notes
json.dump(c, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
changed = 0
for f, b in boards.items():
    p = os.path.join(PROJ, f); s = open(p, encoding='utf-8').read()
    m = re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}', s)
    assert m, f
    new = '"$preview":{"width":%d,"height":%d}' % (b['w'], b['h'])
    if m.group(0) != new:
        s = s.replace(m.group(0), new); open(p, 'w', encoding='utf-8').write(s); changed += 1
    hs = re.search(r'hint-size="390px,\d+px"', s)
    if hs:
        s2 = s.replace(hs.group(0), 'hint-size="390px,%dpx"' % b['h'])
        if s2 != s: open(p, 'w', encoding='utf-8').write(s2)
print('final ok:', len(boards), 'boards; $preview updated in', changed, 'files; canvas', max(b['x'] + b['w'] for b in boards.values()), 'x', max(b['y'] + b['h'] for b in boards.values()))
print('notes:', sorted(notes))
