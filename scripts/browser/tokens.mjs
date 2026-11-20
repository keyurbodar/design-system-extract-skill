// Step 2b. Read the design tokens the app actually ships: every CSS custom property, with the selector that sets it.
// usage: node tokens.mjs <path> [...] > tokens.json     (also writes $DSX_WORK/tokens.json and tokens_local.css)
// Groups: selectors like :root / html / body are the base theme; anything else (.dark, [data-theme=x]) is a theme override.
// Copy these names and values exactly. Do not rename, round, merge or invent tokens.
import { connect, newCtx, abs, WORK } from './lib.mjs';
import fs from 'fs';
const b = await connect(); const ctx = await newCtx(b); const p = await ctx.newPage(); const all = {};
for (const u of process.argv.slice(2).length ? process.argv.slice(2) : ['/']) {
  await p.goto(abs(u), { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(5000);
  const ext = await p.evaluate(() => [...document.styleSheets].filter(s => { try { s.cssRules; return false; } catch { return !!s.href; } }).map(s => s.href));
  for (const href of ext) { try { await p.addStyleTag({ content: await (await p.request.get(href)).text() }); } catch {} }
  const found = await p.evaluate(() => {
    const out = []; const walk = (rules, ctx) => { for (const r of rules) {
      if (r.style && r.selectorText) { for (const name of r.style) if (name.startsWith('--')) out.push({ name, value: r.style.getPropertyValue(name).trim(), selector: r.selectorText, context: ctx }); }
      if (r.cssRules && r.constructor.name !== 'CSSKeyframesRule') walk(r.cssRules, r.selectorText ? ctx : (ctx ? ctx + ' ' : '') + r.cssText.slice(0, r.cssText.indexOf('{')).trim()); } };
    for (const s of document.styleSheets) { try { walk(s.cssRules, ''); } catch {} }
    const cs = getComputedStyle(document.documentElement); const resolved = {};
    for (const t of out) if (!(t.name in resolved)) resolved[t.name] = cs.getPropertyValue(t.name).trim();
    return { out, resolved };
  });
  for (const t of found.out) { const k = t.name + '§' + t.selector + '§' + t.context; if (!all[k]) all[k] = { ...t, resolved: found.resolved[t.name] || '' }; }
}
const list = Object.values(all); const base = /^(:root|html|body|:host)(,|\s|$)/;
const type = (v) => /^(#|rgb|hsl|oklch|oklab|lab|lch|color\()/.test(v) ? 'color' : /^-?[\d.]+(px|rem|em|%)$/.test(v) ? 'dimension' : /^[\d.]+m?s$/.test(v) ? 'duration' : /^cubic-bezier|^ease|^linear/.test(v) ? 'easing' : /^[\d.]+$/.test(v) ? 'number' : 'other';
const result = { base: list.filter(t => base.test(t.selector) && !t.context).map(t => ({ ...t, type: type(t.resolved || t.value) })), themed: list.filter(t => !(base.test(t.selector) && !t.context)) };
fs.writeFileSync(WORK + '/tokens.json', JSON.stringify(result, null, 1));
fs.writeFileSync(WORK + '/tokens_local.css', ':root{' + result.base.map(t => `${t.name}:${t.value};`).join('') + '}');
const byType = {}; for (const t of result.base) byType[t.type] = (byType[t.type] || 0) + 1;
console.error('base tokens', result.base.length, byType, '| scoped overrides (themes and components)', result.themed.length, '| selectors', [...new Set(result.themed.map(t => t.selector))].slice(0, 12));
console.log(JSON.stringify(result, null, 1));
await ctx.close(); await b.close();
