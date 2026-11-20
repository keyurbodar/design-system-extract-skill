// Step 3. Read the app's own vocabulary so scenarios use real selectors instead of guesses.
// usage: node discover.mjs <path> [...]   (desktop)   |   DSX_MOBILE=1 node discover.mjs <path> ...
// Prints, per page: internal routes, labelled controls, data-* attribute names, data-slot/data-component/data-testid values, roles.
import { connect, newCtx, abs } from './lib.mjs';
const mobile = !!process.env.DSX_MOBILE;
const b = await connect();
const ctx = await newCtx(b, mobile ? { width: 390, height: 844 } : undefined, mobile ? { isMobile: true, hasTouch: true } : {});
const p = await ctx.newPage();
for (const u of process.argv.slice(2).length ? process.argv.slice(2) : ['/']) {
  await p.goto(abs(u), { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(6000);
  const info = await p.evaluate(() => {
    const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.right > 0 && r.left < innerWidth; };
    const uniq = (a) => [...new Set(a)];
    const attrs = {}; const vals = { 'data-slot': new Set(), 'data-component': new Set(), 'data-testid': new Set(), role: new Set() };
    for (const el of document.querySelectorAll('*')) for (const a of el.attributes) {
      if (a.name.startsWith('data-')) attrs[a.name] = (attrs[a.name] || 0) + 1;
      if (vals[a.name]) vals[a.name].add(a.value);
    }
    return {
      url: location.pathname.replace(/[A-Za-z0-9_-]{16,}/g, ':id'),
      routes: uniq([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => h && h.startsWith('/')).map(h => h.replace(/[A-Za-z0-9_-]{16,}/g, ':id'))).slice(0, 80),
      controls: uniq([...document.querySelectorAll('button,[role=button],[role=tab],[role=menuitem],summary')].filter(vis).map(x => (x.getAttribute('aria-label') || x.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 32)).filter(Boolean)).slice(0, 120),
      inputs: uniq([...document.querySelectorAll('input,textarea,[contenteditable=true]')].filter(vis).map(x => x.tagName.toLowerCase() + ':' + (x.getAttribute('placeholder') || x.getAttribute('aria-label') || x.type || ''))),
      dataAttrs: Object.entries(attrs).sort((a, b) => b[1] - a[1]).slice(0, 60).map(([k, v]) => `${k}(${v})`),
      slots: [...vals['data-slot']].slice(0, 120), components: [...vals['data-component']].slice(0, 80), testids: [...vals['data-testid']].slice(0, 80), roles: [...vals.role],
      html: document.documentElement.className + ' | ' + JSON.stringify(document.documentElement.dataset),
      stylesheets: document.styleSheets.length, canvases: document.querySelectorAll('canvas').length, iframes: document.querySelectorAll('iframe').length,
    };
  });
  console.log('=====', u); console.log(JSON.stringify(info, null, 1));
}
await ctx.close(); await b.close();
