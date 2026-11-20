// Step 4. Scenario runner: one isolated browser context per scenario, N in parallel.
// usage: node capture.mjs <scenarios.mjs> [workers=6] [key1,key2]
// A scenario is { key, name, group, url?, vp?, mobile?, settle?, steps?(page), after? }.
// Output per scenario: $DSX_WORK/snaps/<key>.html (self-contained DOM snapshot) + <key>.live.png (ground truth) + index.json row.
import { connect, newCtx, abs, redact, loadModule, WORK } from './lib.mjs';
import { snapshot } from './snap.mjs';
import fs from 'fs';
const mod = await loadModule(process.argv[2]);
const only = process.argv[4] ? new Set(process.argv[4].split(',')) : null;
const scenarios = mod.default.filter(s => !only || only.has(s.key)); const workers = +(process.argv[3] || 6);
const OUT = WORK + '/snaps'; fs.mkdirSync(OUT, { recursive: true });
const b = await connect(); const queue = [...scenarios]; const results = [];
async function worker() {
  while (queue.length) {
    const s = queue.shift(); const vp = s.vp || { width: 1600, height: 1000 };
    const ctx = await newCtx(b, vp, s.mobile ? { isMobile: true, hasTouch: true } : {});
    const p = await ctx.newPage();
    try {
      await p.goto(abs(s.url || '/'), { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForTimeout(s.settle || 5000);
      if (s.steps) await s.steps(p);
      await p.waitForTimeout(s.after ?? 700);
      const snap = await snapshot(p);
      fs.writeFileSync(`${OUT}/${s.key}.html`, snap.html);
      await p.screenshot({ path: `${OUT}/${s.key}.live.png` });
      results.push({ key: s.key, name: s.name, group: s.group, w: vp.width, h: vp.height, bytes: snap.html.length, url: redact(snap.url), ok: true });
      console.log('ok', s.key, snap.html.length);
    } catch (e) { results.push({ key: s.key, name: s.name, group: s.group, ok: false, err: String(e).slice(0, 160) }); console.log('FAIL', s.key, String(e).slice(0, 160)); }
    await ctx.close();
  }
}
await Promise.all(Array.from({ length: workers }, worker));
const idxPath = `${OUT}/index.json`; const idx = fs.existsSync(idxPath) ? JSON.parse(fs.readFileSync(idxPath, 'utf8')) : {};
for (const r of results) idx[r.key] = r;
fs.writeFileSync(idxPath, JSON.stringify(idx, null, 1));
console.log('done', results.filter(r => r.ok).length, '/', results.length);
await b.close();
