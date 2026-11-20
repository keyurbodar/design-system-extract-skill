#!/usr/bin/env python3
"""Step 7a. Contact sheets: one image per canvas page with every frame's real canvas render, labelled with id and name.
usage: sheets.py <canvas_id> [page-name-substring ...] [--refresh] [--cols=4] [--cw=520]
This is how you LOOK at what is on the canvas. Open every sheet you report on. Renders are downloaded to $DSX_WORK/thumbs
(max 5 in parallel: more gets HTTP 429) and sheets are written to $DSX_WORK/sheets."""
import json, sys, os, io, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import doop_cli
W=os.environ.get("DSX_WORK", os.getcwd())
os.makedirs(f"{W}/thumbs", exist_ok=True); os.makedirs(f"{W}/sheets", exist_ok=True)
def canvas(cid):
    t,_=doop_cli.call_tool("get_canvas", {"canvas_id": cid}); return json.loads(t)
def fetch(fid, refresh=False, scale=1):
    p=f"{W}/thumbs/{fid}.png"
    if os.path.exists(p) and not refresh: return p
    for a in range(4):
        try:
            req=urllib.request.Request(f"https://doop.design/i/{fid}.png?scale={scale}&t={int(time.time())}", headers={"User-Agent":"Mozilla/5.0"})
            d=urllib.request.urlopen(req, timeout=120).read()
            open(p,"wb").write(d); return p
        except Exception as e:
            err=e; time.sleep(2+a)
    print("FAIL thumb", fid, err); return None
def sheet(frames, out, cell_w=520, cols=4, title=""):
    try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception: font=ImageFont.load_default()
    tiles=[]
    for f in frames:
        p=f.get("_thumb")
        if not p: continue
        im=Image.open(p).convert("RGB")
        r=cell_w/im.width; h=min(int(im.height*r), 900)
        im=im.resize((cell_w, int(im.height*r)))
        if im.height>h: im=im.crop((0,0,cell_w,h))
        tiles.append((f, im))
    paths=[]; per=cols*3
    for s in range(0, len(tiles), per):
        chunk=tiles[s:s+per]; rows=[chunk[i:i+cols] for i in range(0,len(chunk),cols)]
        H=sum(max(im.height for _,im in r)+34 for r in rows)+30
        sh=Image.new("RGB", (cols*(cell_w+12)+12, H), (40,40,44)); d=ImageDraw.Draw(sh)
        d.text((12,8), f"{title}  [{s+1}-{s+len(chunk)} of {len(tiles)}]", fill=(255,255,255), font=font)
        y=30
        for r in rows:
            x=12
            for f,im in r:
                d.text((x,y), f"{f['id']} · {f['name'][:58]} ({f['width']}x{f['height']})", fill=(255,220,120), font=font)
                sh.paste(im,(x,y+18)); x+=cell_w+12
            y+=max(im.height for _,im in r)+34
        p=f"{out}_{s//per+1}.png"; sh.save(p); paths.append(p)
    return paths
if __name__=="__main__":
    args=[a for a in sys.argv[1:] if not a.startswith("--")]; refresh="--refresh" in sys.argv
    cols=next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--cols=")),4)
    cw=next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--cw=")),520)
    c=canvas(args[0]); subs=args[1:]
    for pg in c["pages"]:
        if subs and not any(s.lower() in pg["name"].lower() for s in subs): continue
        fs=sorted([f for f in c["frames"] if f["pageId"]==pg["id"]], key=lambda f:(f["y"],f["x"]))
        with ThreadPoolExecutor(5) as ex:
            for f,p in zip(fs, ex.map(lambda f: fetch(f["id"], refresh), fs)): f["_thumb"]=p
        safe="".join(ch if ch.isalnum() else "_" for ch in pg["name"])[:40]
        print(pg["name"], len(fs), sheet(fs, f"{W}/sheets/{args[0]}_{safe}", cell_w=cw, cols=cols, title=pg["name"]))
