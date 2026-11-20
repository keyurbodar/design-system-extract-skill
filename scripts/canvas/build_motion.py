"""Step 10b. One frame per interaction from motion.mjs output.
usage: python3 build_motion.py [--page-key motion] [--page-name "Motion"] [key ...]
Frame = the full real screen replaying the interaction at real speed (CSS steps over a sprite of the captured frames),
plus a band with the trigger, the measured transitions (element, property, duration, delay, easing) and a zoomed
filmstrip of the affected region with an 8x slower loop. Nothing is drawn: every pixel is a screenshot of the live app."""
import json, os, sys, glob
from PIL import Image
from sheetlib import *
import hostassets
M = f"{W}/motion"; BAND = 440
COLOR = ("color", "background-color", "border-color", "outline-color", "fill", "stroke", "text-decoration-color", "box-shadow")
def sprite(key, n, fw, fh):
    out = f"{M}/{key}/sprite.webp"
    if not os.path.exists(out):
        sh = Image.new("RGB", (fw, fh * n))
        for i in range(n): sh.paste(Image.open(f"{M}/{key}/f{i}.png").convert("RGB").resize((fw, fh)), (0, i * fh))
        sh.save(out, "WEBP", quality=86, method=4)
    return out
def region(meta, fw, fh):
    """Crop for the filmstrip: the trigger, any popup that appeared, and every element that moves, fades or resizes.
    Colour-only transitions far from the trigger are ignored (they are usually the pointer leaving another control)."""
    t = meta.get("tbox"); xs = []
    tb = (t["x"], t["y"], t["x"] + t["width"], t["y"] + t["height"]) if t else None
    if tb: xs.append(tb)
    for r in meta.get("rects", []):
        x1, y1, x2, y2 = r["rect"]
        if x2 - x1 < 2 or y2 - y1 < 2 or (x2 - x1) > fw * 0.98: continue
        near = tb and not (x2 < tb[0] - 4 or x1 > tb[2] + 4 or y2 < tb[1] - 4 or y1 > tb[3] + 4)
        if r["prop"] not in COLOR or near or not tb: xs.append((x1, y1, x2, y2))
    if not xs: return (0, 0, fw, fh)
    x1 = min(a[0] for a in xs) - 28; y1 = min(a[1] for a in xs) - 28; x2 = max(a[2] for a in xs) + 28; y2 = max(a[3] for a in xs) + 28
    w = min(max(x2 - x1, 200), fw); h = min(max(y2 - y1, 120), fh); cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    return (int(max(0, min(fw - w, cx - w / 2))), int(max(0, min(fh - h, cy - h / 2))), int(w), int(h))
def kf(name, n, hold0, play, hold1):
    total = hold0 + play + hold1; steps = []
    for i in range(n):
        t = 0 if i == 0 else hold0 + play * (i / (n - 1))
        steps.append(f"{min(100, t / total * 100):.3f}%{{background-position-y:calc(var(--oy) - {i} * var(--fh))}}")
    steps.append(f"100%{{background-position-y:calc(var(--oy) - {n - 1} * var(--fh))}}")
    return f"@keyframes {name}{{{''.join(steps)}}}", total
def css(fw, fh, bg, fg):
    return f"""*{{box-sizing:border-box}}html,body{{margin:0;background:{bg};color:{fg};font:13px/1.45 ui-sans-serif,system-ui,sans-serif;--mut:color-mix(in srgb,{fg} 58%,transparent);--dim:color-mix(in srgb,{fg} 38%,transparent);--line:color-mix(in srgb,{fg} 12%,transparent);--mono:ui-monospace,SFMono-Regular,Menlo,monospace}}
.stage{{width:{fw}px;height:{fh}px;background-repeat:no-repeat;--fh:{fh}px;--oy:0px;border-bottom:1px solid var(--line)}}
.band{{display:grid;grid-template-columns:{min(600, fw)}px 1fr;gap:32px;padding:24px 32px;height:{BAND}px;overflow:hidden}}
.kick{{font:11px/1.4 var(--mono);color:var(--dim);margin-bottom:6px;letter-spacing:.04em}}.ttl{{font-size:20px;font-weight:600;line-height:1.2}}.how{{margin-top:6px;color:var(--mut)}}
table{{width:100%;border-collapse:collapse;margin-top:14px;font-size:12px}}th{{text-align:left;font-weight:500;color:var(--dim);padding:4px 6px;border-bottom:1px solid var(--line)}}
td{{padding:4px 6px;border-bottom:1px solid var(--line);font-family:var(--mono);vertical-align:top;word-break:break-word}}td.m{{color:var(--mut)}}td.n{{white-space:nowrap}}
.strip{{display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap;overflow:hidden}}.cell{{display:flex;flex-direction:column;gap:6px;flex:none}}
.crop{{background-repeat:no-repeat;border:1px solid var(--line);border-radius:8px}}.lab,.note{{font:11px/1.4 var(--mono);color:var(--dim)}}.note{{margin-top:8px}}"""
def build(key, kicker, bg, fg):
    meta = json.load(open(f"{M}/{key}/meta.json")); n = meta["frames"]; fw, fh = meta.get("w", 1600), meta.get("h", 1000)
    url = hostassets.upload("image/webp", open(sprite(key, n, fw, fh), "rb").read())
    T = meta["T"] or 0; real = max(T, 120) if n > 2 else 300
    k1, tot1 = kf("play", n, 900, real, 1300); k2, tot2 = kf("slow", n, 700, real * 8, 1100)
    rx, ry, rw, rh = region(meta, fw, fh); narrow = fw < 900
    avail = fw - 64 - (0 if narrow else 600 + 32); ncell = n + 1
    z = min(((avail - 10 * (ncell - 1)) / ncell) / rw, 340 / rh, 1.6)
    if z < 0.45 or (rh * z < 120 and ncell > 4):
        per = -(-ncell // 2); z = min(((avail - 10 * (per - 1)) / per) / rw, 165 / rh, 1.6)
    def crop(i, anim=False):
        st = f"width:{rw * z:.1f}px;height:{rh * z:.1f}px;background-image:url('{url}');background-size:{fw * z:.1f}px auto;background-position:{-rx * z:.1f}px {-(i * fh + ry) * z:.1f}px;"
        if anim: st += f"--fh:{fh * z:.1f}px;--oy:{-ry * z:.1f}px;animation:slow {tot2}ms steps(1,end) infinite;"
        return f'<div class="crop" style="{st}"></div>'
    labs = (["before"] + [f"{round(T * i / (n - 2))}ms" for i in range(1, n - 1)] + ["settled"]) if n > 2 else ["before", "after"]
    cells = "".join(f'<div class="cell">{crop(i)}<div class="lab">{labs[i]}</div></div>' for i in range(n)) + f'<div class="cell">{crop(0, True)}<div class="lab">loop · 8× slower</div></div>'
    rows = sorted(meta["rows"], key=lambda r: (-r["dur"], r["el"]))
    tbl = ("<table><thead><tr><th>Element</th><th>Property</th><th>Duration</th><th>Delay</th><th>Easing</th></tr></thead><tbody>" +
           "".join(f'<tr><td class="m">{esc(r["el"])}</td><td>{esc(r["prop"])}</td><td class="n">{r["dur"]}ms</td><td class="n">{r["delay"]}ms</td><td class="m n">{esc(r["ease"])}</td></tr>' for r in rows[:9]) +
           "</tbody></table>") if rows else '<div class="note">No CSS transition or animation was running after the trigger: the state changes in one frame, or it is driven by script.</div>'
    more = f'<div class="note">+ {len(rows) - 9} more transitions</div>' if len(rows) > 9 else ""
    band_cols = "grid-template-columns:1fr;height:auto;" if narrow else ""
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css(fw, fh, bg, fg)}{k1}{k2}</style></head><body>'
            f'<div class="stage" style="background-image:url(\'{url}\');background-size:{fw}px auto;animation:play {tot1}ms steps(1,end) infinite"></div>'
            f'<div class="band" style="{band_cols}"><div><div class="kick">{esc(kicker)} / {esc(str(meta.get("group", "")).upper())}</div><div class="ttl">{esc(meta["name"])}</div>'
            f'<div class="how">Trigger: {esc(meta.get("trigger") or "")}. Total {T}ms. The screen above replays it at real speed.</div>{tbl}{more}</div>'
            f'<div><div class="strip">{cells}</div></div></div></body></html>')
    open(f"{M}/{key}/frame.html", "w").write(html)
    return meta, html, fw, fh + (BAND if not narrow else BAND + 420)
if __name__ == "__main__":
    a = sys.argv[1:]; opt = {"--page-key": "motion", "--page-name": "Motion", "--bg": "#0b0b0c", "--fg": "#ececec", "--kicker": "MOTION"}
    while a and a[0] in opt: opt[a[0]] = a[1]; a = a[2:]
    order = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(f"{M}/*/meta.json")); keys = a or order
    metas = {k: json.load(open(f"{M}/{k}/meta.json")) for k in order}; groups = list(dict.fromkeys(m.get("group", "") for m in metas.values()))
    pid = page_id(opt["--page-key"], opt["--page-name"])
    pos = {}; y = 0
    for g in groups:
        ks = [k for k in order if metas[k].get("group", "") == g]
        for i, k in enumerate(ks): pos[k] = (i * (metas[k].get("w", 1600) + 120), y)
        y += max(metas[k].get("h", 1000) for k in ks) + BAND + 620
    for k in keys:
        try:
            meta, html, w, h = build(k, opt["--kicker"], opt["--bg"], opt["--fg"]); x, yy = pos[k]
            print("ok", k, publish("motion_" + k, f"Motion · {meta.get('group', '')} · {meta['name']}", pid, html, w, h, x, yy, "live app, frames at measured transition times"), "T", meta["T"], flush=True)
        except Exception as ex: print("FAIL", k, str(ex)[:200], flush=True)
