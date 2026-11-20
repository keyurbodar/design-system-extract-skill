// Render a built sheet locally and measure its height before publishing. usage: node render.mjs <in.html> <out.png|-> [width]
import { connect, WORK, SCHEME } from './lib.mjs';
import fs from 'fs';
const [src, out, w] = process.argv.slice(2);
const b = await connect();
const ctx = await b.newContext({ viewport: { width: +w || 1440, height: 900 }, deviceScaleFactor: 1, colorScheme: SCHEME });
const p = await ctx.newPage();
await p.setContent(fs.readFileSync(src, 'utf8'), { waitUntil: 'load', timeout: 90000 });
if (fs.existsSync(WORK + '/tokens_local.css')) await p.addStyleTag({ content: fs.readFileSync(WORK + '/tokens_local.css', 'utf8') });
await p.waitForTimeout(600);
const h = await p.evaluate(() => Math.ceil(document.querySelector('.sheet')?.getBoundingClientRect().height || document.documentElement.scrollHeight));
console.log('HEIGHT', h);
if (out && out !== '-') { await p.setViewportSize({ width: +w || 1440, height: Math.min(h, 12000) }); await p.waitForTimeout(300); await p.screenshot({ path: out }); }
await ctx.close(); await b.close();
