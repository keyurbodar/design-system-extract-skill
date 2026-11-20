"""Step 4 gate. Contact sheet of the LIVE screenshots, before anything is published.
usage: python3 live_sheet.py [group ...]      writes $DSX_WORK/sheets/live_<group>.png (one per scenario group)
Open each sheet and check that every capture shows the state its name says (menu open, dialog open, hover visible)."""
import json, os, sys
from PIL import Image, ImageDraw
W = os.environ.get("DSX_WORK", os.getcwd()); os.makedirs(f"{W}/sheets", exist_ok=True)
idx = json.load(open(f"{W}/snaps/index.json")); groups = {}
for k, v in idx.items():
    if v.get("ok") and (not sys.argv[1:] or v.get("group") in sys.argv[1:]): groups.setdefault(v.get("group", "ungrouped"), []).append(k)
for g, keys in groups.items():
    e = idx[keys[0]]; cw = 420 if e["w"] > e["h"] else 240; ch = int(cw * e["h"] / e["w"]); cols = 5 if e["w"] > e["h"] else 8
    for part in range(0, len(keys), cols * 4):
        ks = keys[part:part + cols * 4]; rows = -(-len(ks) // cols)
        sh = Image.new("RGB", (cols * (cw + 8) + 8, rows * (ch + 26) + 8), (40, 40, 44)); d = ImageDraw.Draw(sh)
        for i, k in enumerate(ks):
            im = Image.open(f"{W}/snaps/{k}.live.png").convert("RGB").resize((cw, ch)); x = 8 + (i % cols) * (cw + 8); y = 8 + (i // cols) * (ch + 26)
            d.text((x, y), k[:60], fill=(255, 220, 120)); sh.paste(im, (x, y + 14))
        out = f"{W}/sheets/live_{g}_{part // (cols * 4) + 1}.png"; sh.save(out); print(g, len(ks), out)
