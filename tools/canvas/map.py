# S1 · the map: every screen, what can be pressed on it, and where each press leads.
# Written from the click audit (tools/audit.cjs -> audit.json) and rows.py. Run tools/refresh-canvas.sh rather than this file alone.
import sys, os, json, re, html as H
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build import *
from rows import ROWS, GROUPS, code_of

AUD = {o['file'][:-8]: o for o in json.load(open(os.path.join(HERE, 'audit.json'))) if 'error' not in o}
CODE, NAME, KIND, ORDER, GROUP = {}, {}, {}, [], {}
for key, rtitle, items in ROWS:
    for stem, title, w, kind in items:
        c, n = title.split(' · ', 1)
        CODE[stem] = c; NAME[stem] = n; KIND[stem] = kind; ORDER.append(stem); GROUP[stem] = c[0]
PHONE_SRC = {'PhoneMain': 'Main', 'PhoneEvent': 'Event', 'PhoneSignIn': 'SignIn', 'PhoneMyHusna': 'MyHusna', 'PhoneEnroll2': 'Enroll2', 'PhoneEnroll5': 'Enroll5', 'PhoneChild': 'Child',
             'PhoneAbsence': 'AbsenceSheet', 'PhoneMessages': 'Messages', 'PhoneDonate': 'Donate', 'PhonePrayerBar': 'PrayerBar', 'PhoneEid': 'Eid', 'PhoneTeacher': 'TeacherHome', 'PhoneAttendance': 'OrgAttendance', 'PhoneOrgHome': 'OrgHome'}
TVNOTE = {'TvPair': 'Shown until someone types this code on D34.', 'TvMain': 'The clock and the countdown run.', 'TvSlides': 'Slides change by themselves.', 'TvFocus': 'The countdown runs.',
          'TvAdhan': 'Appears at the adhan time for as long as D35 says.', 'TvIqamah': 'Counts down to zero, then gives way to H7.', 'TvPrayer': 'Nothing moves until the prayer is over.',
          'TvFriday': 'From Thursday’s Maghrib until the last service ends.', 'TvRamadan': 'For the whole month, when D35 has it switched on.', 'TvMessage': 'Sent from D37 and cleared from there, or by its timer.',
          'TvOffline': 'What a screen shows by itself when the connection drops.', 'TvEid': 'From three days before an Eid prayer, when D39 has the notice switched on.', 'TvPortrait': 'The timetable layout on a screen turned on its side.'}
e = lambda s: H.escape(s, quote=True)
def short(s, n=44):
    s = ' '.join(s.split())
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'
def dest(href):
    if not href or href.startswith('#'): return None
    if re.match(r'https?:|mailto:|tel:', href): return 'EXT'
    return href.split('#')[0].replace('.dc.html', '')
def cd(stem): return '<span class="cd">%s</span>' % CODE[stem]
def to(stem): return '<a class="go2" href="%s.dc.html" aria-label="Open %s, %s">→ %s</a>' % (stem, CODE[stem], e(NAME[stem]), CODE[stem])

CHROME = ('header', 'sidebar', 'footer', 'workbar')
graph, main_in = {}, {}
for stem in ORDER:
    if stem == 'Map' or stem not in AUD or stem in PHONE_SRC: continue
    for l in AUD[stem]['links']:
        d = dest(l['href'])
        if d and d != 'EXT' and d != stem and d in CODE:
            graph.setdefault(stem, set()).add(d)
            if l['region'] not in CHROME: main_in.setdefault(d, []).append(stem)

def tweaks(stem):
    s = open(os.path.join(ROOT, stem + '.dc.html'), encoding='utf-8').read()
    m = re.search(r"data-props='([^']*)'", s)
    if not m: return []
    try: p = json.loads(H.unescape(m.group(1)))
    except Exception: return []
    out = []
    for k, v in p.items():
        if k.startswith('$') or not isinstance(v, dict) or v.get('editor') is None: continue
        label = re.sub(r'([a-z])([A-Z])', r'\1 \2', k).capitalize()
        if v.get('editor') == 'enum': out.append((label, ' · '.join(v.get('options', []))))
        elif v.get('editor') == 'boolean': out.append((label, 'off · on'))
    return out

def outcome(b):
    o = b['outcome']; cls = b.get('cls') or ''
    add = [a for a in b.get('added', []) if a and a != b['label']]
    if o == 'label-only': return 'becomes “%s”' % short(add[0], 40) if add else 'changes its label'
    if o in ('panel', 'small'):
        if 'Cancel' in add and b.get('nAdded', 0) > 2: return 'opens a form on this screen'
        good = [x for x in add if len(x) >= 8 and re.search(r'[A-Za-z]{3}', x) and not x.isupper()]
        return 'shows “%s”' % short(good[0], 40) if good else 'updates this screen'
    if ' off' in ' ' + cls: return 'waits until the form is complete'
    if b.get('pressed') == 'true' or re.search(r'(^| )on( |$)', cls): return 'already selected'
    return 'selects it'

def card(stem):
    kind = KIND[stem]; a = AUD.get(stem); rows = []
    head = '<a class="mh" href="%s.dc.html">%s<span>%s</span></a>' % (stem, cd(stem), e(NAME[stem]))
    if stem in PHONE_SRC:
        src = PHONE_SRC[stem]
        return '<article class="mc">%s<p class="mn">The same screen as %s, at 390px wide. Every press leads where it does there.</p></article>\n' % (head, to(src).replace('→ ', ''))
    if kind == 'tv':
        frm = sorted(set(main_in.get(stem, [])), key=ORDER.index)
        return '<article class="mc">%s<p class="mn">What the TV shows. Nothing to press: a TV has no mouse. %s Previewed from %s.</p></article>\n' % (head, TVNOTE.get(stem, ''), ' '.join(to(f).replace('→ ', '') for f in frm) or to({'TvMessage': 'OrgDisplayMessageSheet'}.get(stem, 'OrgDisplays')).replace('→ ', ''))
    if kind == 'doc':
        frm = sorted(set(main_in.get(stem, [])), key=ORDER.index)
        return '<article class="mc">%s<p class="mn">A printed page. Nothing to press. Opened from %s.</p></article>\n' % (head, ', '.join(to(f).replace('→ ', '') for f in frm) or 'the screens that offer the download')
    for label, opts in tweaks(stem):
        rows.append('<li class="mr tw"><span><b>Tweak · %s</b></span><span>%s</span></li>' % (e(label), e(opts)))
    if a:
        by = {}
        for l in a['links']:
            if l['region'] in CHROME: continue
            d = dest(l['href'])
            if d is None or d == stem: continue
            by.setdefault(d, [])
            lab = short(l['label'] or 'Link')
            if lab not in by[d]: by[d].append(lab)
        for d, labs in sorted(by.items(), key=lambda kv: (kv[0] == 'EXT', ORDER.index(kv[0]) if kv[0] in ORDER else 999)):
            text = ' · '.join(labs[:3]) + (' · and %d more' % (len(labs) - 3) if len(labs) > 3 else '')
            if d == 'EXT': rows.append('<li class="mr"><span>%s</span><span class="go2">↗ new tab</span></li>' % e(text))
            elif d in CODE: rows.append('<li class="mr"><span>%s</span>%s</li>' % (e(text), to(d)))
        seen = {}; run = []
        def flush():
            if not run: return
            labs = []
            for x in run:
                if x not in labs: labs.append(x)
            text = ' · '.join(labs[:5]) + (' · and %d more' % (len(labs) - 5) if len(labs) > 5 else '')
            rows.append('<li class="mr bt"><span>%s</span><span>%s</span></li>' % (e(text), 'switches what is shown' if len(labs) > 1 else 'turns it on or off'))
            run.clear()
        for b in a['buttons']:
            if b['region'] in CHROME: continue
            if b.get('pressed') is not None:
                run.append(short(re.sub(r'\s+\d+( of \d+)?$', '', b['label'] or 'Option'), 26)); continue
            flush()
            k = short(b['label'] or 'Button', 40)
            mv = re.match(r'Move .* up$', b['label'] or '')
            if mv: k = 'Move a slide up'
            if k in seen: seen[k][1] += 1; continue
            seen[k] = ['changes the order of the slides' if mv else outcome(b), 1, len(rows)]
            rows.append(None)
        flush()
        for k, (oc, n, i) in seen.items():
            rows[i] = '<li class="mr bt"><span>%s%s</span><span>%s</span></li>' % (e(k), ' ×%d' % n if n > 1 else '', e(oc))
    frm = [f for f in sorted(set(main_in.get(stem, [])), key=ORDER.index) if f != stem]
    if frm:
        shown = frm[:9]
        foot = 'Reached from ' + ' '.join(to(f).replace('→ ', '') for f in shown) + (' and %d more' % (len(frm) - 9) if len(frm) > 9 else '')
    else:
        foot = {'A': 'Reached from the header or footer of public pages', 'B': 'Reached from an email link', 'C': 'Reached from the member header or menu', 'D': 'Reached from the workspace sidebar',
                'E': 'Reached from the console sidebar', 'F': 'A reference board', 'G': 'Reached from the Menu button on a phone', 'H': 'Shown on a paired TV', 'S': 'A reference board'}[GROUP[stem]]
    return '<article class="mc">%s<ul>%s</ul><p class="mn">%s</p></article>\n' % (head, ''.join(rows), foot)

# ---------- journeys
class V(str): pass
def J(title, lede, steps):
    out = []; prev = None; bad = []
    for st in steps:
        if isinstance(st, V):
            out.append('<span class="jv">%s</span>' % e(st)); prev = None; continue
        if prev and st not in graph.get(prev, ()): bad.append((prev, st))
        if out and not out[-1].startswith('<span class="jv">'): out.append('<span class="ja" aria-hidden="true">→</span>')
        out.append('<a class="jc" href="%s.dc.html">%s%s</a>' % (st, cd(st), e(NAME[st])))
        prev = st
    if bad: print('JOURNEY BREAK', title, bad)
    return '<div class="stack g12"><div class="stack g4"><h3 class="t1">%s</h3><p class="sm mut">%s</p></div><div class="jr">%s</div></div>\n' % (title, lede, ''.join(out))

journeys = ''.join([
 J('A parent enrolls two children', 'From the home page to a confirmed place, without ever being charged by surprise.',
   ['Main', 'Program', 'Gate', 'SignUp', 'SignUpMember', 'Verify', 'Welcome', 'ChildForm', 'Family', V('then, from the program page'), 'Enroll1', 'Enroll2', 'Enroll3', 'Enroll4', 'Enroll5', V('card saved on Stripe’s page'), 'Enroll6', V('the school accepts, by email'), 'Child', 'AbsenceSheet']),
 J('An organization joins and goes live', 'A person applies, Husna verifies, and the setup guide walks the rest.',
   ['ForOrgs', 'OrgApply1', 'OrgApply2', 'OrgApply3', 'OrgApply4', 'OrgPending', V('Husna approves, by email'), 'OrgSetup', 'OrgProfileEdit', V('next step in the guide'), 'OrgFriday', V('next'), 'OrgEventEdit', V('next'), 'OrgInviteSheet', V('next'), 'OrgPayouts', V('connected on Stripe’s page'), 'OrgProgramEdit', V('published'), 'OrgProfile', V('all of it free; if it helped'), 'OrgCoffee']),
 J('A school runs a term', 'Applications in, classes filled, attendance taken, money settled, next term opened.',
   ['OrgPrograms', 'OrgProgramEdit', V('families apply'), 'OrgApplications', 'OrgDecisionSheet', V('accepted'), 'OrgRoster', 'OrgStudent', V('the teacher signs in'), 'TeacherHome', 'OrgAttendance', 'DocSignIn', V('during the term'), 'OrgAnnouncements', V('money'), 'OrgPayouts', 'OrgRefundSheet', V('term ends'), 'OrgPrograms', 'OrgNewTermSheet']),
 J('A neighbor finds an event, goes, and gives', 'Browsing needs no account. An RSVP does. Giving does not. None of it costs anything.',
   ['Main', 'Discover', 'Event', 'Gate', 'SignIn', 'Workspaces', 'MyHusna', V('from the event'), 'RsvpSheet', V('later'), 'Saved', V('the masjid they pray at most'), 'OrgProfile', V('made their home masjid, so its times top every page'), 'PrayerBar', V('giving'), 'OrgProfile', 'Donate', 'Stripe', V('paid, back on Husna'), 'DonateDone', V('and, if Husna helped'), 'Coffee']),
 J('Husna staff approve and oversee', 'Two-step sign-in, then every action written to the audit log.',
   ['Help', 'FounderSignIn', 'FounderCode', 'Founder', 'FounderApprovals', 'FounderDecisionSheet', V('or approved'), 'FounderOrgs', 'FounderOrg', 'FounderSuspendSheet', V('platform'), 'FounderPayments', V('then'), 'FounderSettings', 'FounderLegalSheet', V('day to day'), 'FounderSupport', V('and'), 'FounderAudit']),
 J('When things do not go to plan', 'Each of these starts from a message Husna sends, and ends with the person knowing where they stand.',
   ['Emails', 'Payments', 'Stripe', V('a waitlist place opens'), 'Emails', 'WaitlistOffer', V('an unexplained absence'), 'Emails', 'AbsenceSheet', V('the terms change'), 'Emails', 'TermsUpdate', V('a family moves away'), 'Child', 'WithdrawSheet', V('everything else'), 'States']),
 J('A masjid puts its prayer times on the wall', 'The times are set once. A screen is paired with a code, and from then on it follows the day with no one touching it.',
   ['OrgHome', 'OrgPrayerTimes', 'OrgDisplays', 'OrgDisplayPairSheet', 'TvPair', V('the code is typed, the screen is paired'), 'OrgDisplayEdit', 'OrgSlideSheet', V('on the TV, most of the day'), 'TvMain', V('at the adhan'), 'TvAdhan',
    V('five minutes before the iqamah'), 'TvIqamah', V('during the prayer'), 'TvPrayer', V('from Thursday evening'), 'TvFriday', V('something urgent'), 'OrgDisplays', 'OrgDisplayMessageSheet', V('shown on every screen'), 'TvMessage']),
 J('Fridays, and an Eid held somewhere else', 'One Jumu’ah or three, each with its khutbah and its iqamah. Eid gets its own page, because it is often not at the masjid at all.',
   ['OrgHome', 'OrgFriday', 'OrgServiceSheet', V('saved, and on the masjid’s page'), 'OrgProfile', V('Eid, planned months ahead'), 'OrgFriday', 'OrgEidEdit', V('published; the day is confirmed the evening before'), 'Emails', 'Eid', V('before the prayer'), 'Zakah', 'Stripe', V('meanwhile, on the TVs at the masjid'), 'TvEid']),
])

# ---------- navigation that is on every screen of a space
def chrome_block(title, stem, regions, note):
    seen = []; items = []
    for l in AUD[stem]['links']:
        d = dest(l['href'])
        if l['region'] in regions and d in CODE and (l['label'], d) not in seen:
            seen.append((l['label'], d)); items.append('<li class="mr"><span>%s</span>%s</li>' % (e(short(l['label'] or NAME[d], 34)), to(d)))
    return '<article class="mc"><p class="mh"><span>%s</span></p><ul>%s</ul><p class="mn">%s</p></article>\n' % (title, ''.join(items), note)
chrome = ''.join([
 chrome_block('Public header and footer', 'Main', ('header', 'footer'), 'On every public page. On a phone the links move into the visitor menu.'),
 chrome_block('Member header and footer', 'MyHusna', ('header', 'footer'), 'On every signed-in member page. On a phone the links move into the member menu.'),
 chrome_block('Workspace sidebar', 'OrgHome', ('sidebar', 'workbar'), 'On every workspace page. Each role sees only its own sections.'),
 chrome_block('Teacher’s sidebar', 'TeacherHome', ('sidebar', 'workbar'), 'What the Teacher role sees in place of the full sidebar.'),
 chrome_block('Founder console sidebar', 'Founder', ('sidebar', 'workbar'), 'On every console page, under the sand strip.'),
])

n_links = sum(len(AUD[s]['links']) for s in AUD if s not in PHONE_SRC and s != 'Map')
n_btn = sum(len(AUD[s]['buttons']) for s in AUD if s not in PHONE_SRC and s != 'Map')
n_screens = len(ORDER)
_em = open(os.path.join(ROOT, 'Emails.dc.html'), encoding='utf-8').read()
n_txt = _em[_em.index('>Text messages</h2>'):].count('<article'); n_email = _em.count('<article') - n_txt
NUM = {6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'}
N_J = journeys.count('<h3 class="t1">')
groups = []
for g, gname in GROUPS:
    stems = [s for s in ORDER if GROUP[s] == g and s != 'Map']
    if not stems: continue
    groups.append('<h2 class="mg"><span class="d4">%s · %s</span><span class="sm sub">%s</span></h2>\n%s' % (g, gname, '1 screen' if len(stems) == 1 else '%d screens' % len(stems), ''.join(card(s) for s in stems)))

MAPW = 3360
STYLE = '''
.mapcols{columns:332px;column-gap:16px}
.mc{break-inside:avoid;margin:0 0 16px;padding:12px 16px 12px;border:1px solid rgba(232,249,229,.13);border-radius:14px;background:#14201c}
.mc ul{margin:6px 0 0}
.mg{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;margin:20px 0 12px;padding-bottom:10px;border-bottom:1px solid #c8efa4;break-after:avoid;break-inside:avoid;color:#f3f0e7;font-weight:400}
.mh{display:flex;gap:10px;align-items:center;min-height:36px;margin:0;color:#f3f0e7;font:600 15px/1.3 'DM Sans',system-ui,sans-serif;text-decoration:none}
a.mh:hover span:last-child{text-decoration:underline}
.cd{flex:0 0 auto;display:inline-block;min-width:38px;padding:4px 7px;border-radius:7px;background:#22352d;color:#c8efa4;font:700 12px/1.2 'DM Sans',system-ui,sans-serif;text-align:center;font-variant-numeric:tabular-nums}
.mr{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:5px 0;border-top:1px solid rgba(232,249,229,.13);font-size:13px;line-height:1.4;color:#b4bfb7}
.mr>span:first-child{min-width:0}
.mr>span:last-child:not(:first-child){flex:0 1 46%;text-align:right;color:#8b9b93}
.mr.bt>span:first-child::before{content:'';display:inline-block;width:7px;height:7px;margin-right:8px;border-radius:2px;border:1.5px solid #8b9b93;vertical-align:1px}
.mr.tw{color:#f2c57c}.mr.tw>span:last-child{color:#f2c57c}
.go2{flex:0 0 auto;color:#c8efa4;font-weight:700;text-decoration:none;white-space:nowrap;font-variant-numeric:tabular-nums}
a.go2:hover{text-decoration:underline}
.mn{margin-top:8px;padding-top:8px;border-top:1px solid rgba(232,249,229,.13);font-size:12px;line-height:1.5;color:#8b9b93}
.mn .go2{font-weight:600}
.jr{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.jc{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:6px 12px 6px 6px;border:1px solid rgba(232,249,229,.26);border-radius:11px;background:#14201c;color:#f3f0e7;font:600 13px/1.2 'DM Sans',system-ui,sans-serif;text-decoration:none;white-space:nowrap}
.jc:hover{border-color:#c8efa4;color:#f3f0e7}
.ja{color:#8b9b93;font-size:16px}
.jv{padding:0 4px;color:#f2c57c;font:600 12px/1.3 'DM Sans',system-ui,sans-serif;white-space:nowrap}
.jv::after{content:' →';color:#8b9b93}
.wrap.mapwrap{width:calc(100% - 128px);max-width:none}
@media (max-width:720px){.wrap.mapwrap{width:calc(100% - 32px)}.jc,.jv{white-space:normal}.mr>span:last-child:not(:first-child){flex-basis:40%}}
'''
main = ('<section class="sec s"><div class="wrap stack g48 mapwrap">\n'
 '<div class="row between bottom g32"><div class="stack g12"><p class="eyebrow">Start here</p><h1 class="d2">Every screen, <em>every click.</em></h1>'
 '<p class="lede" style="max-width: 78ch">Each card is one screen on this canvas. It lists what can be pressed there and the screen that press opens. Press a code to go to that screen.</p></div>'
 '<div style="flex: 0 1 880px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px"><div class="stat"><p class="eyebrow q">Screens</p><b>%d</b><span>in %s groups</span></div><div class="stat"><p class="eyebrow q">Links</p><b>%s</b><span>each one leads somewhere</span></div>'
 '<div class="stat"><p class="eyebrow q">Buttons</p><b>%d</b><span>each one changes its screen</span></div><div class="stat"><p class="eyebrow q">Messages</p><b>%d</b><span>%d emails and %d texts, on F2</span></div></div></div>\n'
 '<div class="card row g24" style="padding: 14px 20px"><span class="eyebrow q">How to read a card</span><span class="sm mut"><span class="go2">→ C12</span>&nbsp; opens another screen</span>'
 '<span class="sm mut mr bt" style="border: 0; padding: 0; display: inline-flex"><span>A button</span></span><span class="sm mut">changes the screen it is on, and the line says how</span>'
 '<span class="sm" style="color: #f2c57c"><b>Tweak</b>&nbsp; a state you can switch from the canvas side panel</span><span class="sm mut"><span class="go2">↗</span>&nbsp; leaves Husna</span></div>\n'
 '<section class="stack g24"><div class="stack g8"><h2 class="d3">%s journeys, end to end</h2><p class="mut">Each chip is a screen; each arrow is a press you can make in Play. Amber words mark a step that happens somewhere else: an email, a decision by another person, a page on Stripe.</p></div>\n%s</section>\n<hr class="hr">\n'
 '<section class="stack g16"><div class="stack g8"><h2 class="d3">Every screen, and every press on it</h2><p class="mut">The first five cards are the navigation that sits on every screen of a space, so the cards after them list only what is particular to each screen.</p></div>'
 '<div class="mapcols"><h2 class="mg" style="margin-top: 0"><span class="d4">On every screen of a space</span></h2>\n%s%s</div></section>\n'
 '</div></section>\n') % (n_screens, NUM.get(len(GROUPS), str(len(GROUPS))), format(n_links, ','), n_btn, n_email + n_txt, n_email, n_txt, NUM.get(N_J, str(N_J)).capitalize(), journeys, chrome, ''.join(groups))

html = (head('Every screen and every click').replace('a{color:#c8efa4}a:hover{color:#dbf7c1}\n', 'a{color:#c8efa4}a:hover{color:#dbf7c1}\n' + STYLE.strip() + '\n')
        + '<div class="page">\n<header class="hdr"><div class="wrap mapwrap">\n<a class="brand" href="Main.dc.html" aria-label="Husna home">' + LOGO + 'husna<i>.</i><small>Map</small></a>\n'
        '<div class="row g8 push"><a class="btn" href="System.dc.html">Design system</a><a class="btn pri" href="Main.dc.html">Start at the home page →</a></div>\n</div></header>\n\n<main>\n' + main + '</main>\n</div>\n' + tail('', MAPW, 6000))
write('Map.dc.html', html)
print('screens', n_screens, 'links', n_links, 'buttons', n_btn)
