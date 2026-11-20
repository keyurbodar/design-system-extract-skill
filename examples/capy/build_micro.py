import json, re, sys
from sheetlib import *
src = json.load(open(f"{W}/micro_src.json")); o = json.load(open(f"{W}/out_micro.json"))
V = o["variants"]; CSS = css_text(o["css"])
def split_variants(u):
    parts = re.split(r":(?![^\[]*\])", u.replace("&gt;", ">")); return parts[:-1]
def ops_for(prefixes):
    t = {"c": [], "a": {}, "wc": [], "wa": {}, "fc": [], "fa": {}}; lab = []
    for p in prefixes:
        m = re.match(r"group-(hover|focus-visible|focus-within|active)(?:/([\w-]+))?$", p)
        if m:
            t["wc"] += ["group", "is-" + m.group(1)] + (["group/" + m.group(2)] if m.group(2) else []); lab.append("group " + m.group(1)); continue
        m = re.match(r"group-data-\[([\w-]+)(?:=([^\]]+))?\](?:/([\w-]+))?$", p)
        if m:
            t["wc"] += ["group"] + (["group/" + m.group(3)] if m.group(3) else []); t["wa"]["data-" + m.group(1)] = m.group(2) or ""; lab.append("group " + m.group(1)); continue
        m = re.match(r"in-data-\[?([\w-]+)(?:=([^\]]+))?\]?$", p)
        if m: t["wa"]["data-" + m.group(1)] = m.group(2) or ""; lab.append("in " + m.group(1)); continue
        m = re.match(r"data-\[([\w-]+)(?:=([^\]]+))?\]$", p)
        if m: t["a"]["data-" + m.group(1)] = m.group(2) or ""; lab.append(m.group(1) + ("=" + m.group(2) if m.group(2) else "")); continue
        m = re.match(r"aria-\[?([\w-]+)(?:=([^\]]+))?\]?$", p)
        if m: t["a"]["aria-" + m.group(1)] = m.group(2) or "true"; lab.append("aria-" + m.group(1)); continue
        if p in ("hover", "focus-visible", "focus", "focus-within", "active"): t["c"].append("is-" + p); lab.append(p); continue
        if p == "disabled": t["c"].append("is-disabled"); t["a"]["disabled"] = ""; lab.append("disabled"); continue
        if p == "has-[[data-popup-open]]": t["fa"]["data-popup-open"] = ""; lab.append("child popup-open"); continue
        if p in ("has-focus-visible", "has-[:focus-visible]"): t["fc"].append("is-focus-visible"); lab.append("child focus-visible"); continue
    return t, " + ".join(lab)
def tag_end(h):
    q = None
    for i, ch in enumerate(h):
        if q:
            if ch == q: q = None
        elif ch in "\"'": q = ch
        elif ch == ">": return i
    return -1
def apply_root(h, cls, attrs):
    e = tag_end(h); tag = h[:e]; rest = h[e:]
    if cls:
        m = re.search(r'\sclass="', tag)
        tag = (tag[:m.end()] + " ".join(cls) + " " + tag[m.end():]) if m else tag + f' class="{" ".join(cls)}"'
    for k, v in attrs.items():
        if re.search(rf"\s{re.escape(k)}(=|\s|$)", tag): continue
        tag += f' {k}="{esc(v)}"'
    return tag + rest
def pick(key):
    vs = [v for v in V.get(key, {}).values() if v["html"]]
    if not vs: return None
    return min(vs, key=lambda v: (0 if (v["text"] or "<svg" in v["html"]) else 1, v["w"] * v["h"]))
def cell(v, label, t=None, static=False, live=False):
    inh = v.get("inherit") or {}
    st = f"color:{inh.get('color','inherit')};font-size:{inh.get('fontSize','inherit')};line-height:{inh.get('lineHeight','inherit')};font-weight:{inh.get('fontWeight','inherit')};letter-spacing:{inh.get('letterSpacing','inherit')};"
    cls = "st-stage" + (" " + v["bgClass"] if v.get("bgClass") else "")
    if not v.get("bgClass") and v.get("bgColor"): st += f"background:{v['bgColor']};"
    h = v["html"]; wc = ""; wa = ""
    if t and not live:
        h = apply_root(h, t["c"], t["a"]); wc = " ".join(t["wc"]); wa = "".join(f' {k}="{esc(x)}"' for k, x in t["wa"].items())
    elif t:
        wc = " ".join(c for c in t["wc"] if not c.startswith("is-"))
    tg = ""
    if t and (live or t["fc"] or t["fa"]):
        tg = f" data-tg='{esc(json.dumps(t))}'" + (' data-static="1"' if not live else "")
    return (f'<div class="st-cell"><div class="{cls}" style="{st}"{tg}><div style="width:{v["w"]}px"><div data-w class="{wc}"{wa} style="display:contents">{h}</div></div></div>'
            f'<div class="st-lab">{esc(label)}</div></div>')
SCRIPT = """<script>(function(){var cells=[].slice.call(document.querySelectorAll('[data-tg]'));function ap(cell,on){var t=JSON.parse(cell.getAttribute('data-tg'));var wrap=cell.querySelector('[data-w]');var root=wrap?wrap.firstElementChild:null;if(!root)return;var fd=root.querySelector('button,a,[tabindex],input')||root.firstElementChild;function set(el,cls,attrs){if(!el)return;(cls||[]).forEach(function(c){if(c.indexOf('group')===0)el.classList.add(c);else el.classList.toggle(c,on);});Object.keys(attrs||{}).forEach(function(k){if(on)el.setAttribute(k,attrs[k]);else el.removeAttribute(k);});}set(root,t.c,t.a);set(wrap,t.wc,t.wa);set(fd,t.fc,t.fa);}cells.filter(function(c){return c.dataset.static;}).forEach(function(c){ap(c,true);});var on=false;setInterval(function(){on=!on;cells.filter(function(c){return !c.dataset.static;}).forEach(function(c){ap(c,on);});},1200);})();</script>"""
def empty(t): return not (t["c"] or t["a"] or t["wc"] or t["wa"] or t["fc"] or t["fa"])
def own_state(v):
    cl = re.search(r'class="([^"]*)"', v["html"][:tag_end(v["html"]) + 1]); cl = cl.group(1).replace("&gt;", ">").replace("&amp;", "&").split() if cl else []
    for want in ("hover", "data-[selected]", "data-[popup-open]", "focus-visible", "active"):
        for c in cl:
            pre = split_variants(c)
            if pre == [want]: return ops_for(pre)
    for c in cl:
        m = re.match(r"group-hover(/[\w-]+)?:", c)
        if m: return ops_for([c.rsplit(":", 1)[0]])
    return None, ""
gaps = []
def util_row(i, u):
    v = pick(f"u{i}"); pre = split_variants(u["utility"]); t, lab = ops_for(pre)
    meta = (f'<div class="st-meta"><div class="mi-u">{esc(u["utility"])}</div>' + "".join(f'<div class="mi-c">{esc(c)}</div>' for c in u["css"]) +
            "".join(f'<div class="mi-x">{esc(c)}</div>' for c in u["cond"]) + f'<div class="mi-w">{esc(u["count"])} elements · {esc((u["usedBy"] or [""])[0])}</div></div>')
    if not v:
        gaps.append(u["utility"]); return f'<div class="st-row">{meta}<div class="st-cells"><div class="mi-x">no element at or under 700×220 carries this class in the captures</div></div></div>'
    cells = cell(v, "rest")
    if not empty(t):
        cells += cell(v, lab or "state", t) + cell(v, "live · toggles every 1.2s", t, live=True)
    else:
        t2, lab2 = own_state(v)
        if t2 and not empty(t2): cells += cell(v, "with " + lab2, t2) + cell(v, "live · toggles every 1.2s", t2, live=True)
        else: cells += cell(v, "live", None)
    return f'<div class="st-row">{meta}<div class="st-cells">{cells}</div></div>'
ORDER = ["hover", "focus-visible", "active", "selected", "selected + unfocused", "selected + unfocused + hover", "popup-open", "disabled"]
def recipe_row(i, r):
    v = pick(f"r{i}")
    meta = f'<div class="st-meta"><div class="mi-u">{esc(r["owner"])}</div><div class="mi-x">seen {esc(r["seen"])}×</div><div class="mi-c">{esc(" ".join(r["classes"]))}</div></div>'
    if not v:
        gaps.append(r["owner"]); return f'<div class="st-row">{meta}<div class="st-cells"><div class="mi-x">no instance at or under 900×260 in the captures</div></div></div>'
    cols = {}
    for c in r["classes"]:
        t, lab = ops_for(split_variants(c))
        if lab and not empty(t) and lab not in cols: cols[lab] = t
    labs = sorted(cols, key=lambda l: (ORDER.index(l) if l in ORDER else 99, l))[:9]
    cells = cell(v, "rest") + "".join(cell(v, l, cols[l]) for l in labs)
    if labs: cells += cell(v, "live · " + labs[0], cols[labs[0]], live=True)
    return f'<div class="st-row">{meta}<div class="st-cells">{cells}</div></div>'
GROUPS = [("micro01", "Hover", ["Hover"]), ("micro02", "Focus, press and disabled", ["Focus", "Press", "Disabled"]),
          ("micro03", "Selected, open, highlighted and context", ["Selected · open · highlighted", "Context (in-data, group, aria)"]),
          ("micro04", "Enter, exit and animation", ["Enter · exit · animation"]), ("micro05", "Transition timing", ["Transition timing"])]
WIDTH = 1920
if __name__ == "__main__":
    res = {}
    for key, title, groups in GROUPS:
        body = ""
        for g in groups:
            rows = [util_row(i, u) for i, u in enumerate(src["utils"]) if u["group"] == g]
            body += section(g, f"{len(rows)} utilities", "".join(rows))
        html = doc("16 · MICRO-INTERACTIONS / VISUAL", title, "Each utility shown on a real captured element: at rest, with the state applied, and looping live so the transition can be seen. Hovering, focusing and pressing the specimens also works.", body, CSS, SCRIPT, WIDTH)
        h, _ = render(html, key, WIDTH); res[key] = {"name": f"Visual · {title}", "h": h, "bytes": len(html)}; print(key, h, len(html))
    n = len(src["recipes"]); half = (n + 1) // 2
    for pi, (a, b) in enumerate([(0, half), (half, n)], 1):
        body = section("Components", f"{b - a} of {n}", "".join(recipe_row(i, src["recipes"][i]) for i in range(a, b)))
        html = doc("16 · MICRO-INTERACTIONS / VISUAL", f"Interaction recipes by component ({pi}/2)", "Each source component rendered from the captures in every state its classes define: rest, hover, focus, press, selected, open, disabled, plus a live loop.", body, CSS, SCRIPT, WIDTH)
        key = f"micro_recipes_{pi}"; h, _ = render(html, key, WIDTH); res[key] = {"name": f"Visual · Recipes by component ({pi}/2)", "h": h, "bytes": len(html)}; print(key, h, len(html))
    json.dump(res, open(f"{W}/build/micro_index.json", "w")); json.dump(gaps, open(f"{W}/build/micro_gaps.json", "w"))
    print("gaps (no specimen):", len(gaps), gaps[:12])
