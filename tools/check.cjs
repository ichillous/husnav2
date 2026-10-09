// Renders screens in a headless browser and reports anything broken.
//   node tools/check.cjs                     every screen, at the width its artboard has on the canvas
//   node tools/check.cjs Main MyHusna        only these
//   node tools/check.cjs --w=390             every screen at phone width (TV frames and printed pages are skipped)
//   node tools/check.cjs --shots=shots       also save a PNG of each screen
//   node tools/check.cjs --heights           also write tools/canvas/heights.json (used by tools/canvas/layout.py)
// It fails (exit code 1) on: a screen that does not load, a script error, a {{hole}} left unfilled, a link to a file
// that does not exist, a <button> with no handler, or a page wider than its window.
const fs = require('fs'), path = require('path');
const { PROJECT, serve, launch, localFonts, canvas, screens } = require('./lib.cjs');
const args = process.argv.slice(2), flag = (n) => { const a = args.find((x) => x === '--' + n || x.startsWith('--' + n + '=')); return a ? (a.split('=')[1] || true) : null; };
const forceW = Number(flag('w')) || 0, shots = flag('shots') === true ? 'shots' : flag('shots'), wantHeights = !!flag('heights');
let files = args.filter((a) => !a.startsWith('--')).map((a) => (a.endsWith('.dc.html') ? a : a + '.dc.html'));
(async () => {
  const boards = canvas().boards;
  if (!files.length) files = screens();
  const fixed = (f) => boards[f] && !boards[f].expand;            // TV frames, printed pages, phone frames: they have one size
  if (forceW) files = files.filter((f) => !fixed(f) && f !== 'Map.dc.html');
  const { server, port } = await serve(PROJECT), browser = await launch();
  if (shots) fs.mkdirSync(shots, { recursive: true });
  const heights = {}; let bad = 0;
  for (const file of files) {
    const b = boards[file] || {}, w = forceW || b.w || 1440;
    const ctx = await browser.newContext({ viewport: { width: w, height: 500 }, deviceScaleFactor: 1 }), page = await ctx.newPage(), errors = [];
    page.on('pageerror', (e) => errors.push(String(e).slice(0, 200)));
    page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errors.push(m.text().slice(0, 200)); });
    await localFonts(page, port);
    const problems = [];
    try { await page.goto(`http://localhost:${port}/${file}`, { waitUntil: 'networkidle', timeout: 30000 }); await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(300); }
    catch (e) { problems.push('did not load: ' + String(e).slice(0, 100)); }
    const info = await page.evaluate(() => ({
      root: !!document.querySelector('#dc-root > .sc-host'), natural: Math.ceil(document.documentElement.scrollHeight),
      hrefs: [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href')),
      dead: [...document.querySelectorAll('button')].filter((x) => !Object.keys(x).some((k) => k.startsWith('__reactProps') && x[k] && x[k].onClick)).map((x) => (x.textContent || x.getAttribute('aria-label') || '').trim().slice(0, 40)),
      wide: document.documentElement.scrollWidth > window.innerWidth + 1, holes: ((document.body.innerText || '').match(/\{\{[^}]*\}\}/g) || []).slice(0, 4)
    })).catch((e) => ({ hrefs: [], dead: [], holes: [], natural: 0, failed: String(e) }));
    if (!info.root) problems.push('nothing rendered');
    if (errors.length) problems.push('errors: ' + [...new Set(errors)].slice(0, 3).join(' | '));
    if (info.holes.length) problems.push('unfilled ' + info.holes.join(' '));
    if (info.dead.length) problems.push('buttons that do nothing: ' + info.dead.join(', '));
    if (info.wide && !fixed(file)) problems.push('wider than the window');
    const missing = [...new Set(info.hrefs.filter((x) => x && !x.startsWith('#') && !/^(https?:|mailto:|tel:)/.test(x)).map((x) => x.split('#')[0].split('?')[0]).filter((x) => !fs.existsSync(path.join(PROJECT, x))))];
    if (missing.length) problems.push('links to missing files: ' + missing.join(', '));
    heights[file] = info.natural;
    if (shots) { await page.setViewportSize({ width: w, height: Math.min(Math.max(info.natural, b.expand ? 0 : (b.h || 0), 200), 12000) }); await page.waitForTimeout(120); await page.screenshot({ path: path.join(shots, file.replace('.dc.html', forceW ? '-' + forceW : '') + '.png') }); }
    await ctx.close();
    if (problems.length) { bad++; console.log('✗ ' + file + '\n    ' + problems.join('\n    ')); }
  }
  await browser.close(); server.close();
  if (wantHeights && !forceW) {
    const p = path.join(__dirname, 'canvas', 'heights.json'), all = fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : {};
    fs.writeFileSync(p, JSON.stringify(Object.assign(all, heights), null, 0)); console.log('heights written to tools/canvas/heights.json');
  }
  console.log(`${files.length} screens checked${forceW ? ' at ' + forceW + 'px' : ''}; ${bad ? bad + ' with problems' : 'all clean'}`);
  process.exit(bad ? 1 : 0);
})();
