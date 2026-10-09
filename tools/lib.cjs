// Shared by the tools: where things are, a tiny static server, and local fonts for steady measurements.
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const PROJECT = path.join(ROOT, 'project');
const FONTS = path.join(ROOT, 'runtime', 'fonts');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.woff2': 'font/woff2', '.png': 'image/png', '.svg': 'image/svg+xml', '.md': 'text/plain; charset=utf-8' };

function playwright() {
  for (const id of ['playwright', 'playwright-core', '/opt/npm-tools/node_modules/playwright']) { try { return require(id); } catch (e) { /* try the next one */ } }
  console.error('Playwright is not installed. Run: npm install && npx playwright install chromium'); process.exit(1);
}
function launch() { return playwright().chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}); }

/** Serves a folder. /__fonts/ is the bundled font files. Resolves with { server, port }. */
function serve(dir, port = 0) {
  const server = http.createServer((req, res) => {
    let u = decodeURIComponent(req.url.split('?')[0]);
    if (u.endsWith('/')) u += 'index.html';
    const f = u.startsWith('/__fonts/') ? path.join(FONTS, path.basename(u)) : path.join(dir, path.normalize(u));
    if (!f.startsWith(dir) && !f.startsWith(FONTS)) { res.writeHead(403); res.end(); return; }
    fs.readFile(f, (err, data) => {
      if (err) { res.writeHead(404, { 'content-type': 'text/plain' }); res.end('Not found: ' + u); return; }
      res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-store' }); res.end(data);
    });
  });
  return new Promise((resolve) => server.listen(port, () => resolve({ server, port: server.address().port })));
}

/** The screens ask Google Fonts for their type. Tools answer from runtime/fonts so text measures the same everywhere. */
async function localFonts(page, port) {
  const face = (family, file, weight, style) => `@font-face{font-family:'${family}';font-style:${style || 'normal'};font-weight:${weight};src:url(http://localhost:${port}/__fonts/${file}) format('woff2')}`;
  const css = [face('Instrument Serif', 'instrument-serif-latin-400-normal.woff2', 400), face('Instrument Serif', 'instrument-serif-latin-400-italic.woff2', 400, 'italic'),
    face('DM Sans', 'dm-sans-latin-400-normal.woff2', 400), face('DM Sans', 'dm-sans-latin-500-normal.woff2', 500), face('DM Sans', 'dm-sans-latin-600-normal.woff2', 600), face('DM Sans', 'dm-sans-latin-700-normal.woff2', 700),
    face('Amiri', 'amiri-arabic-400-normal.woff2', 400).replace('}', ';unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF}')].join('\n');
  await page.route(/fonts\.googleapis\.com/, (r) => r.fulfill({ contentType: 'text/css', body: css }));
  await page.route(/fonts\.gstatic\.com/, (r) => r.abort());
}

function canvas() { return JSON.parse(fs.readFileSync(path.join(PROJECT, 'canvas.json'), 'utf8')); }
function screens() { return fs.readdirSync(PROJECT).filter((f) => f.endsWith('.dc.html')).sort(); }

module.exports = { ROOT, PROJECT, serve, launch, localFonts, canvas, screens };
