// DOM snapshot: turn the page as it is right now into one self-contained HTML document.
//  - every stylesheet is inlined from the CSSOM (cross-origin sheets are fetched), relative url()s made absolute
//  - <canvas> elements are replaced by a PNG of their current pixels (shaders, dither, charts would otherwise be blank)
//  - form values, checked state and scroll positions are kept; scripts, iframes and preloads are removed
//  - <html> and <body> attributes are kept, so theme classes and data attributes still drive the CSS
// The result renders the same without the app's JavaScript, and its DOM stays inspectable and editable on the canvas.
export async function snapshot(page) {
  const canvases = await page.$$('canvas');
  const shots = [];
  for (const c of canvases) {
    try { const box = await c.boundingBox(); if (box && box.width > 4 && box.height > 4) shots.push('data:image/png;base64,' + (await c.screenshot({ type: 'png', omitBackground: true })).toString('base64')); else shots.push(null); }
    catch { shots.push(null); }
  }
  const r = await page.evaluate((shots) => {
    const abs = (u, base) => { try { return new URL(u, base).href; } catch { return u; } };
    const fixUrls = (css, base) => css.replace(/url\((['"]?)(?!data:|https?:|blob:|#)([^'")]+)\1\)/g, (m, q, u) => `url("${abs(u, base)}")`);
    const css = []; const ext = [];
    for (const s of [...document.styleSheets, ...(document.adoptedStyleSheets || [])]) {
      try { css.push(fixUrls([...s.cssRules].map(x => x.cssText).join('\n'), s.href || location.href)); }
      catch { if (s.href) { ext.push(s.href); css.push('/*EXT:' + s.href + '*/'); } }
    }
    const clone = document.body.cloneNode(true);
    const live = [...document.body.querySelectorAll('*')]; const cl = [...clone.querySelectorAll('*')];
    let ci = 0;
    live.forEach((el, i) => {
      const c = cl[i]; if (!c) return;
      if (el.tagName === 'CANVAS') { const src = shots[ci++]; if (src) { const img = document.createElement('img'); img.src = src; img.className = el.className; img.setAttribute('style', (el.getAttribute('style') || '') + ';width:' + el.clientWidth + 'px;height:' + el.clientHeight + 'px'); for (const a of el.attributes) if (a.name.startsWith('data-')) img.setAttribute(a.name, a.value); c.replaceWith(img); } return; }
      if (el.tagName === 'IMG' && el.currentSrc) { c.setAttribute('src', el.currentSrc); c.removeAttribute('srcset'); c.removeAttribute('loading'); }
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') { if (el.type !== 'password') c.setAttribute('value', el.value); if (el.tagName === 'TEXTAREA') c.textContent = el.value; if (el.checked) c.setAttribute('checked', ''); }
      if (el.scrollTop > 0 || el.scrollLeft > 0) c.setAttribute('data-snap-scroll', el.scrollTop + ',' + el.scrollLeft);
      const st = c.getAttribute('style'); if (st && st.includes('url(')) c.setAttribute('style', fixUrls(st, location.href));
    });
    clone.querySelectorAll('script,noscript,iframe,link[rel=preload],link[rel=modulepreload]').forEach(n => n.remove());
    const attrs = (el) => [...el.attributes].map(a => `${a.name}="${a.value.replace(/&/g, '&amp;').replace(/"/g, '&quot;')}"`).join(' ');
    return { css, ext, body: clone.innerHTML, htmlAttrs: attrs(document.documentElement), bodyAttrs: attrs(document.body), url: location.pathname, title: document.title, w: innerWidth, h: innerHeight };
  }, shots);
  for (const href of r.ext) {
    try { const resp = await page.request.get(href); let t = await resp.text(); t = t.replace(/url\((['"]?)(?!data:|https?:|blob:|#)([^'")]+)\1\)/g, (m, q, u) => `url("${new URL(u, href).href}")`); r.css = r.css.map(c => c === '/*EXT:' + href + '*/' ? t : c); } catch {}
  }
  const restore = `<script>document.querySelectorAll('[data-snap-scroll]').forEach(function(e){var p=e.getAttribute('data-snap-scroll').split(',');e.scrollTop=+p[0];e.scrollLeft=+p[1];});</script>`;
  const html = `<!doctype html><html ${r.htmlAttrs}><head><meta charset="utf-8"><style>${r.css.join('\n')}</style><style>html,body{margin:0;width:${r.w}px;height:${r.h}px;overflow:hidden}*{animation-play-state:running}</style></head><body ${r.bodyAttrs}>${r.body}${restore}</body></html>`;
  return { html, url: r.url, title: r.title, w: r.w, h: r.h };
}
