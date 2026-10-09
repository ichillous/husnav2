# Husna redesign

The complete high-fidelity design of Husna: every screen as HTML, clickable end to end.

Husna is a free platform for Islamic organizations and the people they serve, starting in Columbus, Ohio.
This repository holds the design, not the production app. All organizations, people, prices and counts in
it are fictional sample data.

## See it

**In a browser, from this repository**

```bash
node tools/serve.cjs
```

then open <http://localhost:4173>. Nothing to install; it needs only Node.

**On the web.** The repository is laid out as a static site, so GitHub Pages can serve it as it is:
Settings → Pages → Deploy from a branch → `main`, folder `/ (root)`. It then lives at
<https://ichillous.github.io/husnav2/>.

The first page lists all 155 screens. Open one and click through: links inside a screen lead to the next
screen, as they will in the product. Start with **S1, the map**, which shows every screen, what can be
pressed on it and where each press leads.

## What is in it

| Group | Screens | What |
| --- | --- | --- |
| S · Start here | 2 | The map of every screen and click, and the design system |
| A · Public site | 20 | Home, discover, events, organizations, Friday and Eid prayers, Qur'an school, giving and zakah, help, legal |
| B · Accounts | 18 | Sign in, sign up, organization application, invitations |
| C · Member and family | 20 | My week, family, enrolling children, payments, messages, the home masjid banner |
| D · Organization workspace | 39 | Events, Friday and Eid prayers, prayer times, TV displays, school, money, team, settings |
| E · Founder console | 18 | Approvals, organizations, users, moderation, support, payments and coffee, audit |
| F · System | 7 | Empty and error states, every email and text, hand-offs to Stripe, printed documents |
| G · On a phone | 18 | The same screens at 390px, and the menus |
| H · On a TV | 13 | What a masjid's TV shows through the day |

A few things the design settles:

- **Husna is free.** No plans and no platform fee; nothing is taken from donations or tuition. Members and
  organizations can buy the developer a coffee, and that is the only way money reaches Husna.
- **Home masjid.** A member chooses one masjid, and its prayer times sit at the top of every page they open.
- **Fridays and Eid.** A masjid holds one Jumu'ah or several, each with a khutbah start and an iqamah. Eid is
  its own occasion, with its place, prayer times, details and parking, because it is often not at the masjid.
- **Zakah** has its own button, page and fund.
- **TV displays.** A masjid opens `husna.app/tv` on any screen with a browser, types the code into its
  workspace, and the screen follows the day by itself.
- **Open decisions** are written `[IN BRACKETS, IN CAPITALS]` on the screens; AGENTS.md lists them.

## How it is built

Each screen is one file in `project/`, named `Something.dc.html`: plain HTML with a small template syntax
and a few lines of logic for its states. One stylesheet, `project/husna.css`, is the design system.
`project/support.js` makes the files run in any browser. There is no build step for the screens.

The same files open in Claude Design as the "Husna Redesign" canvas, where each screen is an artboard.

To change the design, by hand or with a coding agent, read **[AGENTS.md](AGENTS.md)**. In short:

```bash
npm install                    # once, for the checks
node tools/check.cjs           # every screen renders, every button does something, every link leads somewhere
node tools/check.cjs --w=390   # and nothing breaks at phone width
bash tools/refresh-canvas.sh   # after adding or removing screens
```

## Credits

The screens load [React](https://react.dev) (MIT licence, `runtime/vendor`) through `project/support.js`.
The typefaces are Instrument Serif, DM Sans and Amiri, each under the SIL Open Font License
(`runtime/fonts`, used by the checking tools; the screens themselves load them from Google Fonts).
