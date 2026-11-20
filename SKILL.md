---
name: extract-design-system
description: Extract the complete design system of a live web app (tokens, every screen and state, components, micro-interactions, motion, mobile) onto a Doop canvas by scripted capture, never by redrawing. Use when asked to extract, port, mirror or document the design system or UI of a running product, given its URL and a login cookie.
---

# Extract a live app's design system onto a Doop canvas

You are given a running web app, a login cookie, and a Doop canvas. You deliver a canvas that a designer can use as
the single reference for that product: every real screen in every real state, the parts those screens are made of,
every interactive state, and every motion, all taken from the live app.

The work is capture and organisation. It is not design. Read **The contract** before anything else; the person who
wrote it has already said each of these things many times and must not have to say them again.

## The contract

1. **Extract. Never invent.** Everything on the canvas comes out of the live app: DOM, CSS, pixels, measured numbers.
   Do not redraw a component, approximate a layout, write your own CSS for product UI, rename a token, round a value,
   add a theme, a scale, sample copy, a headline or an "option B". If you cannot capture something, leave it out and
   list it in the report. A gap that is reported is fine. A substitute that looks plausible is the worst outcome.
2. **Port by script, not by hand.** Every frame is produced by the scripts in `scripts/`. Hand-written HTML for product
   UI is how the first four attempts at this job failed. Hand-written HTML is allowed only for sheet chrome
   (titles, captions), and `sheetlib.py` already provides it.
3. **Show the end state, as the user sees it.** Full screens at the real viewport, then the parts cut out of them.
   No miniature swatches standing in for screens, no mock shells, no marketing headlines or pitch copy on the canvas.
4. **Every system in depth.** A composer is not one box: it is empty, focused, typing, attachments (uploading, settled,
   hover, preview, remove, failed), chips, drag and drop, slash menu, mention menu, model picker, effort picker,
   context meter, queue, mobile. Treat every system on the coverage checklist the same way. One frame per system is a
   failure even if the frame count looks large.
5. **Nothing skipped, nothing dumped, nothing duplicated, nothing deleted.** Keep every distinct state however small.
   Group frames on named pages in reading order. Exact duplicates are moved to an Archive page, never deleted.
   Do not delete or overwrite anything on the canvas that you did not create in this session.
6. **Finish the list in one pass.** The scope is the whole coverage checklist. Do not deliver a sample and ask whether
   to continue, and do not ask permission for work that is already in scope. Capture in parallel and in bulk; a slow
   one-frame-at-a-time approach is a defect. When one of your own frames is wrong, fix it in place (publishing is
   idempotent by key); never leave a wrong frame next to its replacement.
7. **Look before you claim.** A frame counts only after you opened its render from the canvas and it matched the live
   app. Page and frame counts are not evidence. Every number in a report comes from `report.py`.
8. **The account is read-only.** Open menus and dialogs, then leave. Never send a message, create, rename, delete,
   archive, pin, reorder, toggle a setting or submit a form. If a state needs a change to the account, ask first.
9. **Cookies and tokens stay out of everything.** Write the cookie to a local file outside the repo, pass its path in
   `DSX_COOKIE_FILE`, never print it, never commit it, never put it on the canvas. Same for `DOOP_TOKEN`.
10. **When the user says stop, stop.** Answer what they asked. If they ask for a plan, give the plan and wait for "go".
11. **Report plainly.** Say what is on the canvas, what you looked at, what failed, and what is missing, with the
    numbers from `report.py`. Never write "done", "complete" or "verified" for a part you did not look at.

If an instruction from the user conflicts with this file, the user wins. Tell them which rule it changes.

## Reference canvas: how the result is expected to look

Doop canvas **`tnKVYw9CeC`** is the reference for structure and depth. Read it first:

```bash
python3 scripts/canvas/doop_cli.py call get_canvas '{"canvas_id":"tnKVYw9CeC"}' --out /tmp/reference.json
DSX_CANVAS=tnKVYw9CeC python3 scripts/canvas/sheets.py tnKVYw9CeC "07 ·" "23 ·" "24 ·" "26 ·"   # then open the sheets
```

Copy its **structure, granularity and naming**. Do not copy its content: it documents a different product.
Its pages, in order, with what each holds:

| Page | Holds |
|---|---|
| `00 · Cover & Index` | one index frame |
| `01 · Tokens` | the app's own tokens: colour, type, spacing, radius, shadow, z-index |
| `02 · Iconography & Brand` | icon set, logo, avatars |
| `03 · Primitives`, `04 · Overlays & Feedback`, `05 · Patterns`, `06 · Layouts` | component matrices |
| `07 · Motion` | one frame per interaction: real screen looping at real speed, measured timings, filmstrip (75 frames) |
| `08 · Mobile`, `19 · Screens — Mobile` | mobile screens and states |
| `Components` | reusable canvas components |
| `09`–`15`, `17`, `18`, `21`, `22` · `Screens — <area>` | full-screen states, one page per product area, 20 to 110 frames each |
| `16 · Micro-interactions` | every interactive element in every state, visual |
| `23 · Chat UX system (reusable)` | parts cut from transcripts: status, work log, steps and tool calls, messages, cards, markdown and code, composer, rows |
| `24`–`27 · Live — <area>` | DOM snapshots of the live app: sidebar and composer, settings, thread and right sidebar, mobile |
| `28 · Kiko — …` | a second source app, captured the same way from a local build |
| `Archive — exact duplicate frames` | duplicates moved out of the way |

Frame names say what the state is in plain words: `Live · Composer model picker`, `Motion · Sidebar · Thread row hover`,
`Chat UX · 03 Steps, tool calls & reasoning (1/2)`. Use the same pattern.

## Setup

```bash
npm install                              # playwright-core
pip install -r requirements.txt          # pillow, numpy
export DSX_BASE_URL=https://app.example.com
export DSX_COOKIE_FILE=$HOME/.dsx/cookies.json   # Chrome cookie-export JSON; chmod 600; outside the repo
export DSX_WORK=$HOME/dsx-work/example            # every output goes here
export DSX_CANVAS=<target canvas id>              # ask the user, or create one named "<App> Design System"
export DOOP_TOKEN=<Doop API token>                # ask the user
export DSX_CDP=http://localhost:29229             # optional: reuse a running Chrome; unset launches headless Chromium
```

Keep a `NOTES.md` in the work dir and append to it after every step: what ran, what it produced, what is next.
Long runs outlive your context; the notes and the manifest are how you resume without redoing work.

## Workflow

Each step has a gate. Do not start the next step until the gate holds.

### 1. Prove the login
`node scripts/browser/probe.mjs /` prints the final URL and saves a screenshot. Open the screenshot.
**Gate:** the screenshot shows the signed-in app. A redirect to a sign-in page means the cookie export is incomplete
(PITFALLS 2). Stop and tell the user exactly which cookie is missing; do not continue with public pages.

### 2. Back up the canvas and read the tokens
```bash
python3 scripts/canvas/backup.py                       # only if the target canvas already has frames
node scripts/browser/tokens.mjs / /settings > /dev/null # writes tokens.json and tokens_local.css
```
`tokens.json` holds every CSS custom property the app ships, with its selector. Put them on the canvas with the
same names and values (`create_tokens`; read its schema with `doop_cli.py list-tools` first, this call is not scripted
here). **Gate:** token names on the canvas are identical to the app's. Zero tokens of your own.

### 3. Learn the app's vocabulary
`node scripts/browser/discover.mjs / /settings <a content page>` and again with `DSX_MOBILE=1`. It prints routes,
labelled controls, `data-*` attributes, slots, components, roles. Write scenarios from this output, not from guesses.
Then copy `references/coverage-checklist.md` to `$DSX_WORK/coverage.md` and mark each line: which scenario keys will
cover it, or `[-]` with the evidence that this app does not have it.
**Gate:** every checklist line has scenario keys or a `[-]` with evidence. Send the user this plan in a few lines.

### 4. Capture every state, in parallel
Write scenario files (shape in `scripts/browser/capture.mjs`, real examples in `examples/capy/`):
```js
export default [
  { key: 'sb_user_menu', group: 'sidebar', name: 'Live · User menu',
    steps: async (p) => { await p.locator('button[aria-label="Account"]').click(); } },
  { key: 'mob_new', group: 'mobile', name: 'Mobile · New chat', vp: { width: 390, height: 844 }, mobile: true },
];
```
`node scripts/browser/capture.mjs scenarios/sidebar.mjs 6` runs six isolated contexts at once. Each scenario writes
a self-contained DOM snapshot (`snaps/<key>.html`) and a live screenshot (`snaps/<key>.live.png`), the ground truth.
One scenario per state: each menu, each dialog, each hover that reveals something, each tab, each settings section,
each route, each of these again at 390×844.
**Gate:** `python3 scripts/canvas/live_sheet.py`, then open each sheet. Every capture shows the state its name says.
A menu that did not open is a failed capture: fix the selector and rerun that key (`capture.mjs file 6 key1,key2`).

### 5. Host embedded assets
`python3 scripts/canvas/hostassets.py`. Doop refuses frames with base64 `data:` URIs; this uploads each once and
rewrites the snapshots. **Gate:** it prints `left: 0` for every key.

### 6. Publish
Write `pages.json` mapping scenario groups to pages (format in `publish_snaps.py`), then
`python3 scripts/canvas/publish_snaps.py pages.json`. It is idempotent and records every frame in `manifest.json`.
**Gate:** `report.py` shows zero "captured but not published".

### 7. Verify against live
```bash
python3 scripts/canvas/sheets.py $DSX_CANVAS "Live"     # downloads the canvas renders, builds contact sheets
python3 scripts/canvas/diff_snaps.py                      # pixel-compares each frame with its live screenshot
```
Open every contact sheet. For each frame above the threshold, open both images side by side and find the cause.
**Gate:** every snapshot frame is viewed. Each failure is either fixed and re-verified or written down with its cause.

### 8. Cut the reusable parts
Write an extract job naming the parts by the app's own selectors (from step 3), run
`node scripts/browser/extract.mjs job.json out.json`, describe the sheets in `sheets.json`, then
`python3 scripts/canvas/build_sheets.py out.json sheets.json --publish`.
Extract deduplicates by structure, so each sheet shows every distinct variant once, as the real element with the real CSS.
Required sheets for a chat product: status and streaming indicators; activity line and work log; steps, tool calls and
reasoning (collapsed, open, running, failed); messages; question, approval, secret and other in-chat cards; markdown,
code and media; composer; transcript rows. **Gate:** open each published sheet. An `EMPTY section` line in the output
means the selector matched nothing: fix the selector or capture the missing state. Never fill it by hand.

### 9. Micro-interactions, visually
Run an extract job over interactive elements (`examples/jobs/states.job.json`), then
`python3 scripts/canvas/build_states.py out_states.json --publish`. Each row is one real element at rest, hover,
focus-visible, active, disabled, with its state attributes flipped, plus a cell that loops hover.
A table of class names or CSS text is not acceptable as the micro-interaction deliverable.
**Gate:** open the sheets; hover, focus and disabled columns visibly differ from rest wherever the app defines them.

### 10. Motion: one frame per interaction
Write motion scenarios (`examples/capy/sc_motion.mjs`): `setup` puts the app in the state before, `trigger` does the
one action and returns the element it acted on.
```bash
node scripts/browser/motion.mjs scenarios/motion.mjs 5
python3 scripts/canvas/build_motion.py --page-name "07 · Motion"
```
`motion.mjs` slows animations to 2% through CDP, reads each transition's real property, duration, delay and easing
from the Web Animations API, and screenshots the full screen at six evenly spaced times. `build_motion.py` turns that
into a frame: the real screen looping at real speed, the measured table, and a zoomed filmstrip with an 8× slower loop.
Cover every interaction the app has, and both directions where they differ: hover on each row and control type;
every menu, picker, popover, tooltip, dialog and sheet opening and closing; expand and collapse; tab switch; route change;
focus; typing; copy feedback; scroll-triggered UI; drag affordances; streaming and loading indicators.
Expect 50 or more frames for a product of normal size.
**Gate:** `report.py` lists motion captures with no measured transition. For each, open the frame: either the change
really is instant (say so) or the capture missed it (fix `wait` or the trigger and rerun). In every "opens" frame the
filmstrip must show the whole popup, and the table must include the popup's own rows, not only the trigger's.

### 11. Mobile
Mobile is a full pass, not a sample: every scenario group again at 390×844 with `mobile: true` (sheets and drawers
replace menus, the sidebar becomes a drawer). **Gate:** same as steps 4 to 7. If text renders at a different size on the
canvas than live, see PITFALLS 9 and report it; do not hide it.

### 12. Archive duplicates
`python3 scripts/canvas/archive_dups.py` prints the plan; add `--apply` to move byte-identical frames to an Archive
page. Give the user `archive_report.json`. Never delete.

### 13. Report
`python3 scripts/canvas/report.py` after marking what you looked at (`report.py --viewed-page <page_key>`).
Use the format in **Reporting** below.

## Definition of done

All of these hold, and you can show the evidence for each:

- `coverage.md` has no open `[ ]` line. Every `[-]` line carries evidence.
- `report.py`: published = viewed for every page; every not-passed frame has a written cause.
- Motion: one frame per interaction on the coverage list; none with an unexplained empty timing table.
- Mobile pages exist for every product area that desktop pages exist for.
- Micro-interaction sheets are visual.
- No frame contains product UI you wrote by hand. No token on the canvas is absent from `tokens.json`.
- Nothing pre-existing on the canvas was deleted or overwritten.
- The account is in the state you found it.

If one does not hold, the work is not done. Say which, and keep going or ask.

## Reporting

Short, and the same shape every time:

1. One sentence: what is on the canvas now and what is not right yet.
2. A table from `report.py`: page, frames, viewed, passed.
3. **Not right yet:** each failure, one line, with the cause if known.
4. **Missing:** each thing you could not capture and why.
5. **Decisions for the user:** only real ones, for example anything that needs a change to their account.

Attach the contact sheets. Do not describe the method unless asked.

## How this goes wrong

These are the actual mistakes made before this skill existed. Each one cost the user a round of corrections.

- Reading the wrong source (a small prototype instead of the real product) and building on it.
- Redrawing UI "to match" and adding invented tokens, themes and type scales.
- Summarising a deep system (composer, chat steps, sidebar) as one tidy board.
- Picking a subset of states by keyword instead of covering the list.
- Adding new frames beside old wrong ones instead of replacing them.
- Reporting completion from frame counts without opening the frames.
- Treating a table of CSS classes as a micro-interaction spec.
- Capturing a "menu opens" motion before the menu's own animation had started.

More, with symptoms and fixes, in `PITFALLS.md`. Script reference in `README.md`.
