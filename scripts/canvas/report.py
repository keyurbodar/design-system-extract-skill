"""Step 13. The only source of numbers for a status report.
usage:
  python3 report.py                      print the report (per page: published, viewed, passed; open items; motion gaps; archive)
  python3 report.py --viewed <key> ...   mark frames as viewed AFTER you opened their contact sheet (add --fail to mark them failed)
  python3 report.py --viewed-page <page_key> [--fail]
A frame is "viewed" only if you looked at its canvas render, and "passed" only if it matched the live app.
Never report a count that this script did not print."""
import json, os, sys, glob
from collections import defaultdict
from sheetlib import *
a = sys.argv[1:]
if a and a[0] in ("--viewed", "--viewed-page"):
    ok = "--fail" not in a; keys = [k for k in a[1:] if k != "--fail"]
    with state_update() as s:
        n = 0
        for k, e in s["frames"].items():
            hit = (e.get("page") == s["pages"].get(keys[0])) if a[0] == "--viewed-page" else (k in keys)
            if hit: e["viewed"] = True; e["passed"] = ok; n += 1
    print("marked", n, "viewed,", "passed" if ok else "FAILED"); sys.exit(0)
s = state_load(); names = {v: k for k, v in s["pages"].items()}; by = defaultdict(list)
for k, e in s["frames"].items(): by[names.get(e.get("page"), e.get("page"))].append((k, e))
tot = [0, 0, 0]
print(f"{'page':28} {'published':>9} {'viewed':>7} {'passed':>7}")
for pg, fr in by.items():
    v = sum(1 for _, e in fr if e.get("viewed")); p = sum(1 for _, e in fr if e.get("passed"))
    print(f"{str(pg)[:28]:28} {len(fr):9} {v:7} {p:7}"); tot[0] += len(fr); tot[1] += v; tot[2] += p
print(f"{'TOTAL':28} {tot[0]:9} {tot[1]:7} {tot[2]:7}")
nv = [k for k, e in s["frames"].items() if not e.get("viewed")]; nf = [(k, e.get("diff")) for k, e in s["frames"].items() if e.get("viewed") and not e.get("passed")]
print(f"\nNOT VIEWED ({len(nv)}):", ", ".join(nv[:40]) + (" …" if len(nv) > 40 else ""))
print(f"VIEWED BUT NOT PASSED ({len(nf)}):", ", ".join(f"{k}({d}%)" if d is not None else k for k, d in nf[:40]) + (" …" if len(nf) > 40 else ""))
idx = f"{W}/snaps/index.json"
if os.path.exists(idx):
    i = json.load(open(idx)); bad = [k for k, v in i.items() if not v.get("ok")]; unpub = [k for k, v in i.items() if v.get("ok") and "live_" + k not in s["frames"]]
    print(f"CAPTURES: {len(i)} total, {len(bad)} failed {bad[:20]}, {len(unpub)} captured but not published {unpub[:20]}")
metas = [json.load(open(p)) for p in glob.glob(f"{W}/motion/*/meta.json")]
if metas:
    none = [m["key"] for m in metas if not m.get("rows")]; unpub = [m["key"] for m in metas if "motion_" + m["key"] not in s["frames"]]
    print(f"MOTION: {len(metas)} interactions captured, {len(none)} with no measured transition {none[:20]}, {len(unpub)} not published {unpub[:20]}")
if os.path.exists(f"{W}/archive_report.json"):
    r = json.load(open(f"{W}/archive_report.json")); print(f"ARCHIVE: {len(r)} duplicate groups, {sum(len(g['moved']) for g in r)} extra frames")
if os.path.exists(f"{W}/coverage.md"):
    t = open(f"{W}/coverage.md").read(); print(f"COVERAGE: {t.count('[x]')} done, {t.count('[ ]')} open, {t.count('[-]')} not in this app")
else: print("COVERAGE: coverage.md is missing. Copy references/coverage-checklist.md into the work dir and fill it in.")
