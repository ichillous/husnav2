# Helpers for writing a .dc.html file from Python: the document head and tail, the shared icons, the workspace and
# console sidebars (copied from OrgHome and Founder so there is one source), and page and sheet skeletons.
# map.py uses the head, tail and write helpers. The other helpers are here for building new screens the same way.
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'project')
LOGO = '<svg viewBox="0 0 39 44" aria-hidden="true"><path d="M6 37V19C6 7 17 7 19.5 19V37M19.5 37V19C22 7 33 7 33 19V37M3 41h33"></path><circle cx="19.5" cy="6" r="2" fill="currentColor" stroke="none"></circle></svg>'
MENU = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"></path></svg>'
MSG = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 4v-4A2.5 2.5 0 0 1 4 13.5Z"></path></svg>'
BELL = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9a6 6 0 0 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9ZM10 20a2 2 0 0 0 4 0"></path></svg>'
X = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"></path></svg>'
PLUS = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"></path></svg>'
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Amiri&amp;family=DM+Sans:wght@400;500;600;700&amp;family=Instrument+Serif:ital@0;1&amp;display=swap" rel="stylesheet">'

def head(title, bg='#0b100f'):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>%s</title>\n<script src="./support.js"></script>\n'
            '<link rel="stylesheet" href="./husna.css">\n</head>\n<body>\n<x-dc>\n<helmet>\n%s\n<style>\nbody{margin:0;background:%s}\n'
            'a{color:#c8efa4}a:hover{color:#dbf7c1}\n</style>\n</helmet>\n') % (title, FONTS, bg)

def tail(js, w, h, props=None):
    p = dict(props or {}); p['$preview'] = {'width': w, 'height': h}
    pj = json.dumps(p, ensure_ascii=False, separators=(',', ':')).replace('&', '&amp;').replace("'", '&#39;')
    js = js.strip() or 'renderVals() { return {}; }'
    return ("</x-dc>\n<script type=\"text/x-dc\" data-dc-script data-props='%s'>\nclass Component extends DCLogic {\n%s\n}\n</script>\n</body>\n</html>\n") % (pj, js)

def nav(items, active):
    out = []
    for label, href in items:
        out.append('<a class="on" href="%s" aria-current="page">%s</a>' % (href, label) if label == active else '<a href="%s">%s</a>' % (href, label))
    return ''.join(out)

MEMBER_NAV = [('My week', 'MyHusna.dc.html'), ('Discover', 'Discover.dc.html'), ('Organizations', 'Organizations.dc.html'), ('Family', 'Family.dc.html'), ('Saved', 'Saved.dc.html')]
VISITOR_NAV = [('Discover', 'Discover.dc.html'), ('Organizations', 'Organizations.dc.html'), ('For organizations', 'ForOrgs.dc.html')]

def member_header(active=None):
    return ('<header class="hdr"><div class="wrap">\n<a class="brand" href="MyHusna.dc.html" aria-label="Husna home">%shusna<i>.</i></a>\n'
            '<nav class="nav" aria-label="Primary">%s</nav>\n'
            '<div class="row g8 push"><a class="ibtn" href="Messages.dc.html" aria-label="Messages">%s</a><a class="ibtn" href="Notifications.dc.html" aria-label="Notifications">%s</a>'
            '<a class="av" href="Account.dc.html" aria-label="Account, Amina Farah">AF</a><a class="ibtn menu-btn" href="MenuMember.dc.html" aria-label="Menu">%s</a></div>\n</div></header>\n'
            ) % (LOGO, nav(MEMBER_NAV, active), MSG, BELL, MENU)

def visitor_header(active=None):
    return ('<div class="ribbon"><div class="wrap"><span><b>Husna</b> · Columbus, Ohio</span><span>A place to belong</span></div></div>\n'
            '<header class="hdr"><div class="wrap">\n<a class="brand" href="Main.dc.html" aria-label="Husna home">%shusna<i>.</i></a>\n'
            '<nav class="nav" aria-label="Primary">%s</nav>\n'
            '<div class="row g8 push"><a class="btn" href="SignIn.dc.html">Sign in</a><a class="btn pri" href="SignUp.dc.html">Create account</a>'
            '<a class="ibtn menu-btn" href="MenuVisitor.dc.html" aria-label="Menu">%s</a></div>\n</div></header>\n') % (LOGO, nav(VISITOR_NAV, active), MENU)

FOOT_MEMBER = '<footer class="foot"><div class="wrap"><span>© 2026 Husna · Columbus, Ohio</span><nav class="row g20" aria-label="Footer"><a href="Help.dc.html">Help</a><a href="Terms.dc.html">Terms</a><a href="Privacy.dc.html">Privacy</a><a href="Workspaces.dc.html">Switch space</a></nav></div></footer>\n'
FOOT_PUBLIC = ('<footer class="foot"><div class="wrap">\n<div class="stack g4"><a class="brand" href="Main.dc.html" aria-label="Husna home">%shusna<i>.</i></a><span>One city. Countless connections.</span></div>\n'
               '<nav class="row g20" aria-label="Footer"><a href="Discover.dc.html">Discover</a><a href="Organizations.dc.html">Organizations</a><a href="ForOrgs.dc.html">For organizations</a><a href="Help.dc.html">Help</a><a href="Terms.dc.html">Terms</a><a href="Privacy.dc.html">Privacy</a></nav>\n</div></footer>\n') % LOGO

def org_side(active_href):
    s = open(os.path.join(ROOT, 'OrgHome.dc.html'), encoding='utf-8').read()
    side = s[s.index('<aside class="side" aria-label="Workspace">'):s.index('</aside>') + 8]
    side = re.sub(r'<a class="on" href="([^"]+)" aria-current="page">', r'<a href="\1">', side)
    if active_href:
        a = '<a href="%s">' % active_href
        assert side.count(a) == 1, active_href
        side = side.replace(a, '<a class="on" href="%s" aria-current="page">' % active_href)
    return side + '\n'

def founder_side(active_href):
    s = open(os.path.join(ROOT, 'Founder.dc.html'), encoding='utf-8').read()
    side = s[s.index('<aside class="side fd"'):s.index('</aside>') + 8]
    side = re.sub(r'<a class="on" href="([^"]+)" aria-current="page">', r'<a href="\1">', side)
    if active_href:
        a = '<a href="%s">' % active_href
        assert side.count(a) == 1, active_href
        side = side.replace(a, '<a class="on" href="%s" aria-current="page">' % active_href)
    return side + '\n'

def crumbs(parts):
    out = []
    for i, p in enumerate(parts):
        if i: out.append('<span aria-hidden="true">/</span>')
        out.append('<a href="%s">%s</a>' % (p[1], p[0]) if isinstance(p, tuple) else '<span>%s</span>' % p)
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ''.join(out) + '</nav>'

def page_member(name, title, active, main, js='', h=1400, props=None):
    html = head(title) + '<div class="page">\n\n' + member_header(active) + '\n<main>\n' + main.strip() + '\n</main>\n\n' + FOOT_MEMBER + '</div>\n' + tail(js, 1440, h, props)
    write(name, html)

def page_public(name, title, active, main, js='', h=1400, props=None):
    html = head(title) + '<div class="page">\n\n' + visitor_header(active) + '\n<main>\n' + main.strip() + '\n</main>\n\n' + FOOT_PUBLIC + '</div>\n' + tail(js, 1440, h, props)
    write(name, html)

def page_org(name, title, active_href, crumb_parts, main, js='', h=1400, props=None, who=('KO', 'Khadija Osman, Owner. Switch space or sign out'), side=None):
    bar = '<div class="work-bar">%s<a class="av" href="Workspaces.dc.html" aria-label="%s">%s</a></div>\n' % (crumbs([('Crescent House Masjid', 'OrgHome.dc.html')] + crumb_parts), who[1], who[0])
    html = head(title) + '<div class="shell">\n\n' + (side or org_side(active_href)) + '\n<main class="work">\n' + bar + '\n' + main.strip() + '\n</main>\n</div>\n' + tail(js, 1440, h, props)
    write(name, html)

def page_founder(name, title, active_href, crumb_parts, main, js='', h=1400, props=None):
    bar = '<div class="work-bar">%s<a class="av" href="FounderSettings.dc.html" aria-label="Isiah, console owner. Open settings" style="border-color: #e0d3bd">IC</a></div>\n' % crumbs([('Founder console', 'Founder.dc.html')] + crumb_parts)
    html = (head(title) + '<div class="page">\n<div class="strip">Founder console · every action here is written to the <a href="FounderAudit.dc.html">audit log</a></div>\n<div class="shell in">\n\n'
            + founder_side(active_href) + '\n<main class="work">\n' + bar + '\n' + main.strip() + '\n</main>\n</div>\n</div>\n' + tail(js, 1440, h, props))
    write(name, html)

def sheet(name, title, eyebrow, heading, close_href, body, js='', h=700, props=None, tid='sh-title', wide=False):
    html = (head(title, '#060908') + '<div class="scrim">\n<div class="sheet" role="dialog" aria-modal="true" aria-labelledby="%s"%s>\n<div class="sheet-h">\n'
            '<div class="stack g8"><p class="eyebrow">%s</p><h1 class="d3" id="%s">%s</h1></div>\n'
            '<a class="ibtn" href="%s" aria-label="Close">%s</a>\n</div>\n%s\n</div>\n</div>\n') % (tid, ' style="width: min(660px, 100%)"' if wide else '', eyebrow, tid, heading, close_href, X, body.strip())
    write(name, html + tail(js, 720, h, props))

def auth(name, title, body, js='', h=700, props=None, wide=False):
    html = (head(title) + '<div class="auth">\n<main class="auth-main">\n<div class="auth-card%s stack g24">\n'
            '<a class="brand" href="Main.dc.html" aria-label="Husna home">%shusna<i>.</i></a>\n%s\n</div>\n</main>\n</div>\n') % (' w' if wide else '', LOGO, body.strip())
    write(name, html + tail(js, 720, h, props))

def write(name, html):
    assert name.endswith('.dc.html')
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(html)
    print('wrote', name, len(html))
