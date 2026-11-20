"""Shared helpers for the canvas side: Doop calls, the manifest, CSS forcing, sheet layout, local render.
Env: DOOP_TOKEN, DSX_CANVAS (target canvas id), DSX_WORK (work dir), DSX_AGENT (display name), DSX_NODE (node binary)."""
import json, re, html as H, subprocess, os, sys, fcntl, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); import doop_cli
W = os.environ.get("DSX_WORK", os.getcwd())
CDS = CANVAS = os.environ["DSX_CANVAS"]
AGENT = os.environ.get("DSX_AGENT", "Design system extractor")
NODE = os.environ.get("DSX_NODE", "node")
BROWSER = os.path.join(HERE, "..", "browser")
PSEUDO = [(r":hover", ".is-hover"), (r":focus-visible", ".is-focus-visible"), (r":focus-within", ".is-focus-within"),
          (r":focus(?![-\w])", ".is-focus"), (r":active", ".is-active"), (r":disabled", ".is-disabled")]
PRX = re.compile(r":hover|:focus-visible|:focus-within|:focus(?![-\w])|:active|:disabled")
def force(sel):
    for a, b in PSEUDO: sel = re.sub(a, b, sel)
    return sel
def css_text(flat, forced=True):
    items = []
    for chain, text in flat:
        items.append((chain, text))
        if not forced: continue
        leaf_sel = None
        if "{" in text and not text.lstrip().startswith("@"):
            leaf_sel = text[:text.index("{")]
        has = any((not c.startswith("@")) and PRX.search(c) for c in chain) or (leaf_sel and PRX.search(leaf_sel))
        if not has: continue
        nchain = [force(c) if not c.startswith("@") else c for c in chain if not (c.startswith("@media") and "hover" in c)]
        ntext = force(leaf_sel) + text[text.index("{"):] if leaf_sel else text
        items.append((nchain, ntext))
    out = []; cur = None; buf = []
    def flush():
        if cur is None: return
        out.append("".join(c + "{" for c in cur) + "\n".join(buf) + "}" * len(cur))
    for chain, text in items:
        if chain != cur:
            flush(); cur = chain; buf = []
        buf.append(text)
    flush()
    return "\n".join(out)
# Sheet chrome. It is annotation only (titles, captions, hairlines) and deliberately uses no token of the site
# being extracted: neutral system fonts and colours mixed from the site's own page background and text colour.
SHEET_CSS = """
.dsx-sheet{padding:48px 48px 56px;box-sizing:border-box;font:13px/1.45 ui-sans-serif,system-ui,sans-serif;color:var(--dsx-fg);--dsx-mut:color-mix(in srgb,var(--dsx-fg) 58%,transparent);--dsx-dim:color-mix(in srgb,var(--dsx-fg) 38%,transparent);--dsx-line:color-mix(in srgb,var(--dsx-fg) 12%,transparent);--dsx-mono:ui-monospace,SFMono-Regular,Menlo,monospace}
.dsx-sheet .sh-head{padding-bottom:20px;border-bottom:1px solid var(--dsx-line);margin-bottom:32px}
.dsx-sheet .sh-kicker{font:11px/1.4 var(--dsx-mono);color:var(--dsx-dim);margin-bottom:8px;letter-spacing:.04em}
.dsx-sheet .sh-title{font-size:24px;font-weight:600;letter-spacing:-.01em;line-height:1.15}
.dsx-sheet .sh-desc{margin-top:8px;max-width:760px;color:var(--dsx-mut);font-size:14px;line-height:1.5}
.dsx-sheet .sec{margin-top:36px}
.dsx-sheet .sec-h{display:flex;align-items:baseline;gap:10px;margin-bottom:14px}
.dsx-sheet .sec-t{font-size:15px;font-weight:600}
.dsx-sheet .sec-n{font-size:12px;color:var(--dsx-dim)}
.dsx-sheet .mi-u{font:12px/1.4 var(--dsx-mono);color:var(--dsx-fg)}
.dsx-sheet .mi-c{font:12px/1.45 var(--dsx-mono);color:var(--dsx-mut)}
.dsx-sheet .mi-x{font:11px/1.4 var(--dsx-mono);color:var(--dsx-dim);margin-top:3px}
.dsx-sheet .mi-w{font:11px/1.5 var(--dsx-mono);color:var(--dsx-mut)}
.dsx-sheet .sp-grid{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start}
.dsx-sheet .sp{display:flex;flex-direction:column;gap:6px;min-width:0}
.dsx-sheet .sp-box{position:relative;border:1px solid var(--dsx-line);border-radius:8px;padding:12px;box-sizing:content-box;overflow:hidden}
.dsx-sheet .sp-box.tall{max-height:1100px;overflow:auto}
.dsx-sheet .sp-cap{display:flex;gap:8px;flex-wrap:wrap;align-items:baseline}
.dsx-sheet .st-row{display:flex;gap:12px;align-items:stretch;padding:12px 0;border-bottom:1px solid var(--dsx-line)}
.dsx-sheet .st-meta{width:300px;flex:none;min-width:0;word-break:break-word}
.dsx-sheet .st-cells{display:flex;gap:12px;flex-wrap:wrap;flex:1;min-width:0}
.dsx-sheet .st-cell{display:flex;flex-direction:column;gap:6px;min-width:0}
.dsx-sheet .st-stage{display:flex;align-items:center;justify-content:center;min-height:44px;min-width:72px;padding:10px 14px;border:1px solid var(--dsx-line);border-radius:8px;position:relative;overflow:hidden}
.dsx-sheet .st-lab{font:11px/1.4 var(--dsx-mono);color:var(--dsx-dim);text-align:center}
"""
def esc(s): return H.escape(str(s), quote=True)
def spec(v, label=None, box_extra=""):
    inh = v.get("inherit") or {}
    st = f"width:{v['w']}px;color:{inh.get('color','inherit')};font-size:{inh.get('fontSize','inherit')};line-height:{inh.get('lineHeight','inherit')};font-weight:{inh.get('fontWeight','inherit')};letter-spacing:{inh.get('letterSpacing','inherit')};"
    cls = "sp-box" + (" tall" if v["h"] > 1100 else "") + (" " + v["bgClass"] if v.get("bgClass") else "")
    if not v.get("bgClass") and v.get("bgColor"): st += f"background:{v['bgColor']};"
    cap = label if label is not None else ""
    inner = v["html"]
    if v["w"] <= 24 and v["h"] <= 24:
        st = st.replace(f"width:{v['w']}px;", f"width:{v['w']*5}px;"); inner = f'<div style="zoom:5;line-height:0">{inner}</div>'
    return (f'<div class="sp"><div class="{cls}" style="{st}{box_extra}">{inner}</div>'
            f'<div class="sp-cap"><span class="mi-u">{esc(cap)}</span><span class="mi-x">{esc(v.get("st",""))}</span>'
            f'<span class="mi-w">{v["w"]}×{v["h"]} · {esc(v.get("frameName",""))}</span></div></div>')
def section(title, note, body): 
    return f'<div class="sec"><div class="sec-h"><div class="sec-t">{esc(title)}</div><div class="sec-n">{esc(note)}</div></div>{body}</div>'
def doc(kicker, title, desc, sections_html, css, script="", width=1440, root=None):
    """A sheet document. `css` is the site's own CSS (from extract.mjs, see css_text). `root` is extract's `root`:
    the site's <html>/<body> attributes are re-applied so its variables, theme classes and base font reach every specimen."""
    root = root or {}
    links = "".join(f'<link rel="stylesheet" href="{esc(u)}">' for u in root.get("links", []))
    bg, fg = root.get("bg") or "#111", root.get("color") or "#eee"
    page = (f"html,body{{margin:0!important;background:{bg};--dsx-fg:{fg};height:auto!important;min-height:0!important;max-height:none!important;"
            f"width:auto!important;overflow:visible!important;display:block!important;position:static!important}}")
    return (f'<!doctype html><html {root.get("htmlAttrs", "")}><head><meta charset="utf-8">{links}<style>{css}</style><style>{page}{SHEET_CSS}</style></head>'
            f'<body {root.get("bodyAttrs", "")}><div class="dsx-sheet sheet" style="width:{width}px"><div class="sh-head"><div class="sh-kicker">{esc(kicker)}</div>'
            f'<div class="sh-title">{esc(title)}</div><div class="sh-desc">{esc(desc)}</div></div>{sections_html}</div>{script}</body></html>')
def render(html, name, width=1440):
    os.makedirs(f"{W}/build", exist_ok=True)
    p = f"{W}/build/{name}.html"; open(p, "w").write(html)
    r = subprocess.run([NODE, os.path.join(BROWSER, "render.mjs"), p, f"{W}/build/{name}.png", str(width)], capture_output=True, text=True)
    m = re.search(r"HEIGHT (\d+)", r.stdout)
    if not m: raise RuntimeError(r.stdout + r.stderr)
    return int(m.group(1)), r.stdout
def call(tool, args):
    t, err = doop_cli.call_tool(tool, {**args, "agent_name": AGENT})
    if err: raise RuntimeError(f"{tool}: {t[:500]}")
    try: return json.loads(t)
    except Exception:
        try: return json.JSONDecoder().raw_decode(t.lstrip())[0]
        except Exception: return {"raw": t}
# The manifest is the single record of progress: one row per published frame (id, page, source, viewed, passed).
# Every report number must come from it. All writes go through state_update, which holds a file lock,
# so two publishing scripts can run at once without losing rows.
def state_load():
    p = f"{W}/manifest.json"; return json.load(open(p)) if os.path.exists(p) else {"pages": {}, "frames": {}}
def state_save(s): json.dump(s, open(f"{W}/manifest.json", "w"), indent=1)
@contextlib.contextmanager
def state_update():
    with open(f"{W}/manifest.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX); s = state_load()
        try: yield s
        finally: state_save(s); fcntl.flock(lk, fcntl.LOCK_UN)
def page_id(key, name):
    """Return the canvas page id for a manifest page key, creating the page once."""
    with state_update() as s:
        if key not in s["pages"]:
            r = call("create_canvas_page", {"canvas_id": CANVAS, "name": name}); s["pages"][key] = (r.get("page") or {}).get("id") or r.get("id")
        return s["pages"][key]
def publish(key, name, page_id, html, width, height, x, y, source):
    """Create the frame the first time, replace it in place afterwards (idempotent by manifest key)."""
    e = state_load()["frames"].get(key)
    if e and e.get("id"):
        call("set_frame_html", {"frame_id": e["id"], "html": html})
        call("update_frame", {"frame_id": e["id"], "name": name, "x": x, "y": y, "width": width, "height": height})
        fid = e["id"]
    else:
        r = call("create_frame", {"canvas_id": CDS, "pageId": page_id, "name": name, "html": html, "x": x, "y": y, "width": width, "height": height})
        fid = r.get("id") or r.get("frame_id") or (r.get("frame") or {}).get("id")
        if not fid: raise RuntimeError(str(r)[:400])
    with state_update() as s:
        s["frames"][key] = {"id": fid, "name": name, "page": page_id, "x": x, "y": y, "w": width, "h": height, "source": source, "published": True, "viewed": False, "passed": False}
    return fid
