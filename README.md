# design-system-extract-skill

A skill and a toolkit for extracting the design system of a live web app onto a [Doop](https://doop.design) canvas:
every screen and state as real DOM, the components cut out of those screens, every interactive state, and every motion
with measured timings. Nothing is redrawn.

Start with [`SKILL.md`](SKILL.md). It is written for an agent and contains the rules, the workflow with a gate per
step, the definition of done and the report format. [`PITFALLS.md`](PITFALLS.md) lists what went wrong before and how
to avoid it. [`references/coverage-checklist.md`](references/coverage-checklist.md) is the inventory to cover.

Reference result: Doop canvas `tnKVYw9CeC`.

## How it works

| Idea | What it replaces |
|---|---|
| **DOM snapshot** (`snap.mjs`): inline the CSSOM, freeze canvases to images, keep `<html>`/`<body>` attributes | screenshots (not inspectable) and hand-rebuilt screens (not faithful) |
| **Scenario files** run in parallel isolated contexts, cookie injected (`capture.mjs`) | clicking through the app one state at a time |
| **Live screenshot per capture** as ground truth, **pixel diff** against the canvas render (`diff_snaps.py`) | "it looks right to me" |
| **Structural dedupe** when cutting parts out of captures (`extract.mjs`) | choosing examples by hand |
| **Forced-state CSS**: the site's own `:hover`/`:focus` rules duplicated as classes (`sheetlib.css_text`) | writing state styles |
| **Slow-motion capture**: CDP playback rate 2%, Web Animations API for timings, seek and screenshot (`motion.mjs`) | describing motion in words or CSS tables |
| **Manifest** with one row per frame: published, viewed, passed (`report.py`) | frame counts |
| **Archive page** for byte-identical frames (`archive_dups.py`) | deleting |

## Scripts

Browser side (Node, Playwright). Environment: `DSX_BASE_URL`, `DSX_COOKIE_FILE`, `DSX_WORK`, optional `DSX_CDP`, `DSX_COLOR_SCHEME`.

| Script | Does |
|---|---|
| `scripts/browser/probe.mjs` | proves the cookie signs in |
| `scripts/browser/discover.mjs` | prints routes, labelled controls, `data-*` vocabulary |
| `scripts/browser/tokens.mjs` | dumps every CSS custom property the app ships |
| `scripts/browser/capture.mjs` | runs scenarios in parallel, writes snapshot + live screenshot |
| `scripts/browser/snap.mjs` | the snapshot function |
| `scripts/browser/extract.mjs` | cuts deduplicated parts and the union CSS out of captures |
| `scripts/browser/motion.mjs` | measures and films one interaction per scenario |
| `scripts/browser/render.mjs` | renders a built sheet locally and measures its height |

Canvas side (Python). Environment: `DOOP_TOKEN`, `DSX_CANVAS`, `DSX_WORK`.

| Script | Does |
|---|---|
| `scripts/canvas/backup.py` | saves the canvas and every frame's HTML |
| `scripts/canvas/live_sheet.py` | contact sheet of live screenshots, before publishing |
| `scripts/canvas/hostassets.py` | uploads embedded images, rewrites snapshots |
| `scripts/canvas/publish_snaps.py` | publishes snapshots to pages by group |
| `scripts/canvas/sheets.py` | contact sheets of the canvas renders |
| `scripts/canvas/diff_snaps.py` | compares canvas renders with live screenshots |
| `scripts/canvas/build_sheets.py` | component sheets from `extract.mjs` output |
| `scripts/canvas/build_states.py` | visual state sheets for interactive elements |
| `scripts/canvas/build_motion.py` | motion frames from `motion.mjs` output |
| `scripts/canvas/archive_dups.py` | moves byte-identical frames to an Archive page |
| `scripts/canvas/report.py` | the status report; marks frames viewed |
| `scripts/canvas/sheetlib.py`, `doop_cli.py` | shared helpers, Doop client |

## What has been tested

Every script was run end to end against two different apps: a hosted chat product behind cookie login, and a local
build of a second app, publishing to a scratch set of pages that was removed afterwards.

Not covered by a script, or not solved:
- Putting tokens on the canvas (`create_tokens`) is left to the agent.
- Mobile type size can differ between the live capture and the canvas render (PITFALLS 9).
- Interactions driven by script rather than CSS transitions get a before/after pair without a timing table.

## Secrets

No cookie, token or captured account data belongs in this repo. `.gitignore` excludes the usual names; keep the
cookie file and the work directory outside the checkout.
