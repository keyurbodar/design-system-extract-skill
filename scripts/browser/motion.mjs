// Step 10. Measure and film one interaction per scenario, on the live app.
// usage: node motion.mjs <scenarios.mjs> [workers=4] [key1,key2]
// A scenario is { key, name, group, how, url?, settle?, setup?(page), trigger(page) -> locator|null, wait?, end? }.
// Method: slow all animations to 2% speed through CDP, fire the trigger, wait until the set of new animations stops growing,
// read each one's real property / duration / delay / easing from the Web Animations API, pause them, then seek to
// 6 evenly spaced times and take a full-screen screenshot at each. Output: $DSX_WORK/motion/<key>/f0..fN.png + meta.json.
import { connect, newCtx, abs, loadModule, WORK } from './lib.mjs';
import fs from 'fs';
const mod = await loadModule(process.argv[2]);
const only = process.argv[4] ? new Set(process.argv[4].split(',')) : null;
const list = mod.default.filter(s => !only || only.has(s.key)); const workers = +(process.argv[3] || 4);
const OUT = WORK + '/motion'; const N = 6;
const POPUP = '[role=menu],[role=dialog],[role=listbox],[role=tooltip],[role=alertdialog],[data-popup],[popover]';
const b = await connect(); const queue = [...list]; let ok = 0;
const freshCount = () => document.getAnimations().filter(a => { if (!a.effect || (window.__pre && window.__pre.has(a)) || a.playState === 'finished') return false; const t = a.effect.getComputedTiming(); return typeof t.duration === 'number' && t.iterations !== Infinity && t.duration > 0 && t.duration <= 3000; }).length;
const collect = (popupSel) => {
  const desc = (el) => { if (!el) return '?'; const s = el.getAttribute('data-slot') || el.getAttribute('data-component') || el.getAttribute('data-testid'); const r = el.getAttribute('role'); const c = (el.getAttribute('class') || '').split(/\s+/).filter(x => x && !x.includes(':') && !x.includes('[')).slice(0, 2).join('.'); return (s ? `[${s}] ` : '') + el.tagName.toLowerCase() + (r ? `[${r}]` : '') + (!s && c ? '.' + c : ''); };
  const an = document.getAnimations().filter(a => { if (!a.effect || (window.__pre && window.__pre.has(a)) || a.playState === 'finished') return false; const t = a.effect.getComputedTiming(); return typeof t.duration === 'number' && t.iterations !== Infinity && t.duration > 0 && t.duration <= 3000; });
  const rows = [];
  for (const a of an) {
    const t = a.effect.getComputedTiming(); const el = a.effect.target; if (!el) continue;
    a.pause(); const r = el.getBoundingClientRect();
    rows.push({ rect: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)], el: desc(el), type: a.constructor.name.replace('CSS', '').toLowerCase(), prop: a.transitionProperty || a.animationName || '', dur: Math.round(t.duration), delay: Math.round(t.delay), ease: t.easing, end: t.delay + t.duration });
  }
  window.__an = an;
  const popups = [...document.querySelectorAll(popupSel)].filter(e => !(window.__prePop && window.__prePop.has(e))).map(e => e.getBoundingClientRect()).filter(r => r.width > 2 && r.height > 2).map(r => [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]);
  return { rows, popups, T: rows.reduce((m, r) => Math.max(m, r.end), 0) };
};
async function runOne(s) {
  const dir = `${OUT}/${s.key}`; fs.mkdirSync(dir, { recursive: true });
  const ctx = await newCtx(b, s.vp); const p = await ctx.newPage(); const cdp = await ctx.newCDPSession(p);
  try {
    await p.goto(abs(s.url || '/'), { waitUntil: 'domcontentloaded', timeout: 60000 });
    await p.waitForTimeout(s.settle || 5000);
    if (s.setup) { await s.setup(p); await p.waitForTimeout(900); }
    await p.screenshot({ path: `${dir}/f0.png` });
    await cdp.send('Animation.enable'); await cdp.send('Animation.setPlaybackRate', { playbackRate: 0.02 });
    await p.evaluate((sel) => { window.__pre = new WeakSet(document.getAnimations()); window.__prePop = new WeakSet(document.querySelectorAll(sel)); }, POPUP);
    const tb = await s.trigger(p);
    if (s.wait) await p.waitForTimeout(s.wait);
    else { // wait until new animations exist and their count is stable for 300ms (popups mount late)
      let last = -1, stable = 0;
      for (let i = 0; i < 40; i++) { await p.waitForTimeout(60); const n = await p.evaluate(freshCount); if (n > 0 && n === last) { if (++stable >= 5) break; } else stable = 0; last = n; }
    }
    const info = await p.evaluate(collect, POPUP);
    let frames = 1;
    if (info.T > 0) {
      for (let i = 1; i <= N; i++) {
        await p.evaluate(([T, f]) => { for (const a of window.__an) { try { const t = a.effect.getComputedTiming(); a.currentTime = Math.min(T * f, t.delay + t.duration); } catch (e) {} } }, [info.T, i / N]);
        await p.waitForTimeout(40); await p.screenshot({ path: `${dir}/f${i}.png` }); frames++;
      }
      await p.evaluate(() => { for (const a of window.__an) { try { a.finish(); } catch (e) {} } });
    }
    await cdp.send('Animation.setPlaybackRate', { playbackRate: 1 });
    await p.waitForTimeout(s.end ?? 700);
    await p.screenshot({ path: `${dir}/f${frames}.png` }); frames++;
    let tbox = null; try { tbox = tb && tb.boundingBox ? await tb.boundingBox() : null; } catch (e) {}
    const vp = p.viewportSize();
    const seen = new Set(); const rects = info.rows.map(r => ({ prop: r.prop, rect: r.rect })).concat(info.popups.map(r => ({ prop: 'popup', rect: r })));
    const rows = info.rows.filter(r => { const k = [r.el, r.prop, r.dur, r.delay, r.ease].join('|'); if (seen.has(k)) return false; seen.add(k); return true; }).map(({ rect, end, ...r }) => r);
    fs.writeFileSync(`${dir}/meta.json`, JSON.stringify({ key: s.key, name: s.name, group: s.group, trigger: s.how, frames, T: Math.round(info.T), w: vp.width, h: vp.height, rows, rects, tbox }, null, 1));
    console.log('ok', s.key, 'frames', frames, 'T', Math.round(info.T), 'transitions', rows.length, 'popups', info.popups.length); ok++;
  } catch (e) { console.log('FAIL', s.key, String(e).slice(0, 170)); }
  await ctx.close();
}
async function worker() { while (queue.length) await runOne(queue.shift()); }
await Promise.all(Array.from({ length: workers }, worker));
console.log('done', ok, '/', list.length); await b.close();
