const T = async (p) => { const h = await p.evaluate(() => document.querySelector('a[href^="/thread/"]')?.getAttribute('href')); await p.goto(process.env.DSX_BASE_URL + h, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(6500); };
const Tn = (n) => async (p) => { const h = await p.evaluate((n) => [...document.querySelectorAll('a[href^="/thread/"]')].map(a => a.getAttribute('href')).filter((v, i, a) => a.indexOf(v) === i)[n], n); await p.goto(process.env.DSX_BASE_URL + h, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(6500); };
const th = (key, name, fn, extra = {}) => ({ key, group: 'thread', name: 'Live · ' + name, steps: async (p) => { await T(p); if (fn) await fn(p); }, ...extra });
const btn = (p, l) => p.locator(`button[aria-label="${l}"]`).first();
const chat = '[data-thread-chat]';
export default [
  th('th_rest', 'Thread at rest (chat + overview pane)'),
  th('th_worklog_open', 'Thread · work log expanded', async (p) => { await p.locator(`${chat} [data-slot="activity-line"] button`).last().click(); await p.waitForTimeout(600); }),
  th('th_worklog_step_open', 'Thread · work log step expanded', async (p) => { await p.locator(`${chat} [data-slot="activity-line"] button`).last().click(); await p.waitForTimeout(600); await p.locator(`${chat} [data-slot="work-group-panel"] [data-slot="collapsible"] [role=button], ${chat} [data-slot="work-group-panel"] [data-slot="collapsible-trigger"]`).first().click().catch(() => {}); }),
  th('th_user_hover', 'Thread · user message hover (reply, copy, edit)', async (p) => { await p.locator(`${chat} [data-slot="user-message"]`).last().hover(); }),
  th('th_agent_hover', 'Thread · agent message hover (section rail)', async (p) => { await p.locator(`${chat} [data-slot="message-section"]`).last().hover(); }),
  th('th_msg_more', 'Thread · message More menu', async (p) => { await p.locator(`${chat} [data-slot="message-section"]`).last().hover(); await p.locator(`${chat} button[aria-label="More"]`).last().click(); }),
  th('th_preview_card', 'Thread · chip preview card', async (p) => { await p.locator(`${chat} [data-slot="preview-card-trigger"]`).last().hover(); await p.waitForTimeout(900); }),
  th('th_open_tab', 'Right sidebar · Open a tab menu', async (p) => { await btn(p, 'Open a tab').click(); }),
  th('th_cost', 'Thread · cost breakdown', async (p) => { await p.locator('button[aria-label^="Thread cost"]').first().click(); }),
  th('th_context', 'Thread · context meter', async (p) => { await p.locator('button[aria-label*="token budget"]').first().click(); }),
  th('th_options', 'Thread · options menu', async (p) => { await p.locator(`${chat} button[aria-label="Thread options"], header button[aria-label="Thread options"]`).last().click(); }),
  th('th_expand', 'Right sidebar · pane expanded', async (p) => { await btn(p, 'Expand pane').click(); }),
  th('th_tab_issues', 'Right sidebar · Issues tab', async (p) => { await p.locator('[data-pane-tab="captain_issues"]').first().click(); await p.waitForTimeout(1500); }),
  th('th_tab_ctx', 'Right sidebar · tab context menu', async (p) => { await p.locator('[data-pane-tab="overview"]').first().click({ button: 'right' }); }),
  th('th_tab_hover', 'Right sidebar · tab hover (close affordance)', async (p) => { await p.locator('[data-pane-tab="overview"]').first().hover(); }),
  th('th_pr_sort', 'Right sidebar · sort pull requests', async (p) => { await btn(p, 'Sort pull requests').click(); }),
  th('th_pr_row_hover', 'Right sidebar · pull request row hover', async (p) => { await p.locator('button:has-text("PR-ROW-TEXT")').first().hover(); await p.waitForTimeout(900); }),
  th('th_pr_row_ctx', 'Right sidebar · pull request row context menu', async (p) => { await p.locator('button:has-text("PR-ROW-TEXT")').first().click({ button: 'right' }); }),
  th('th_model', 'Thread · model picker', async (p) => { await btn(p, 'Model').click(); }),
  th('th_machine', 'Thread · machine menu', async (p) => { await btn(p, 'Machine').click(); }),
  th('th_add', 'Thread · add to message', async (p) => { await btn(p, 'Add to message').click(); }),
  th('th_scrolled', 'Thread · scrolled up (scroll-to-end pill)', async (p) => { await p.mouse.move(700, 500); await p.mouse.wheel(0, -2400); await p.waitForTimeout(900); }),
  th('th_pane_closed', 'Thread · right pane closed', async (p) => { await btn(p, 'Close pane').click(); }),
  th('th_identity', 'Captain · identity header menu', async (p) => { await p.locator('button:has-text("View Captain"), button[aria-label="View Captain"]').first().click().catch(() => {}); }),
  { key: 'th_t2', group: 'thread', name: 'Live · Thread (project thread)', steps: Tn(2) },
  { key: 'th_t3', group: 'thread', name: 'Live · Thread (second project thread)', steps: Tn(5) },
  { key: 'cap_edit', group: 'captain', name: 'Live · Captain options → edit', steps: async (p) => { await p.locator('[data-captain-row]').first().click({ button: 'right' }); await p.waitForTimeout(500); await p.getByRole('menuitem', { name: /Edit|Settings|Profile/ }).first().click().catch(() => {}); await p.waitForTimeout(900); } },
  { key: 'cap_new_avatar', group: 'captain', name: 'Live · New Captain → avatar editor', steps: async (p) => { await p.locator('button[aria-label="New Captain"]').first().click(); await p.waitForTimeout(800); await p.locator('button[aria-label="Change avatar"]').first().click().catch(() => {}); await p.waitForTimeout(900); } },
  { key: 'cap_new_model', group: 'captain', name: 'Live · New Captain → model menu', steps: async (p) => { await p.locator('button[aria-label="New Captain"]').first().click(); await p.waitForTimeout(800); await p.locator('[role=dialog] button:has-text("Model"), [role=dialog] button[aria-label="Model"]').first().click().catch(() => {}); await p.waitForTimeout(700); } },
  { key: 'um_appearance', group: 'sidebar', name: 'Live · User menu → Appearance', steps: async (p) => { await p.locator('button:has-text("WORKSPACE NAME"), button[aria-label="WORKSPACE NAME"]').first().click(); await p.waitForTimeout(500); await p.getByRole('menuitem', { name: /Appearance/ }).first().hover(); await p.waitForTimeout(700); } },
  { key: 'cmdk', group: 'sidebar', name: 'Live · Command menu (Ctrl+K)', steps: async (p) => { await p.keyboard.press('Control+k'); await p.waitForTimeout(800); } },
];
