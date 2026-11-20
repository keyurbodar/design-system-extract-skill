# Pitfalls

Each of these happened. Symptom, cause, fix.

## 1. Wrong source of truth
**Symptom:** geometry and components differ from the real product. **Cause:** work started from a small prototype
canvas and a zip archive instead of the full canvas and the running app. **Fix:** confirm the source with the user
before step 1: the URL, the account, and for a canvas its id plus page and frame count.

## 2. The cookie export does not sign you in
**Symptom:** `probe.mjs` lands on a sign-in page. **Cause:** the export held only a short-lived session token (a JWT
that expires in about a minute) and missed the long-lived, httpOnly cookie on the auth provider's own domain
(Clerk keeps `__client` on `clerk.<domain>`). **Fix:** ask for an export that includes the auth subdomain's cookies, or
for the user to sign in once in your browser. Check which host the app really runs on; the documented one may 404.
Inspect cookie names, domains and JWT expiry only. Never print values.

## 3. Doop refuses frames with base64 data URIs
**Symptom:** `create_frame` fails with "this HTML embeds N base64 data: URIs". **Cause:** snapshots inline canvas
pixels and small images. **Fix:** `hostassets.py` (upload once, cache by sha1, rewrite). Uploads are limited to 15 a
minute per account; the script throttles. Motion sprites go through the same uploader.

## 4. HTTP 429 when downloading frame renders
**Cause:** more than about five parallel requests to `doop.design/i/<id>.png`. **Fix:** `sheets.py` uses five workers
and retries. If a render is still missing, rerun; do not mark the frame viewed.

## 5. Two publishers, one manifest
**Symptom:** a frame gets published twice. **Cause:** two scripts rewrote `manifest.json` at the same time and one
row was lost. **Fix:** all writes go through `sheetlib.state_update()`, which holds a file lock. Keep it that way in
any script you add. After a crash, compare `get_canvas` with the manifest and delete only frames you created.

## 6. Motion table misses the popup's own transition
**Symptom:** a "menu opens" frame lists only the trigger button's colour transition, and the filmstrip crops around
the button. **Cause:** animations were collected before the popup had mounted. **Fix (in `motion.mjs`):** wait until the
number of new animations has been stable for 300ms, and record the rectangles of popups that appeared.
If a frame still looks like this, give the scenario an explicit `wait`.

## 7. Animations that are not interactions
**Symptom:** `NaN` durations or dozens of identical rows. **Cause:** scroll-driven animations report a non-numeric
duration; infinite loops (spinners, shimmer) never end. **Fix:** `motion.mjs` skips non-numeric and infinite timings and
anything that was already running before the trigger. Film looping indicators as their own scenario with a fixed `wait`.

## 8. `<canvas>` content is blank in snapshots
**Cause:** canvas pixels are not in the DOM. **Fix:** `snap.mjs` screenshots each canvas and swaps in an image.
Animated canvases (dither, shaders) make the pixel diff noisy; judge those frames by eye.

## 9. Mobile text renders smaller on the canvas than live
**Symptom:** layout matches but type is smaller; the diff fails. **Status: not solved.** Rewriting
`(pointer: coarse)` media queries did not fix it on the app where it appeared; another app passed unchanged.
Next things to try: capture with `mobile: false` at the same viewport and compare; look for touch-only classes or
attributes set by script on `<html>`. Until solved, report the affected frames; do not mark them passed.

## 10. Fonts served from the app's own origin
**Symptom:** fallback fonts on the canvas. **Cause:** `@font-face` URLs that need the app's cookies or point at
localhost. **Fix:** upload the font files with Doop `upload_font` (then delete the snapshot's own `@font-face` rule for
that family), or point the rule at a public CDN copy of the same file.

## 11. Local render height cap
**Symptom:** a tall sheet's screenshot is cut. **Cause:** `render.mjs` caps screenshots at 12000px. **Fix:**
`build_sheets.py` splits sheets above `max_height`; keep sheets under about 14000px so they can be reviewed.

## 12. Tool results that are not plain JSON
**Symptom:** a successful `create_frame` is reported as a failure. **Cause:** the response is JSON followed by text.
**Fix:** `sheetlib.call()` decodes the leading JSON value. Use it for every Doop call.

## 13. Capture names that lie
**Symptom:** a frame called "… menu" shows no menu. **Cause:** the selector matched nothing or the click raced the
render, and the step swallowed the error. **Fix:** do not wrap steps in try/catch; let the scenario fail, read the
`FAIL` line, fix the selector from `discover.mjs` output, rerun that key. Always open `live_sheet.py` output.

## 14. Site CSS that only applies under real input
`@media (hover: hover)` and `:hover` rules cannot be triggered in a static frame. `css_text()` duplicates every
`:hover`, `:focus-visible`, `:focus-within`, `:active` and `:disabled` rule as a `.is-…` class rule and drops the
hover media wrapper, so a state can be shown by adding a class. Use it; do not write state styles.

## 15. Sheet chrome borrowing product tokens
Captions and titles on sheets must not use the product's tokens or fonts, or they read as part of the product.
`sheetlib.SHEET_CSS` uses system fonts and colours mixed from the page's own background and text colour.

## 16. Identical frames that look like different states
Hover and focus states captured without the pointer over the element, or theme pages captured before the theme
applied, produce byte-identical frames under different names. `archive_dups.py` finds them. Treat each group as a
state that was never captured, and capture it properly.

## 17. Real account data on the canvas
Live snapshots contain the user's real content. Tell the user in the first report and ask whether to keep it.
Do not rewrite content on your own; replacing text is inventing.

## 18. Local or gated apps
A local build may refuse to start or sign in until its dev secrets are non-empty, and may gate every route behind
onboarding. Set local-only values in the gitignored env file; flip onboarding through the app's own command or API in
the capture context. Capture the onboarding steps before you pass them. Never edit the app's source to get a screenshot.
