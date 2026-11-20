// Step 8. Cut reusable parts out of captured screens.
// usage: node extract.mjs job.json out.json
//   job = { frames: [...], targets: [{ key, sel, mode?, maxW?, maxH?, cap? }], maxHtml?, workers? }
//   frames: snapshot keys (reads $DSX_WORK/snaps/<key>.html), paths to .html files, or canvas frame ids (reads backup/frames/<id>.json)
//   mode: default = dedupe by structure (slot/component/state attrs of the subtree); "class" = by class list + state; "verb" = structure + first word + icons
// Output: { css: union of every stylesheet rule seen, in cascade order, variants: { key: { signature: { html, w, h, st, bgColor, inherit, frameName, n } } } }
import { connect, WORK, SCHEME } from './lib.mjs';
import path from 'path';
import fs from 'fs';
const [jobPath, outPath] = process.argv.slice(2);
const job = JSON.parse(fs.readFileSync(jobPath, 'utf8'));
const tok = fs.existsSync(WORK + '/tokens_local.css') ? fs.readFileSync(WORK + '/tokens_local.css', 'utf8') : '';
const readSrc = (id) => {
  const f = id.endsWith('.html') ? id : fs.existsSync(`${WORK}/snaps/${id}.html`) ? `${WORK}/snaps/${id}.html` : null;
  if (f) return { html: fs.readFileSync(f, 'utf8'), name: path.basename(f, '.html') };
  return JSON.parse(fs.readFileSync(`${WORK}/backup/frames/${id}.json`, 'utf8'));
};
const b = await connect();
const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1, colorScheme: SCHEME });
const master = []; const mIndex = new Map();
const variants = {}; // key -> sig -> rec
const inPage = ({ targets, maxHtml }) => {
  const flat = [];
  const walk = (rules, chain) => {
    for (const r of rules) {
      const T = r.constructor.name;
      if (T === 'CSSStyleRule') {
        const decl = r.style.cssText;
        if (decl) flat.push([chain, `${r.selectorText}{${decl}}`]);
        if (r.cssRules && r.cssRules.length) walk(r.cssRules, [...chain, r.selectorText]);
      } else if (T === 'CSSNestedDeclarations') {
        flat.push([chain, r.style.cssText]);
      } else if (r.cssRules && T !== 'CSSKeyframesRule') {
        const pre = r.cssText.slice(0, r.cssText.indexOf('{')).trim();
        walk(r.cssRules, [...chain, pre]);
      } else flat.push([chain, r.cssText]);
    }
  };
  for (const s of document.styleSheets) { if (s.ownerNode && s.ownerNode.id === '__tok') continue; try { walk(s.cssRules, []); } catch (e) {} }
  const STATE = ['data-state', 'data-panel-open', 'data-open', 'data-closed', 'data-status', 'data-tone', 'data-selected', 'data-active', 'data-unfocused', 'aria-expanded', 'aria-selected', 'aria-pressed', 'aria-checked', 'aria-current', 'disabled', 'data-disabled', 'data-popup-open', 'data-pressed', 'data-hinted', 'data-kind', 'data-variant', 'data-size', 'data-side', 'data-checked', 'data-highlighted', 'data-orientation'];
  const h = (s) => { let x = 5381; for (let i = 0; i < s.length; i++) x = ((x << 5) + x + s.charCodeAt(i)) | 0; return (x >>> 0).toString(36); };
  const stOf = (e) => STATE.filter(k => e.hasAttribute(k)).map(k => k.replace(/^data-|^aria-/, '') + (e.getAttribute(k) ? '=' + e.getAttribute(k) : '')).join(' ');
  const structSig = (el) => {
    const parts = [];
    const w = (e, d) => {
      if (d > 7) return;
      const s = e.getAttribute('data-slot') || e.getAttribute('data-component') || '';
      const st = stOf(e);
      if (s || st || d === 0) { const p = d + ':' + e.tagName + ':' + s + ':' + st; if (parts[parts.length - 1] !== p) parts.push(p); }
      for (const c of e.children) { if (c.hasAttribute('data-d') || c.hasAttribute('data-c') || c.tagName === 'circle') continue; w(c, d + 1); }
    };
    w(el, 0); return h(parts.join('|'));
  };
  const out = [];
  const seen = new Set();
  for (const t of targets) {
    let els; try { els = document.querySelectorAll(t.sel); } catch (e) { continue; }
    for (const el of els) {
      let r = el.getBoundingClientRect();
      if (r.width < 2 || r.height < 1) continue;
      if (t.maxW && (r.width > t.maxW || r.height > t.maxH)) continue;
      const verb = () => { const tx = (el.innerText || '').trim(); const w1 = (tx.match(/^[A-Za-z']+/) || [''])[0]; return w1 + '|' + el.querySelectorAll('svg').length + '|' + (el.querySelector('pre,code') ? 'code' : '') + '|' + [...el.querySelectorAll('[class*="destructive"],[class*="success"],[class*="warning"]')].length; };
      const sig = t.mode === 'class' ? h((el.getAttribute('class') || '') + '|' + stOf(el)) : t.mode === 'verb' ? h(structSig(el) + '|' + verb()) : structSig(el);
      const k = t.key + '§' + sig; if (seen.has(k)) continue; seen.add(k);
      let bgClass = '', bgColor = '';
      for (let a = el.parentElement; a; a = a.parentElement) {
        const c = getComputedStyle(a).backgroundColor; const m = c.match(/rgba?\(([^)]+)\)/);
        const alpha = m ? (m[1].split(/[,/ ]+/).filter(Boolean)[3] ?? '1') : '1';
        if (c && c !== 'transparent' && parseFloat(alpha) > 0.5) { bgColor = c; bgClass = [...a.classList].find(x => /^bg-[a-z-]+$/.test(x)) || ''; break; }
      }
      const pc = getComputedStyle(el.parentElement || el);
      const html = el.outerHTML;
      out.push({ key: t.key, sig, w: Math.round(r.width), h: Math.round(r.height), len: html.length, st: stOf(el), bgClass, bgColor,
        inherit: { color: pc.color, fontSize: pc.fontSize, lineHeight: pc.lineHeight, fontWeight: pc.fontWeight, letterSpacing: pc.letterSpacing },
        text: (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 70), html: html.length <= maxHtml ? html : null });
    }
  }
  const root = document.querySelector('.cds-root') || document.documentElement;
  const at = (el) => [...el.attributes].filter(a => a.name === 'class' || a.name === 'style' || a.name === 'dir' || a.name === 'lang' || a.name.startsWith('data-')).map(a => `${a.name}="${a.value.replace(/&/g, '&amp;').replace(/"/g, '&quot;')}"`).join(' ');
  const bcs = getComputedStyle(document.body); let bg = bcs.backgroundColor; if (!bg || bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') bg = getComputedStyle(document.documentElement).backgroundColor;
  return { flat, out, rootClass: root ? root.className : '', rootTheme: root ? root.getAttribute('data-color-theme') : '', page: { htmlAttrs: at(document.documentElement), bodyAttrs: at(document.body), bg, color: bcs.color, font: bcs.fontFamily, fontSize: bcs.fontSize, lineHeight: bcs.lineHeight, links: [...document.querySelectorAll('link[rel=stylesheet][href^="http"]')].map(l => l.href) } };
};
function mergeCss(flat) {
  let pos = -1;
  for (const [chain, text] of flat) {
    const k = chain.join('§') + '§§' + text;
    const i = mIndex.get(k);
    if (i !== undefined) { if (i > pos) pos = i; continue; }
    pos += 1; master.splice(pos, 0, { chain, text, k });
    for (let j = pos; j < master.length; j++) mIndex.set(master[j].k, j);
  }
}
const capOf = Object.fromEntries(job.targets.map(t => [t.key, t.cap || 1e9]));
const queue = [...job.frames]; let done = 0; const roots = {}; let pageRoot = null;
async function worker() {
  const p = await ctx.newPage();
  while (queue.length) {
    const id = queue.shift();
    try {
      const j = readSrc(id);
      await p.setViewportSize({ width: j.width || 1600, height: Math.min(j.height || 1000, 1400) });
      await p.setContent(j.html, { waitUntil: 'domcontentloaded', timeout: 60000 });
      if (tok) await p.addStyleTag({ content: tok }).then(h => h.evaluate(n => { n.id = '__tok'; }));
      await p.waitForTimeout(150);
      const r = await p.evaluate(inPage, { targets: job.targets, maxHtml: job.maxHtml || 60000 });
      mergeCss(r.flat);
      roots[r.rootClass + '|' + r.rootTheme] = (roots[r.rootClass + '|' + r.rootTheme] || 0) + 1; if (!pageRoot) pageRoot = r.page;
      for (const c of r.out) {
        const m = (variants[c.key] ||= {});
        const e = m[c.sig];
        if (!e) { if (Object.keys(m).length >= capOf[c.key]) continue; m[c.sig] = { ...c, frame: id, frameName: j.name, n: 1 }; }
        else { e.n++; if (!e.html && c.html) Object.assign(e, c, { frame: id, frameName: j.name, n: e.n }); }
      }
    } catch (e) { console.log('ERR', id, String(e).slice(0, 200)); }
    if (++done % 25 === 0) console.log('done', done, 'css rules', master.length);
  }
  await p.close();
}
await Promise.all(Array.from({ length: job.workers || 6 }, worker));
fs.writeFileSync(outPath, JSON.stringify({ css: master.map(({ chain, text }) => [chain, text]), variants, roots, root: pageRoot }));
console.log('frames', done, 'css rules', master.length, 'keys', Object.keys(variants).length, 'variants', Object.values(variants).reduce((a, m) => a + Object.keys(m).length, 0), 'roots', roots);
await ctx.close(); await b.close();
