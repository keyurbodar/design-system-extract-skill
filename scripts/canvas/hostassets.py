"""Step 5. Doop refuses frames that embed base64 data: URIs. Upload each one once and rewrite the snapshot to the hosted URL.
usage: python3 hostassets.py [key ...]        (default: every ok capture in snaps/index.json)
Uploads are throttled to stay under 15 per minute per account and cached by sha1 in assets/map.json, so reruns are free."""
import json, re, sys, os, base64, hashlib, subprocess, time, urllib.parse
from sheetlib import *
os.makedirs(f"{W}/assets", exist_ok=True)
MAP = f"{W}/assets/map.json"
m = json.load(open(MAP)) if os.path.exists(MAP) else {}
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/gif": "gif", "image/svg+xml": "svg"}
RX = re.compile(r'data:(image/[a-z+.-]+)(;charset=[\w-]+)?(;base64)?,([^"\')\s]+)')
last = [0.0]
def upload(mime, raw):
    h = hashlib.sha1(raw).hexdigest()
    if h in m: return m[h]
    p = f"{W}/assets/{h}.{EXT.get(mime, 'bin')}"; open(p, "wb").write(raw)
    for attempt in range(5):
        wait = 4.3 - (time.time() - last[0])
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        try:
            t = call("upload_asset", {"canvas_id": CDS, "local_file": True})
            out = subprocess.run(["curl", "-sS", "-T", p, t["upload_url"]], capture_output=True, text=True, timeout=180).stdout
            url = json.loads(out).get("url")
            if url:
                m[h] = url; json.dump(m, open(MAP, "w")); return url
            err = out[:200]
        except Exception as e: err = str(e)[:200]
        time.sleep(8 * (attempt + 1))
    raise RuntimeError("upload failed: " + err)
def host(html):
    n = [0]
    def rep(mo):
        mime, _, b64, data = mo.groups()
        if mime not in EXT: return mo.group(0)
        try: raw = base64.b64decode(data) if b64 else urllib.parse.unquote(data).encode()
        except Exception: return mo.group(0)
        n[0] += 1; return upload(mime, raw)
    return RX.sub(rep, html), n[0]
if __name__ == "__main__":
    idx = json.load(open(f"{W}/snaps/index.json"))
    for k in (sys.argv[1:] or [k for k in idx if idx[k].get("ok")]):
        p = f"{W}/snaps/{k}.html"; h = open(p).read()
        if "data:image" not in h: continue
        try:
            h2, n = host(h); open(p, "w").write(h2); print("hosted", k, n, len(h), "->", len(h2), "left:", len(RX.findall(h2)))
        except Exception as e: print("FAIL", k, str(e)[:200])
