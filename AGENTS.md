# Husna redesign: instructions for coding agents

This repository is the high-fidelity design of Husna, a free platform for Islamic organizations and the
people they serve, starting in Columbus, Ohio. It is a clickable prototype: 150 screens of HTML, one file
per screen, with sample data. It is not the production app and has no backend.

Your job here is to change the design: add screens, rework screens, fix copy, keep everything consistent
and every click leading somewhere.

## Run it and check it

```bash
node tools/serve.cjs            # open http://localhost:4173  (the index, and every screen)
npm install                     # once, for the checks below (installs Playwright)
npx playwright install chromium # once, if no Chromium is present
node tools/check.cjs            # renders every screen; fails on anything broken
node tools/check.cjs --w=390    # the same at phone width
node tools/check.cjs Main OrgHome --shots=shots   # only these, with PNGs to look at
bash tools/refresh-canvas.sh    # after adding or removing screens: rebuilds the map and the canvas layout
```

Always run both `check` commands before you commit. Look at a screenshot of anything you changed; a clean
check only proves nothing is broken, not that it looks right.

## What is where

| Path | What it is |
| --- | --- |
| `project/*.dc.html` | The screens. One file per screen or per state. **This is the source of truth.** Edit these directly. |
| `project/husna.css` | The design system: one stylesheet shared by every screen. |
| `project/canvas.json` | Where each screen sits on the Claude Design canvas, its title and size. Written by `tools/canvas/layout.py`. |
| `project/index.html` | The front door: lists every screen and opens each in a frame. Reads `canvas.json`; never needs rebuilding. |
| `project/support.js` | Generated. React plus `runtime/dc-runtime.js`. Do not edit; run `node tools/build-support.mjs`. |
| `runtime/dc-runtime.js` | The small runtime that renders a `.dc.html` file in a browser. |
| `runtime/vendor`, `runtime/fonts` | React (MIT) and the three typefaces (SIL Open Font License), with their licences. |
| `tools/` | The server, the checker, the click audit, and the canvas scripts. |
| `tools/canvas/rows.py` | The list of every screen: file, code and title, width, kind. Add a screen here first. |

There are no page generators. Earlier screens were written by scripts that no longer exist; do not try to
regenerate a screen, edit its file.

## How a screen file works

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Report an absence</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="./husna.css">
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Amiri&amp;family=DM+Sans:wght@400;500;600;700&amp;family=Instrument+Serif:ital@0;1&amp;display=swap" rel="stylesheet">
<style>
body{margin:0;background:#0b100f}
a{color:#c8efa4}a:hover{color:#dbf7c1}
</style>
</helmet>
<div class="page"> … the screen … </div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":1440,"height":1400}}'>
class Component extends DCLogic {
  state = { sent: false };
  renderVals() {
    const s = this.state;
    return { form: !s.sent, done: s.sent, send: () => this.setState({ sent: true }) };
  }
}
</script>
</body>
</html>
```

The markup inside `<x-dc>` is a template. The class supplies its values.

- **Holes.** `{{ name }}` or `{{ item.name }}` is a lookup into what `renderVals()` returns. It is never an
  expression: no `{{ a + b }}`, no `{{ !x }}`, no calls. Compute in `renderVals()` and return the result by name.
- **Attributes.** `x="{{ value }}"` passes the raw value (a function, a boolean, a number). `x="a {{ value }}"`
  makes a string. Write attribute names the React way: `onClick`, `onInput`, `onChange`, `defaultValue`,
  `maxLength`, `inputMode`, `autoComplete`, `colSpan`. `class` and `for` stay as they are.
- **Events.** `onClick="{{ send }}"` where `send` is a function returned from `renderVals()`.
- **Conditions.** `<sc-if value="{{ form }}" hint-placeholder-val="{{true}}"> … </sc-if>`. There is no else;
  return two flags and use two blocks.
- **Lists.** `<sc-for list="{{ rows }}" as="r" hint-placeholder-count="4"> {{ r.name }} </sc-for>`. Give each
  item its own handlers in `renderVals()`: `rows.map((r) => ({ ...r, pick: () => this.setState({ id: r.id }) }))`.
- **A screen inside a screen.** `<dc-import name="PrayerBar" hint-size="100%,45px"></dc-import>` mounts
  `PrayerBar.dc.html`. Other attributes become its props (`shown="{{ home }}"` arrives as `this.props.shown`).
  The phone boards and the TV previews are built this way, so there is one copy of each screen.
- **State.** `state`, `this.setState`, `componentDidMount` and `componentWillUnmount` work as in a React
  class. Do not write `render()`.
- **Switchable states (tweaks).** Declare them in `data-props`:
  `'{"viewer":{"editor":"enum","options":["Visitor","Member"],"default":"Visitor"}, "$preview":{…}}'` and read
  `this.props.viewer ?? 'Visitor'`. In the browser, set one from the address bar: `OrgProfile.dc.html?viewer=Member`.
  The index page offers them as menus.
- **Links.** `<a href="Other.dc.html">` goes to another screen. `href="#id"` scrolls within the screen.
  Style the link itself as the button (`class="btn pri"`).

### Rules that bite

1. **Close every tag** (`</li>`, `</p>`, `</td>`, `</option>`). The runtime reads the file literally.
2. **Never put a `<button>` inside an `<a>`**, and never use `<form>`.
3. **Every `<button>` needs an `onClick`** that changes something on the screen. Every `<a>` needs a real
   destination. `tools/check.cjs` fails on a button that does nothing or a link to a missing file.
4. **Keep each screen's own state inside it.** A flow that must share state across steps is one file with
   one `<sc-if>` per step.
5. **Single-quote `data-props`** and keep it valid JSON. Write `&amp;` for `&` and `&#39;` for `'` inside it.
6. **Do not hand-edit `$preview`, `canvas.json` or `Map.dc.html`.** `tools/refresh-canvas.sh` writes them.
7. **Styles go in `husna.css`.** A one-off adjustment may be an inline `style`. Do not add `<style>` blocks
   to a screen beyond the three lines every helmet already has.

## The design system

`project/System.dc.html` (S2 on the canvas) shows all of it. The header of `husna.css` lists the tokens.

- **Color.** Dark forest ground `--bg #0b100f`, wells `--bg2`, cards `--panel #14201c`; ink `--ink #f3f0e7`,
  muted `--mut`, subtle `--sub`. One accent, sage `--acc #c8efa4`, with `--acc-ink #11190f` on top of it.
  Sand `--sand #e0d3bd` marks the founder console and nothing else. Status colors `--ok --warn --bad --info`
  always come with a word.
- **Type.** Instrument Serif for display (`.d2 .d3 .d4`, headline halves in `<em>` turn sage), DM Sans for
  everything else, Amiri for Arabic.
- **Shape and space.** Cards 18px radius, controls 11 to 14, chips fully round. Targets are at least 44px.
  Spacing comes from `.stack .g4 … .g48` and `.row`.
- **Parts you will reuse.** `.btn` (`.pri .sm .xl .quiet .danger .block .off`), `.chip`, `.seg`, `.tabs`,
  `.pick`, `.field/.label/.input/.select/.textarea/.hint`, `.check`, `.sw` (switch), `.set` (one settings row:
  words left, one control right), `.card` (`.flat .tint .lg .p0`), `.note` (`.ok .warn .bad .info`), `.badge`,
  `.stat`, `.tbl-wrap/.tbl`, `.list/.li`, `.kv`, `.tl` (timeline), `.savebar` with `.state`, `.sheet` in a
  `.scrim`, `.split` with `.col-main` and `.col-side`, `.cols` (`.c2 .c4 .c5 .c2w`).
- **Page shells.** Public and member pages: `.page` with `header.hdr`, `main`, `footer.foot`. The workspace
  and the founder console: `.shell` with `aside.side` and `main.work`. Copy the header, footer or sidebar
  from a neighbouring screen exactly; they are identical everywhere, and when one changes, change them all.
- **Patterns already decided.** A page of fields shows a floating save bar the moment anything changes.
  Step forms keep Back and Continue in view. Destructive actions are a red outline and ask on the spot.
  Empty states are one sentence and one action. Card details are never typed into Husna: every payment
  hands over to a page Stripe hosts (`Stripe.dc.html`).
- **Phone.** The same files at 390px. The header keeps the logo and a Menu button; the menus are their own
  screens. No screen may scroll sideways.
- **TV.** `.tv` is one fixed 1920 by 1080 frame (1080 by 1920 for portrait). Nothing on it can be pressed.
  The smallest type is 22px.

## Product rules. Do not break these

- **Husna is free.** No plans, no platform fee, nothing taken from donations, tuition or payment links. The
  only charge anyone sees is Stripe's own card processing, which goes to Stripe. Never design a paywall, an
  upgrade prompt or a fee.
- **"Buy the developer a coffee"** is the one way money reaches Husna: a voluntary, one-time gift.
  `Coffee.dc.html` for members and visitors (footer, phone menu, Account, Help), `OrgCoffee.dc.html` for
  organizations (foot of the workspace sidebar, Settings). It never interrupts: no pop-ups, no reminders,
  nothing unlocked by it.
- **Events and RSVPs are always free.** There is no checkout on an event.
- **Organizations are verified by a person** before a profile goes live.
- **Children's records are private** to their family and the schools the family chose. Health notes are
  shown only where a teacher needs them, and every opening is logged.
- **Prayer times belong to masjids.** Only an organization of kind Masjid has the Prayer times page.
  The masjid sets each iqamah; adhan times are calculated for its address.
- **Home masjid.** A member may choose one masjid as home (from its page, from Welcome, or in Account).
  Its adhan and iqamah times then sit in a banner (`PrayerBar.dc.html`) at the top of every member page.
  On a wide screen all five prayers are visible and only the countdown changes; when they cannot fit, the
  line moves. No home masjid, no banner.
- **TV displays.** On the TV: open `husna.app/tv`. In the workspace: TV displays, Pair a TV, type the code.
  Then choose what it shows. The TV keeps itself up to date; no computer or phone needs to stay connected.
- **Anything not yet decided is written `[IN BRACKETS, IN CAPITALS]`** on the screen. Do not invent a value
  for one; do not remove one unless the owner has decided it.

## The sample world. Keep it consistent

- "Today" is **Thursday, October 8, 2026** (27 Rabi' al-Thani 1448). Screens that show the term under way
  (child page, attendance, rosters, payouts, teacher's workspace, Payments) are dated mid-November.
- **Crescent House Masjid**, 1200 Sample Avenue, Columbus, OH 43229, (614) 555-0100. Legal name Crescent
  House Islamic Society, Inc. Owner Khadija Osman; admin Imam Adam Rahman. Other organizations: Mosaic Muslim
  Collective (nonprofit), Lantern Learning House (education).
- **The family.** Amina Farah (parent, the signed-in member), Idris Farah, children Yusuf (9, Level 2,
  peanut allergy, no photos) and Maryam (6, Level 1). Teacher Ustadh Bilal Ahmed.
- **Weekend Qur'an School.** Fall term October 24 to December 20. $240.00 a child; $444.00 for two after
  the sibling discount, in two payments of $222.00 (October 20 and November 24).
- **Prayer times on October 8.** Fajr 6:21 (iqamah 6:45), Sunrise 7:36, Dhuhr 1:21 (1:45), Asr 4:32 (4:50),
  Maghrib 7:04 (7:09), Isha 8:17 (8:30). Friday services at 1:30, 2:30 and 3:30 PM. Isha iqamah moves to
  8:15 on October 18; the clocks go back on November 1.
- Everything is fictional. Use `example` domains and 555 phone numbers. Never put a real person's details
  on a screen.

## How Husna talks

Plain, warm and specific. Say what happened, then what happens next. Never blame, never shout, never leave
a parent wondering whether they were charged.

- Dates: "Saturday, October 24"; add the year only when it is not this one. In tables: "Sat, Oct 24".
- Times: "9:00 AM to 12:30 PM". Money: "$240.00", always two decimals, a minus sign for money going back.
- Counts: "47 of 58". People: full name the first time, then first name. Teachers keep their title.
- Buttons say what they do ("Report the absence"), not "Submit" or "OK".
- No exclamation marks, no emoji, no lorem ipsum.

## Adding or changing a screen

1. Copy the nearest existing screen. Keep its shell, header, footer or sidebar unchanged.
2. Name the file in PascalCase with the area first: `OrgSomething.dc.html`, `FounderSomething.dc.html`,
   sheets end in `Sheet`, TV frames start with `Tv`, phone boards with `Phone`.
3. Add it to `tools/canvas/rows.py` with the next free code in its group
   (A public, B accounts, C member, D workspace, E founder console, F system, G phone, H TV), its width
   (1440 page, 720 sheet, 390 phone, 816 printed page, 1920 TV) and its kind.
4. Link to it from every screen that should lead there, and give it a way back. Nothing may be a dead end.
5. If it changes the workspace sidebar, the footer or a menu, change every copy (search for the link text).
6. Run `bash tools/refresh-canvas.sh`. It rebuilds the map, lays out the canvas and runs both checks.
7. Look at the screenshots (`node tools/check.cjs YourScreen --shots=shots`), at 1440 and at 390.

## Taking changes back to the Claude Design canvas

The design also lives as a Claude Design artifact named "Husna Redesign". To update it from this repository,
publish these files to the artifact's `project/` folder: every `project/*.dc.html`, `project/husna.css` and
`project/canvas.json`. **Never publish `project/support.js` or `project/index.html`**; the canvas has its own
runtime. If the canvas was edited after the last export, read it first and merge, because a publish replaces
what is there.

## Open decisions

These appear in brackets on the screens and are the owner's to settle: `[TERMS VERSION]`, `[PRIVACY VERSION]`
and the legal text itself (needs counsel); `[REVIEW TIME]`, `[SUPPORT RESPONSE TIME]`; `[SUPPORT EMAIL]`,
`[SENDER ADDRESS]`, `[ALERT EMAIL AND PHONE]`, `[TEXT SENDER NUMBER]`; `[RETENTION PERIOD]`,
`[ACCOUNT RECOVERY WINDOW]`, `[DATA REQUEST DEADLINE]`; `[COMPANY NAME AND MAILING ADDRESS]`;
`[STATEMENT DESCRIPTOR]`, `[STRIPE REFUND RULE]`; `[TESTED TV DEVICES]`, `[VIDEO SIZE LIMIT]`.

## Do not

- Do not add a framework, a bundler or a build step for the screens. They are plain files on purpose.
- Do not move files out of `project/` or rename existing screens; links and the canvas depend on the names.
- Do not commit screenshots or `node_modules`.
- Do not treat sample data as real, and do not add real data.
