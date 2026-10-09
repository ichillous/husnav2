// Opens the design in a browser, the same way a static host (GitHub Pages, Vercel) would serve it.
//   node tools/serve.cjs [port]        then open http://localhost:4173
const { ROOT, serve } = require('./lib.cjs');
serve(ROOT, Number(process.argv[2]) || 4173).then(({ port }) => console.log(`Husna design: http://localhost:${port}/   (Ctrl+C to stop)`));
