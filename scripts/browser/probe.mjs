// Step 1. Prove the cookie signs you in BEFORE anything else.
// usage: node probe.mjs <path-or-url> [...]   prints status, final URL, title and saves probe_*.png in $DSX_WORK
// Signed in  = final URL stays inside the app.  Not signed in = redirect to a sign-in page (see PITFALLS.md #2).
import { connect, newCtx, abs, redact, WORK } from './lib.mjs';
const b = await connect(); const ctx = await newCtx(b); const p = await ctx.newPage();
for (const u of process.argv.slice(2).length ? process.argv.slice(2) : ['/']) {
  try {
    const resp = await p.goto(abs(u), { waitUntil: 'domcontentloaded', timeout: 45000 });
    await p.waitForTimeout(6000);
    console.log(u, '->', resp?.status(), redact(p.url().replace(/\?.*/, '')), '|', await p.title());
    await p.screenshot({ path: `${WORK}/probe_${u.replace(/[^a-z0-9]+/gi, '_')}.png` });
  } catch (e) { console.log(u, 'ERR', String(e).slice(0, 150)); }
}
await ctx.close(); await b.close();
