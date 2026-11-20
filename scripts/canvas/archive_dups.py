"""Step 12. Remove duplicate load without deleting anything.
usage: python3 archive_dups.py [--apply]        (needs backup.py output; without --apply it only prints the plan)
Two frames are duplicates only when their HTML is byte-identical. For each group the first frame (page order, then name) stays;
the others move to an "Archive" page. Original page and position of every moved frame are saved in archive_map.json, so the
move can be undone, and the kept/moved list is written to archive_report.json for the user."""
import json, hashlib, os, sys
from collections import defaultdict
from sheetlib import *
apply = "--apply" in sys.argv
c = json.load(open(f"{W}/backup/canvas.json")); pages = {p["id"]: p["name"] for p in c["pages"]}; order = {p["id"]: i for i, p in enumerate(c["pages"])}
groups = defaultdict(list)
for f in c["frames"]:
    h = json.load(open(f"{W}/backup/frames/{f['id']}.json"))["html"]; groups[hashlib.sha1(h.encode()).hexdigest()].append(f)
dups = [sorted(v, key=lambda f: (order[f["pageId"]], f["name"])) for v in groups.values() if len(v) > 1]
dups.sort(key=lambda v: (order[v[0]["pageId"]], v[0]["name"]))
MAP = f"{W}/archive_map.json"; amap = json.load(open(MAP)) if os.path.exists(MAP) else {}
pid = page_id("archive", "Archive — exact duplicate frames (moved, not deleted)") if apply and dups else None
y = 0; report = []
for g in dups:
    keep, extra = g[0], g[1:]; x = 0
    report.append({"kept": keep["name"], "kept_id": keep["id"], "kept_page": pages[keep["pageId"]], "moved": [(f["name"], pages[f["pageId"]]) for f in extra]})
    for f in extra:
        if apply and f["id"] not in amap:
            try:
                call("update_frame", {"frame_id": f["id"], "pageId": pid, "x": x, "y": y})
                amap[f["id"]] = {"name": f["name"], "from_page": f["pageId"], "x": f["x"], "y": f["y"], "same_as": keep["id"]}; json.dump(amap, open(MAP, "w"), indent=1)
            except Exception as ex: print("FAIL", f["id"], str(ex)[:150])
        x += f["width"] + 80
    y += max(f["height"] for f in extra) + 160
json.dump(report, open(f"{W}/archive_report.json", "w"), indent=1)
print("duplicate groups", len(dups), "| extra frames", sum(len(g) - 1 for g in dups), "| moved so far", len(amap), "" if apply else "| DRY RUN (pass --apply to move)")
for r in report: print(f"- kept '{r['kept']}' ({r['kept_page'][:28]}) · {len(r['moved'])} duplicate(s): " + ", ".join(n for n, _ in r["moved"][:3]) + (" …" if len(r["moved"]) > 3 else ""))
