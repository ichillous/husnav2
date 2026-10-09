// Click audit: for every screen, lists every link (label, destination, where on the page it sits) and presses
// every button once on a fresh load, recording what changed. The map (Map.dc.html) is written from the result.
//   node tools/audit.cjs [File.dc.html ...]      writes tools/canvas/audit.json
const fs = require('fs'), path = require('path');
const { PROJECT, serve, launch, localFonts, canvas: readCanvas, screens } = require('./lib.cjs');
const only = process.argv.slice(2), outFile = path.join(__dirname, 'canvas', 'audit.json');
const canvas = readCanvas();
let files = only.length ? only.map((f) => (f.endsWith('.dc.html') ? f : f + '.dc.html')) : screens();

const SNAP = () => {
  // Clocks and countdowns (TV previews, the home masjid banner) change by themselves; leave them out of the comparison.
  const ticking = [...document.querySelectorAll('.tv-mini, .pbar')], shown = ticking.map(e => e.style.display);
  ticking.forEach(e => { e.style.display = 'none'; });
  const lines = (document.body.innerText || '').split('\n').map(s => s.trim()).filter(Boolean);
  ticking.forEach((e, i) => { e.style.display = shown[i]; });
  const btns = [...document.querySelectorAll('button')];
  return { lines, nBtn: btns.length, cls: [...document.querySelectorAll('[class]')].map(e => e.className).join('|').length + ':' + document.querySelectorAll('*').length };
};

async function open(browser, port, file, w) {
  const ctx = await browser.newContext({ viewport: { width: w, height: 900 } });
  const page = await ctx.newPage();
  await localFonts(page, port);
  await page.goto(`http://localhost:${port}/${file}`, { waitUntil: 'networkidle', timeout: 20000 });
  await page.waitForTimeout(200);
  return { ctx, page };
}

async function auditFile(browser, port, file) {
  const w = (canvas.boards[file] || {}).w || 1440;
  const { ctx, page } = await open(browser, port, file, w);
  const base = await page.evaluate(() => {
    const region = (el) => {
      if (el.closest('aside.side')) return 'sidebar';
      if (el.closest('header.hdr') || el.closest('.ribbon') || el.closest('.strip')) return 'header';
      if (el.closest('footer.foot')) return 'footer';
      if (el.closest('.work-bar')) return 'workbar';
      return 'main';
    };
    const label = (el) => {
      const key = el.querySelector && el.querySelector('.li-t, .d4, .d3, .t1, .b');
      const raw = el.getAttribute('aria-label') || (key && key.innerText) || el.innerText || el.textContent || '';
      return raw.replace(/\s+/g, ' ').trim().slice(0, 90);
    };
    const links = [...document.querySelectorAll('a[href]')].map(a => ({ label: label(a), href: a.getAttribute('href'), region: region(a), cls: a.className }));
    const buttons = [...document.querySelectorAll('button')].map((b, i) => ({ i, label: label(b), region: region(b), cls: b.className, pressed: b.getAttribute('aria-pressed') }));
    const sets = [...document.querySelectorAll('.set')].map(s => {
      const ctr = [...s.querySelectorAll('input,select,button,a.btn,textarea')].map(c => c.tagName.toLowerCase() + (c.className ? '.' + String(c.className).split(' ')[0] : ''));
      return { text: (s.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 70), controls: ctr };
    }).filter(s => s.controls.length > 1);
    const fields = document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=search]),textarea,select').length;
    const title = document.title;
    const h1 = (document.querySelector('h1') || {}).innerText || '';
    const natural = document.documentElement.scrollHeight;
    const tweaks = null;
    return { links, buttons, sets, fields, title, h1: h1.replace(/\s+/g, ' ').trim(), natural };
  });
  await ctx.close();
  // click each button on a fresh page
  const results = [];
  for (const b of base.buttons) {
    const { ctx: c2, page: p2 } = await open(browser, port, file, w);
    try {
      const before = await p2.evaluate(SNAP);
      const handle = (await p2.$$('button'))[b.i];
      if (!handle) { results.push({ ...b, outcome: 'gone' }); await c2.close(); continue; }
      await handle.evaluate(el => el.click());
      await p2.waitForTimeout(120);
      const after = await p2.evaluate(SNAP);
      const bs = new Map(); before.lines.forEach(l => bs.set(l, (bs.get(l) || 0) + 1));
      const as = new Map(); after.lines.forEach(l => as.set(l, (as.get(l) || 0) + 1));
      const added = []; const removed = [];
      for (const [l, n] of as) { const d = n - (bs.get(l) || 0); for (let k = 0; k < d; k++) added.push(l); }
      for (const [l, n] of bs) { const d = n - (as.get(l) || 0); for (let k = 0; k < d; k++) removed.push(l); }
      let outcome;
      if (!added.length && !removed.length) outcome = before.cls === after.cls ? 'NOTHING' : 'style-only';
      else if (added.length <= 1 && removed.length <= 1 && removed[0] && removed[0].replace(/\s+/g, ' ') === b.label.replace(/\s+/g, ' ')) outcome = 'label-only';
      else if (added.length + removed.length <= 3) outcome = 'small';
      else outcome = 'panel';
      results.push({ ...b, outcome, added: added.slice(0, 4).map(s => s.slice(0, 110)), removed: removed.slice(0, 3).map(s => s.slice(0, 80)), nAdded: added.length, nRemoved: removed.length });
    } catch (e) { results.push({ ...b, outcome: 'ERR ' + String(e).slice(0, 80) }); }
    await c2.close();
  }
  return { file, w, title: base.title, h1: base.h1, natural: base.natural, fields: base.fields, links: base.links, buttons: results, sets: base.sets };
}

(async () => {
  const { server, port } = await serve(PROJECT);
  const browser = await launch();
  const out = [];
  const queue = files.slice();
  const worker = async () => { while (queue.length) { const f = queue.shift(); try { out.push(await auditFile(browser, port, f)); } catch (e) { out.push({ file: f, error: String(e).slice(0, 200) }); } } };
  await Promise.all(Array.from({ length: 6 }, worker));
  if (only.length && fs.existsSync(outFile)) {          // a partial run updates those screens and keeps the rest
    const done = new Set(out.map((o) => o.file));
    for (const o of JSON.parse(fs.readFileSync(outFile, 'utf8'))) if (!done.has(o.file)) out.push(o);
  }
  out.sort((a, b) => a.file.localeCompare(b.file));
  fs.writeFileSync(outFile, JSON.stringify(out));
  await browser.close();
  server.close();
  console.log('audited', out.length, 'files;', out.reduce((n, o) => n + (o.buttons || []).length, 0), 'buttons;', out.reduce((n, o) => n + (o.links || []).length, 0), 'links');
})();
