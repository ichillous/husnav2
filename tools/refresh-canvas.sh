#!/bin/bash
# After adding, removing or resizing screens: rebuild the map (S1) and lay the canvas out again.
# Needs Node with Playwright (npm install) and Python 3. Takes a few minutes.
set -e
cd "$(dirname "$0")/.."
node tools/build-support.mjs
python3 tools/canvas/layout.py prep         # every screen in rows.py gets its width in canvas.json
node tools/audit.cjs                        # press every button, list every link
python3 tools/canvas/map.py                 # write project/Map.dc.html from the audit
node tools/check.cjs --heights              # measure every screen (and fail on anything broken)
python3 tools/canvas/layout.py              # place every artboard; writes project/canvas.json
node tools/check.cjs --w=390                # the same screens at phone width
echo "Canvas refreshed."
