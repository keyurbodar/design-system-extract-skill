"""Step 6. Publish captured snapshots as frames, grouped onto pages.
usage: python3 publish_snaps.py <pages.json> [key ...]     (keys given = republish those even if already published)
pages.json = { "<page_key>": {"name": "Live — Sidebar & composer", "groups": ["sidebar", "composer"], "cols": 6}, ... }
A scenario's "group" decides its page. Frames keep the capture's viewport size. Idempotent: reruns only publish what is missing."""
import json, sys
from sheetlib import *
pages = json.load(open(sys.argv[1])); only = sys.argv[2:]
idx = json.load(open(f"{W}/snaps/index.json")); src = os.environ.get("DSX_BASE_URL", "live app")
for pk, pg in pages.items():
    keys = [k for k in idx if idx[k].get("ok") and idx[k].get("group") in pg["groups"]]
    if not keys: continue
    pid = page_id(pk, pg["name"]); cols = pg.get("cols", 6)
    for i, k in enumerate(keys):
        e = idx[k]; mk = "live_" + k; cur = state_load()["frames"].get(mk)
        x, y = (i % cols) * (e["w"] + 80), (i // cols) * (e["h"] + 120)
        try:
            if cur and cur.get("id") and k not in only:
                if cur.get("page") != pid or cur.get("x") != x or cur.get("y") != y:
                    call("update_frame", {"frame_id": cur["id"], "pageId": pid, "x": x, "y": y})
                    with state_update() as s: s["frames"][mk].update({"page": pid, "x": x, "y": y})
                    print("moved", k)
                continue
            html = open(f"{W}/snaps/{k}.html").read()
            if "data:image" in html: print("SKIP", k, "(still has data: URIs; run hostassets.py first)"); continue
            print("ok", k, publish(mk, e["name"], pid, html, e["w"], e["h"], x, y, f"{src} {e['url']}"), flush=True)
        except Exception as ex: print("FAIL", k, str(ex)[:200], flush=True)
