"""Step 8b. Build component sheets from extract.mjs output and (optionally) publish them.
usage: python3 build_sheets.py <extract_out.json> <sheets.json> [--publish] [sheet_key ...]

sheets.json = {
  "page": {"key": "components", "name": "Components — cut from live screens"},
  "kicker": "COMPONENTS", "width": 2400, "max_height": 14000,
  "sheets": [
    {"key": "s01", "name": "Messages", "desc": "…",
     "sections": [ {"title": "User message", "variant": "user-message"},                 # every distinct variant
                   {"title": "Agent message", "variant": "agent-message", "pick": "reps", "max_h": 1400} ] }   # one per feature cluster
  ]
}
"variant" is a target key from the extract job. Nothing here draws UI: every specimen is the captured element's own outerHTML
rendered with the site's own CSS."""
import json, re, sys
from collections import defaultdict
from sheetlib import *
GENERIC = {"button", "tooltip-trigger", "menu-trigger", "scroll-area", "scroll-area-viewport"}
def feat(v):
    """Feature fingerprint of a variant: which parts/states/tags it contains. Variants with the same fingerprint are one cluster."""
    h = v["html"] or ""
    s = set(re.findall(r'data-(?:slot|component|testid)="([^"]+)"', h)) - GENERIC
    s |= set("st:" + a for a in re.findall(r'data-(?:state|status|tone|variant)="([^"]+)"', h))
    s |= set("tag:" + t for t in re.findall(r'<(table|pre|ul|ol|blockquote|h1|h2|h3|h4|img|video|details|code|hr|a|svg|input|textarea)\b', h))
    return frozenset(s)
def pick(V, sec):
    vs = [v for v in V.get(sec["variant"], {}).values() if v.get("html") and (not sec.get("max_h") or v["h"] <= sec["max_h"])]
    vs.sort(key=lambda v: (v["h"], v["w"]))
    if sec.get("pick") == "reps":
        cl = defaultdict(list)
        for v in vs: cl[feat(v)].append(v)
        vs = sorted([c[0] for c in cl.values()], key=lambda v: (v["h"], v["w"]))
    return vs[: sec.get("limit", 10**9)]
def body(secs):
    out = ""
    for title, vs in secs:
        if vs: out += section(title, f"{len(vs)} distinct", '<div class="sp-grid">' + "".join(spec(v, v["text"][:48]) for v in vs) + "</div>")
    return out
def split(secs, parts):
    flat = [(t, v) for t, vs in secs for v in vs]; tot = sum(v["h"] + 70 for _, v in flat); out = [[] for _ in range(parts)]; acc = 0
    for t, v in flat:
        i = min(parts - 1, int(acc / (tot / parts))); acc += v["h"] + 70
        if out[i] and out[i][-1][0] == t: out[i][-1][1].append(v)
        else: out[i].append((t, [v]))
    return out
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; do_publish = "--publish" in sys.argv
    o = json.load(open(args[0])); cfg = json.load(open(args[1])); only = args[2:]
    V = o["variants"]; css = css_text(o["css"]); root = o.get("root"); width = cfg.get("width", 2400); limit = cfg.get("max_height", 14000)
    built = []
    for sh in cfg["sheets"]:
        if only and sh["key"] not in only: continue
        secs = [(s["title"], pick(V, s)) for s in sh["sections"]]
        for s, (t, vs) in zip(sh["sections"], secs):
            if not vs: print(f"  EMPTY section '{t}' (variant {s['variant']}): no specimen found, nothing drawn in its place")
        html = doc(cfg.get("kicker", ""), sh["name"], sh.get("desc", ""), body(secs), css, width=width, root=root)
        h, _ = render(html, sh["key"], width); parts = [(sh["key"], sh["name"], html, h)]
        if h > limit:  # tall sheets do not screenshot or review well: split them
            n = -(-h // limit); parts = []
            for i, ps in enumerate(split(secs, n), 1):
                nm = f'{sh["name"]} ({i}/{n})'; html = doc(cfg.get("kicker", ""), nm, sh.get("desc", ""), body(ps), css, width=width, root=root)
                k = f'{sh["key"]}_{i}'; h, _ = render(html, k, width); parts.append((k, nm, html, h))
        for k, nm, html, h in parts:
            print(k, nm, "specimens", html.count('class="sp"'), "height", h, "bytes", len(html)); built.append((k, nm, html, h))
    if do_publish:
        pid = page_id(cfg["page"]["key"], cfg["page"]["name"]); x = 0
        for k, nm, html, h in built:
            try: print("published", k, publish("sheet_" + k, nm, pid, html, width, h, x, 0, "cut from captured screens"))
            except Exception as ex: print("FAIL", k, str(ex)[:300])
            x += width + 120
