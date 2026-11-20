"""Step 2. Back up the target canvas before writing to it: canvas.json plus one JSON per frame with its full HTML.
usage: python3 backup.py      (reads DSX_CANVAS, writes $DSX_WORK/backup). Safe to rerun: frames already saved are skipped.
Also the input for archive_dups.py and for mining an existing canvas with extract.mjs."""
import json, sys, os, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doop_cli
CDS=os.environ["DSX_CANVAS"]
OUT=os.path.join(os.environ.get("DSX_WORK", os.getcwd()), "backup"); os.makedirs(OUT + "/frames", exist_ok=True)
txt, err = doop_cli.call_tool("get_canvas", {"canvas_id": CDS})
canvas = json.loads(txt)
json.dump(canvas, open(f"{OUT}/canvas.json","w"))
frames = canvas["frames"]
print("frames", len(frames), "pages", len(canvas["pages"]), "components", len(canvas.get("components") or []), "tokens", len(canvas.get("tokens") or []))
def get(fr):
    p=f"{OUT}/frames/{fr['id']}.json"
    if os.path.exists(p) and os.path.getsize(p)>50: return "cached"
    for a in range(4):
        try:
            t, e = doop_cli.call_tool("get_frame", {"canvas_id": CDS, "frame_id": fr["id"]})
            j=json.loads(t)
            if not j.get("html"): raise RuntimeError("no html: "+t[:200])
            json.dump(j, open(p,"w"))
            return "ok"
        except Exception as ex:
            last=str(ex)[:200]; time.sleep(1+a)
    return "FAIL "+last
with ThreadPoolExecutor(16) as ex:
    res=list(ex.map(get, frames))
from collections import Counter
print(Counter(r.split()[0] for r in res))
for fr,r in zip(frames,res):
    if r.startswith("FAIL"): print(fr["id"], fr["name"], r)
