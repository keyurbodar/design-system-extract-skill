const M = { vp: { width: 390, height: 844 }, mobile: true, group: 'mobile' };
const ab = (l) => `button[aria-label="${l}"]`;
const tap = (sel) => async (p) => { await p.locator(sel).first().click(); };
const openSb = async (p) => { await p.locator(ab('Open sidebar')).first().click(); await p.waitForTimeout(800); };
const goThread = async (p) => { await openSb(p); const h = await p.evaluate(() => document.querySelector('a[href^="/thread/"]')?.getAttribute('href')); await p.goto(process.env.DSX_BASE_URL + h, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(6500); };
const m = (key, name, steps, extra = {}) => ({ key: 'mob_' + key, name: 'Mobile · ' + name, steps, ...M, ...extra });
const sb = (fn) => async (p) => { await openSb(p); await fn(p); };
const th = (fn) => async (p) => { await goThread(p); if (fn) await fn(p); };
const chat = '[data-thread-chat]';
const USER = 'button:has-text("WORKSPACE NAME"), button[aria-label="WORKSPACE NAME"]';
const setPages = ['general','appearance','profile','security','notifications','shortcuts','models','projects','mcp','integrations','devices','instructions','skills','threads','git','org/members','org/billing','org/usage'];
export default [
  m('new', 'New thread'),
  m('sidebar', 'Sidebar open', openSb),
  m('sb_search', 'Search', sb(tap(ab('Search')))),
  m('sb_new_captain', 'New Captain', sb(tap(ab('New Captain')))),
  m('sb_captain_options', 'Captain options', sb(tap(ab('Captain options')))),
  m('sb_thread_options', 'Thread options', sb(tap(ab('Thread options')))),
  m('sb_user_menu', 'User menu', sb(tap(USER))),
  m('sb_automations', 'Automations group open', sb(async (p) => { await p.locator('button:has-text("Automations")').first().click(); })),
  m('sb_captain_longpress', 'Captain row actions', sb(async (p) => { await p.locator('[data-captain-row]').first().click({ button: 'right' }); })),
  m('sb_thread_longpress', 'Thread row actions', sb(async (p) => { await p.locator('a[href^="/thread/"]').nth(4).click({ button: 'right' }); })),
  m('cmp_project', 'Composer · project sheet', tap(ab('Project'))),
  m('cmp_machine', 'Composer · machine sheet', tap(ab('Machine'))),
  m('cmp_branch', 'Composer · branch sheet', tap(ab('Branch'))),
  m('cmp_add', 'Composer · add to message', tap(ab('Add to message'))),
  m('cmp_config', 'Composer · thread configuration', tap(ab('Thread configuration'))),
  m('cmp_model', 'Composer · model sheet', tap(ab('Model'))),
  m('cmp_focus', 'Composer · focused', tap('[contenteditable="true"]')),
  m('cmp_slash', 'Composer · slash commands', async (p) => { await p.locator('[contenteditable="true"]').first().click(); await p.keyboard.type('/'); }),
  m('cmp_mention', 'Composer · mentions', async (p) => { await p.locator('[contenteditable="true"]').first().click(); await p.keyboard.type('@'); }),
  m('th_rest', 'Thread', th()),
  m('th_worklog', 'Thread · work log open', th(async (p) => { await p.locator(`${chat} [data-slot="activity-line"] button`).last().click(); })),
  m('th_more', 'Thread · message actions', th(async (p) => { await p.locator(`${chat} button[aria-label="More"]`).last().click(); })),
  m('th_options', 'Thread · options', th(tap(ab('Thread options')))),
  m('th_open_tab', 'Thread · open a tab', th(tap(ab('Open a tab')))),
  m('th_tab_overview', 'Thread · Overview tab', th(async (p) => { await p.locator('[data-pane-tab="overview"], button:has-text("Overview")').first().click(); await p.waitForTimeout(1200); })),
  m('th_tab_issues', 'Thread · Issues tab', th(async (p) => { await p.locator('[data-pane-tab="captain_issues"], button:has-text("Issues")').first().click(); await p.waitForTimeout(1200); })),
  m('th_model', 'Thread · model sheet', th(tap(ab('Model')))),
  m('th_machine', 'Thread · machine sheet', th(tap(ab('Machine')))),
  m('th_add', 'Thread · add to message', th(tap(ab('Add to message')))),
  m('th_context', 'Thread · context meter', th(tap('button[aria-label*="token budget"]'))),
  m('th_scrolled', 'Thread · scrolled up', th(async (p) => { await p.mouse.move(195, 400); await p.mouse.wheel(0, -2400); await p.waitForTimeout(800); })),
  m('th_lightbox', 'Thread · attachment open', th(async (p) => { await p.locator(`${chat} button[aria-label^="Preview"]`).last().click(); await p.waitForTimeout(1200); })),
  ...['threads', 'issues', 'pulls', 'automations', 'explore', 'drive'].map(r => m('rt_' + r, r[0].toUpperCase() + r.slice(1), null, { url: '/' + r })),
  m('set_nav', 'Settings · navigation', openSb, { url: '/settings/general' }),
  ...setPages.map(s => m('set_' + s.replace(/\W+/g, '_'), 'Settings · ' + s.replace('/', ' / '), null, { url: '/settings/' + s, settle: 5500 })),
];
