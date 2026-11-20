# Coverage checklist

Copy this file to `$DSX_WORK/coverage.md`. For every line write the scenario keys that cover it and mark it:
`[x]` captured, published and viewed · `[ ]` still open · `[-]` this app does not have it (write the evidence: where you looked).

Each line is desktop first. Section 12 repeats all of it on mobile. Rename items to the app's own words; do not drop lines.
Add lines for anything this app has that is not listed. If you find a control you have not opened, open it.

## 1. Shell and navigation
- [ ] App at rest on its start screen
- [ ] Every top-level route, one frame each
- [ ] Left sidebar: at rest, collapsed, each section expanded and collapsed, resize affordance
- [ ] Sidebar rows of every kind: rest, hover (and any preview card), active, unread, working, error
- [ ] Sidebar row context menu, per row kind (include pin / unpin, reorder affordances; open the menu, do not act)
- [ ] Section header menus and "new" controls
- [ ] Account / workspace menu and every submenu
- [ ] Search and command palette: empty, typed query, each tab or category, keyboard-highlighted row, no results
- [ ] Empty states of every list

## 2. Composer (every layer)
- [ ] Empty, focused, text typed (send enabled), multi-line, at max height
- [ ] Each picker and menu on it: model, effort or mode, project, branch, machine, add / attach, configuration
- [ ] Slash-command menu, mention menu, any other trigger character
- [ ] Attachments: uploading, settled, several, hover, preview, remove, failed (only if reachable without sending)
- [ ] Chips and tokens inside the editor
- [ ] Drag and drop overlay
- [ ] Context meter, queue, stop / streaming state (capture from existing threads; do not start a run)
- [ ] The composer inside a thread, where it differs from the start screen

## 3. Chat and transcript
- [ ] A thread at rest; a long thread scrolled up (scroll-to-end control)
- [ ] User message: rest, hover actions, each action menu
- [ ] Agent message: rest, hover actions, footer actions, copy feedback
- [ ] Work log / steps: collapsed, expanded, one step expanded, running, failed, cancelled
- [ ] Every kind of tool call row and its opened detail
- [ ] Reasoning / thinking: live and settled
- [ ] Streaming and status indicators in every state the app has
- [ ] In-chat cards: question, approval, secret or credential request, setup, error, retry, each in every state present
- [ ] Markdown: headings, lists, tables, links, code blocks (header, copy, wrap), diagrams
- [ ] Attachments and media in messages; gallery; lightbox with its toolbar, zoom, annotate
- [ ] Diffs: card, toolbar, selection
- [ ] Subagent, child thread or reference chips and their preview cards
- [ ] Thread header: title, options menu, cost or usage popover, share dialog

## 4. Right sidebar / secondary panel
- [ ] Closed, open, expanded
- [ ] Tab strip: each tab selected, tab hover (close affordance), tab context menu, "open a tab" menu
- [ ] Every pane's content, including empty and loading states
- [ ] Rows inside panes: hover, preview, context menu, sort and filter menus
- [ ] Resize handle and split layouts

## 5. Dialogs, sheets, overlays
- [ ] Every create / edit dialog, including each inner menu and editor (avatar, colour, model)
- [ ] Confirm and destructive dialogs (open them, then cancel)
- [ ] Popovers, tooltips, preview cards
- [ ] Toasts: each type the app shows without changing data
- [ ] Banners: offline, error, update

## 6. Settings
- [ ] Every settings section, one frame each
- [ ] Each select, menu, colour picker and inline editor opened (do not change values)
- [ ] Appearance / theme page and each theme preview (switching the account's theme needs the user's permission)
- [ ] Organisation, members, billing, usage, integrations pages, if present

## 7. Other pages
- [ ] Every list page: default, each filter or display menu, row hover, row context menu, bulk selection bar
- [ ] Every detail page
- [ ] Explore / marketplace / templates pages and their detail views

## 8. Auth and onboarding
- [ ] Sign-in, sign-up, verification (capture signed out, in a context without the cookie)
- [ ] Each onboarding step that can be reached without changing the account
- [ ] 404 and error pages

## 9. Tokens and brand
- [ ] Every CSS custom property the app ships, on the Tokens page with identical names and values
- [ ] Theme overrides (dark / light / named themes) as token themes
- [ ] Fonts in use; icon set; logo and avatars

## 10. Micro-interactions (visual)
- [ ] Buttons of every variant and size: rest, hover, focus-visible, active, disabled, loading
- [ ] Links, fields, selects, switches, checkboxes, radios, tabs, menu rows, list rows, chips: same states
- [ ] Selected / open / highlighted states driven by attributes

## 11. Motion (one frame per interaction)
- [ ] Hover on each kind of row and control
- [ ] Each menu, picker and popover: opening and closing
- [ ] Each dialog and sheet: opening and closing
- [ ] Tooltip and preview-card appear
- [ ] Sidebar collapse and expand; panel open, close, expand
- [ ] Section and work-log expand and collapse
- [ ] Tab switch; route change; settings page change
- [ ] Focus rings; typing enables send; copy feedback
- [ ] Scroll-triggered UI; streaming, shimmer and loading indicators
- [ ] Drag affordances

## 12. Mobile (390×844, touch)
- [ ] Sections 1 to 8 again. Sheets and drawers replace menus; the sidebar is a drawer; tabs may scroll.
- [ ] Motion for the mobile-only transitions: drawer, bottom sheets
