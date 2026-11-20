const hover = (sel) => async (p) => { await p.locator(sel).first().hover(); };
const click = (sel) => async (p) => { await p.locator(sel).first().click(); };
const rclick = (sel) => async (p) => { await p.locator(sel).first().click({ button: 'right' }); };
const btn = (l) => `button[aria-label="${l}"], button:has-text("${l}")`;
const G = 'sidebar';
export default [
  { key: 'sb_new', group: G, name: 'Live · New thread (sidebar at rest)' },
  { key: 'sb_search', group: G, name: 'Live · Search open', steps: click('button[aria-label="Search"]') },
  { key: 'sb_closed', group: G, name: 'Live · Sidebar closed', steps: click('button[aria-label="Close sidebar"]') },
  { key: 'sb_captain_new', group: G, name: 'Live · New Captain dialog', steps: click('button[aria-label="New Captain"]') },
  { key: 'sb_captain_options', group: G, name: 'Live · Captain options menu', steps: click('button[aria-label="Captain options"]') },
  { key: 'sb_thread_new_menu', group: G, name: 'Live · New thread control', steps: click('button[aria-label="New thread"]') },
  { key: 'sb_thread_options', group: G, name: 'Live · Thread options menu', steps: click('button[aria-label="Thread options"]') },
  { key: 'sb_pinned_hover', group: G, name: 'Live · Pinned captain tile hover', steps: hover('[data-captain-row]') },
  { key: 'sb_pinned_menu', group: G, name: 'Live · Pinned captain context menu', steps: rclick('[data-captain-row]') },
  { key: 'sb_row_hover', group: G, name: 'Live · Captain row hover', steps: async (p) => { await p.getByText('CAPTAIN ROW NAME', { exact: true }).first().hover(); } },
  { key: 'sb_row_menu', group: G, name: 'Live · Captain row context menu (pin)', steps: async (p) => { await p.getByText('CAPTAIN ROW NAME', { exact: true }).first().click({ button: 'right' }); } },
  { key: 'sb_thread_hover', group: G, name: 'Live · Thread row hover', steps: hover('a[href^="/thread/"]') },
  { key: 'sb_thread_menu', group: G, name: 'Live · Thread row context menu', steps: rclick('a[href^="/thread/"]') },
  { key: 'sb_automations', group: G, name: 'Live · Automations group open', steps: async (p) => { await p.getByText('Automations', { exact: false }).first().click(); } },
  { key: 'sb_user_menu', group: G, name: 'Live · User menu', steps: click('button[aria-label="WORKSPACE NAME"], button:has-text("WORKSPACE NAME")') },
  { key: 'cmp_project', group: 'composer', name: 'Live · Composer project picker', steps: click('button[aria-label="Project"]') },
  { key: 'cmp_machine', group: 'composer', name: 'Live · Composer machine picker', steps: click('button[aria-label="Machine"]') },
  { key: 'cmp_branch', group: 'composer', name: 'Live · Composer branch picker', steps: click('button[aria-label="Branch"]') },
  { key: 'cmp_add', group: 'composer', name: 'Live · Composer add to message', steps: click('button[aria-label="Add to message"]') },
  { key: 'cmp_config', group: 'composer', name: 'Live · Composer thread configuration', steps: click('button[aria-label="Thread configuration"]') },
  { key: 'cmp_model', group: 'composer', name: 'Live · Composer model picker', steps: click('button[aria-label="Model"]') },
  { key: 'cmp_slash', group: 'composer', name: 'Live · Composer slash commands', steps: async (p) => { await p.locator('[contenteditable="true"]').first().click(); await p.keyboard.type('/'); } },
  { key: 'cmp_mention', group: 'composer', name: 'Live · Composer @ mentions', steps: async (p) => { await p.locator('[contenteditable="true"]').first().click(); await p.keyboard.type('@'); } },
  { key: 'rt_threads', group: 'routes', name: 'Live · Threads', url: '/threads' },
  { key: 'rt_issues', group: 'routes', name: 'Live · Issues', url: '/issues' },
  { key: 'rt_pulls', group: 'routes', name: 'Live · Pull requests', url: '/pulls' },
  { key: 'rt_automations', group: 'routes', name: 'Live · Automations', url: '/automations' },
  { key: 'rt_explore', group: 'routes', name: 'Live · Explore', url: '/explore' },
  { key: 'rt_drive', group: 'routes', name: 'Live · Drive', url: '/drive' },
];
