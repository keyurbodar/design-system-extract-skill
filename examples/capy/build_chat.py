import json, re, sys
from collections import defaultdict
from sheetlib import *
o = json.load(open(f"{W}/out_chat.json"))
V = o["variants"]; CSS = css_text(o["css"])
GEN = {"button","tooltip-trigger","menu-trigger","preview-card-trigger","context-menu-trigger","kbd","button-icon","scroll-area","scroll-area-viewport","scroll-area-scrollbar","scroll-area-thumb"}
def feat(v):
    h = v["html"] or ""
    s = set(re.findall(r'data-(?:slot|component)="([^"]+)"', h)) - GEN
    s |= set("st:" + a for a in re.findall(r'data-(?:state|status|tone)="([^"]+)"', h))
    s |= set("tag:" + t for t in re.findall(r'<(table|pre|ul|ol|blockquote|h1|h2|h3|h4|img|video|details|code|hr|a)\b', h))
    if "data-panel-open" in h: s.add("panel-open")
    return frozenset(s)
def allv(k, maxh=None):
    vs = [v for v in V.get(k, {}).values() if v["html"] and (not maxh or v["h"] <= maxh)]
    return sorted(vs, key=lambda v: (v["h"], v["w"]))
def reps(k, maxh=2400):
    cl = defaultdict(list)
    for v in allv(k, maxh): cl[feat(v)].append(v)
    return sorted([min(vs, key=lambda v: v["h"]) for vs in cl.values()], key=lambda v: (v["h"], v["w"]))
def grid(vs, lab): return '<div class="sp-grid">' + "".join(spec(v, lab(v) if callable(lab) else lab) for v in vs) + '</div>'
def sec(title, vs, lab=None):
    if not vs: return ""
    return section(title, f"{len(vs)} distinct", grid(vs, lab if lab is not None else (lambda v: v["text"][:48])))
SHEETS = [
 ("chat01", "Chat UX · 01 Status, live & streaming indicators", "Live status line, shimmer text, the 3×3 dot grid in each state, the time stamp, the scroll pill and the progress edge. Animations run live.",
  [("Dot grid (svg[data-state])", allv("dotgrid")), ("Live status", allv("slot:live-status")), ("Shimmer text", allv("slot:shimmer-text")),
   ("Chat stamp", allv("slot:chat-stamp")), ("Scroll-to-end pill", allv("slot:chat-scroll-pill")), ("Progress edge", allv("slot:progress-edge")), ("Visual", allv("slot:visual"))]),
 ("chat02", "Chat UX · 02 Activity line & work log", "The activity line that heads each run of agent work, collapsed and expanded, and the work-group panel it opens.",
  [("Activity line", reps("slot:activity-line")), ("Work-group panel", allv("slot:work-group-panel", 2400))]),
 ("chat03", "Chat UX · 03 Steps, tool calls & reasoning", "Every distinct step inside a work-group panel: reasoning text, thinking, tool calls closed and open, shell commands, file references and results.",
  [("Step (one collapsible each: thought, tool call, result)", allv("stepitem", 1600)), ("Step text", allv("stepmd")), ("Step groups", allv("step", 2400)), ("Components", [v for v in allv("component", 1200) if 'data-component="markdown"' not in v["html"][:400]])]),
 ("chat04", "Chat UX · 04 Messages", "User and agent messages with their header, sections, clamped body and footer actions.",
  [("User message", allv("slot:user-message")), ("Message header", allv("slot:message-header")), ("Message footer", allv("slot:message-footer")),
   ("Clamped body", allv("slot:clamped-body")), ("Message section", reps("slot:message-section", 900)), ("Agent message", reps("slot:agent-message", 1400))]),
 ("chat05", "Chat UX · 05 Markers, questions, requests & cards", "Waiting markers, marker rows, the clarify (ask-user) takeover, environment and secret requests, MCP setup, alerts and cards.",
  [("Waiting marker", allv("slot:waiting-marker")), ("Marker row", allv("slot:marker-row")), ("Clarify takeover (ask user)", allv("slot:clarify-takeover")),
   ("Request takeover (secrets / environment)", allv("slot:request-takeover")), ("Variable row", allv("slot:variable-row")), ("MCP setup line", allv("slot:mcp-setup-line")),
   ("Alert", allv("slot:alert")), ("Automation message", allv("slot:automation-message")), ("Card", allv("slot:card")), ("Preview card content", allv("slot:preview-card-content"))]),
 ("chat06", "Chat UX · 06 Markdown, code & media", "Markdown blocks, code blocks with their header, file headers, tables, diagrams, galleries and video.",
  [("Markdown blocks", reps("mdblock", 900)), ("Code block", allv("codeblock")), ("File header", allv("filehdr")), ("Table", allv("slot:markdown-table")),
   ("Mermaid diagram", allv("slot:markdown-mermaid-diagram")), ("Gallery", allv("slot:markdown-gallery")), ("Mixed media gallery", allv("slot:media-gallery-mixed")), ("Video player", allv("slot:video-player"))]),
 ("chat07", "Chat UX · 07 Composer", "Every distinct composer state found in the thread captures.", [("Composer", allv("slot:composer"))]),
 ("chat08", "Chat UX · 08 Transcript rows", "One row per distinct composition of the parts above, as they appear in the transcript.", [("Rows", reps("row", 1600))]),
]
WIDTH = 2960; LIMIT = 14000
def build(key, name, desc, secs, part=None, total=None):
    body = "".join(sec(t, vs) for t, vs in secs if vs)
    title = name.split(" · ", 1)[1].split(" ", 1)[1] + (f" ({part}/{total})" if part else "")
    html = doc("23 · CHAT UX SYSTEM", title, desc, body, CSS, width=WIDTH)
    k = key + (f"_{part}" if part else "")
    h, _ = render(html, k, WIDTH)
    return k, html, h
def split(secs, parts):
    flat = [(t, v) for t, vs in secs for v in vs]
    tot = sum(v["h"] + 70 for _, v in flat); out = [[] for _ in range(parts)]; acc = 0
    for t, v in flat:
        i = min(parts - 1, int(acc / (tot / parts))); acc += v["h"] + 70
        if out[i] and out[i][-1][0] == t: out[i][-1][1].append(v)
        else: out[i].append((t, [v]))
    return out
if __name__ == "__main__":
    only = sys.argv[1:]; res = {}
    for key, name, desc, secs in SHEETS:
        if only and key not in only: continue
        k, html, h = build(key, name, desc, secs)
        outs = [(k, name, html, h)]
        if h > LIMIT:
            parts = -(-h // LIMIT); outs = []
            for i, ps in enumerate(split(secs, parts), 1):
                k, html, h = build(key, name, desc, ps, i, parts); outs.append((k, f"{name} ({i}/{parts})", html, h))
        for k, nm, html, h in outs:
            res[k] = {"name": nm, "h": h, "bytes": len(html), "n": html.count('class="sp"')}
            print(k, nm, "specimens", res[k]["n"], "height", h, "bytes", len(html))
    json.dump(res, open(f"{W}/build/chat_index.json", "w"))
