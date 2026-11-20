// Shared browser helpers. Config comes from the environment (see README):
//   DSX_BASE_URL     origin of the app to extract, e.g. https://chat.example.com
//   DSX_COOKIE_FILE  JSON cookie export (Chrome "EditThisCookie" format). Optional for public or local apps.
//   DSX_CDP          CDP endpoint of a running Chrome. Unset = launch a headless Chromium.
//   DSX_WORK         work directory for all outputs (default: cwd)
//   DSX_COLOR_SCHEME dark | light (default dark)
import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';
export const BASE = (process.env.DSX_BASE_URL || '').replace(/\/$/, '');
export const WORK = process.env.DSX_WORK || process.cwd();
export const SCHEME = process.env.DSX_COLOR_SCHEME || 'dark';
export function loadCookies() {
  const f = process.env.DSX_COOKIE_FILE;
  if (!f) return [];
  const raw = JSON.parse(fs.readFileSync(f, 'utf8'));
  const ss = { no_restriction: 'None', none: 'None', lax: 'Lax', strict: 'Strict', unspecified: 'Lax' };
  return raw.map(c => {
    const o = { name: c.name, value: c.value, domain: c.domain, path: c.path || '/', secure: !!c.secure, httpOnly: !!c.httpOnly, sameSite: ss[String(c.sameSite || 'lax').toLowerCase()] || 'Lax' };
    if (c.expirationDate) o.expires = Math.floor(c.expirationDate);
    if (o.sameSite === 'None') o.secure = true;
    return o;
  });
}
export async function connect() {
  if (process.env.DSX_CDP) return chromium.connectOverCDP(process.env.DSX_CDP);
  return chromium.launch({ headless: true, executablePath: process.env.DSX_CHROME || undefined });
}
// One isolated context per call: this is the "parallel profile". Cookies are injected, never typed.
export async function newCtx(browser, vp = { width: 1600, height: 1000 }, extra = {}) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, colorScheme: SCHEME, ...extra });
  const cookies = loadCookies();
  if (cookies.length) await ctx.addCookies(cookies);
  return ctx;
}
export const abs = (u) => (/^https?:/.test(u) ? u : BASE + u);
export const loadModule = (p) => import(pathToFileURL(path.resolve(p)).href);
// Hide opaque ids when printing URLs so logs stay readable and do not leak resource ids.
export const redact = (s) => String(s).replace(/[A-Za-z0-9_-]{16,}/g, ':id');
