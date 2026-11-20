# Examples

- `jobs/states.job.json`: an extract job that collects every interactive element, for `build_states.py`. Replace `frames` with your own capture keys.
- `capy/`: the scenario files and two site-specific sheet builders from the session this skill was distilled from (a Capy-style chat app). They are reference material, not runnable as they are: selectors, names and placeholder strings such as `WORKSPACE NAME` belong to that app.
  - `sc_sidebar.mjs`, `sc_settings.mjs`, `sc_thread.mjs`, `sc_mobile.mjs`: capture scenarios (29 + 28 + 31 + 57 states).
  - `sc_motion.mjs`: 78 motion scenarios. Copy its shape: one tiny `trigger` per interaction, with `setup` for the state before it.
  - `build_chat.py`, `build_micro.py`: the first, hand-specified versions of what `build_sheets.py` and `build_states.py` now do generically.

What those runs produced: 88 desktop frames, 57 mobile frames, 75 motion frames, 10 chat component sheets, 7 visual state sheets, and 88 duplicate frames moved to an archive page.
