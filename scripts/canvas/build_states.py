"""Step 9. Visual micro-interaction sheets: every interactive element, shown in each of its states.
usage: python3 build_states.py <extract_out.json> [--publish] [--page-key states] [--page-name "Micro-interactions"] [--rows 45]

Input is extract.mjs output for interactive targets (see examples/jobs/states.job.json). For each distinct element the sheet shows
rest · hover · focus-visible · active · disabled, each state attribute the element carries flipped (aria-expanded, data-state, ...),
and one cell that toggles hover every 1.2s so the transition itself is visible. States are produced by the site's OWN rules:
css_text() duplicates every :hover/:focus-visible/:active/:disabled rule as a .is-hover/... class rule, and cells just carry that class.
A table of class names and CSS text is not a micro-interaction spec; this is what a designer can look at."""
import json, re, sys
from sheetlib import *
FLIP = {"true": "false", "false": "true", "open": "closed", "closed": "open", "checked": "unchecked", "unchecked": "checked", "on": "off", "off": "on", "active": "inactive", "inactive": "active"}
STATE_ATTRS = ["aria-expanded", "aria-selected", "aria-pressed", "aria-checked", "aria-current", "data-state", "data-selected", "data-active", "data-open", "data-highlighted", "data-checked"]
def tag_end(h):
    q = None
    for i, ch in enumerate(h):
        if q:
            if ch == q: q = None
        elif ch in "\"'": q = ch
        elif ch == ">": return i
    return -1
def with_root(h, cls=(), attrs=None, drop=()):
    e = tag_end(h); tag, rest = h[:e], h[e:]
    for k in list((attrs or {})) + list(drop): tag = re.sub(rf'\s{re.escape(k)}(="[^"]*")?(?=\s|$)', "", tag)
    if cls:
        m = re.search(r'\sclass="', tag)
        tag = (tag[:m.end()] + " ".join(cls) + " " + tag[m.end():]) if m else tag + f' class="{" ".join(cls)}"'
    for k, v in (attrs or {}).items(): tag += f' {k}="{esc(v)}"'
    return tag + rest
def cell(v, label, html, live=False):
    inh = v.get("inherit") or {}
    st = f"color:{inh.get('color','inherit')};font-size:{inh.get('fontSize','inherit')};line-height:{inh.get('lineHeight','inherit')};font-weight:{inh.get('fontWeight','inherit')};letter-spacing:{inh.get('letterSpacing','inherit')};"
    if v.get("bgColor"): st += f"background:{v['bgColor']};"
    return (f'<div class="st-cell"><div class="st-stage" style="{st}"{" data-live" if live else ""}><div style="width:{v["w"]}px">{html}</div></div><div class="st-lab">{esc(label)}</div></div>')
SCRIPT = """<script>(function(){var on=false;setInterval(function(){on=!on;document.querySelectorAll('[data-live]').forEach(function(c){var el=c.firstElementChild&&c.firstElementChild.firstElementChild;if(el)el.classList.toggle('is-hover',on);});},1200);})();</script>"""
def row(key, v):
    h = v["html"]; tag = h[:tag_end(h) + 1]
    cells = cell(v, "rest", h) + cell(v, "hover", with_root(h, ["is-hover"])) + cell(v, "focus-visible", with_root(h, ["is-focus-visible"])) + cell(v, "active", with_root(h, ["is-active", "is-hover"]))
    if not re.search(r"\sdisabled(\s|=|>|$)", tag): cells += cell(v, "disabled", with_root(h, ["is-disabled"], {"disabled": "", "aria-disabled": "true", "data-disabled": ""}))
    for a in STATE_ATTRS:
        m = re.search(rf'\s{a}(?:="([^"]*)")?', tag)
        if m:
            cur = m.group(1)
            if cur in FLIP: cells += cell(v, f"{a}={FLIP[cur]}", with_root(h, attrs={a: FLIP[cur]}))
            elif cur in (None, ""): cells += cell(v, f"without {a}", with_root(h, drop=[a]))
    cells += cell(v, "live · hover toggles every 1.2s", h, live=True)
    meta = f'<div class="st-meta"><div class="mi-u">{esc(key)} · {esc((v.get("text") or "")[:40])}</div><div class="mi-x">{esc(v.get("st", ""))}</div><div class="mi-w">{v["w"]}×{v["h"]} · seen {v.get("n", 1)}× · {esc(v.get("frameName", ""))}</div></div>'
    return f'<div class="st-row">{meta}<div class="st-cells">{cells}</div></div>'
if __name__ == "__main__":
    a = sys.argv[1:]; src = a[0]; a = a[1:]; opt = {"--page-key": "states", "--page-name": "Micro-interactions — every state, visual", "--rows": "45"}; pub = False
    while a:
        if a[0] == "--publish": pub = True; a = a[1:]
        else: opt[a[0]] = a[1]; a = a[2:]
    o = json.load(open(src)); css = css_text(o["css"]); root = o.get("root"); per = int(opt["--rows"]); width = 1920
    items = [(k, v) for k, m in o["variants"].items() for v in sorted(m.values(), key=lambda v: -v.get("n", 1)) if v.get("html")]
    built = []
    for i in range(0, len(items), per):
        chunk = items[i:i + per]; n = i // per + 1; total = -(-len(items) // per)
        html = doc("MICRO-INTERACTIONS / VISUAL", f"Interactive elements in every state ({n}/{total})",
                   "Each row is one real element cut from the captured screens. Columns apply the site's own hover, focus, press and disabled rules; the last cell loops hover so the transition can be seen. Hovering and focusing the specimens also works.",
                   section("Elements", f"{len(chunk)} of {len(items)}", "".join(row(k, v) for k, v in chunk)), css, SCRIPT, width, root)
        key = f"states_{n}"; h, _ = render(html, key, width); built.append((key, f"States · {n}/{total}", html, h)); print(key, "rows", len(chunk), "height", h, "bytes", len(html))
    if pub:
        pid = page_id(opt["--page-key"], opt["--page-name"]); x = 0
        for key, nm, html, h in built:
            try: print("published", key, publish(key, nm, pid, html, width, h, x, 0, "interactive elements cut from captured screens"))
            except Exception as ex: print("FAIL", key, str(ex)[:300])
            x += width + 120
