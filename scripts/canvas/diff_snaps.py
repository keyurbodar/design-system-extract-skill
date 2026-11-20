"""Step 7b. Compare every published snapshot frame with its live screenshot.
usage: python3 diff_snaps.py [threshold_percent=6]     (run sheets.py first: it downloads the canvas renders into thumbs/)
Score = percent of pixels (400x250 greyscale) that differ by more than 40/255. Writes viewed / diff / passed into the manifest.
A frame only counts as passed here or after a human-style look at its contact sheet; "it was published" is not a pass.
Animated regions (video, canvas shaders, wallpapers) inflate the score: look at those frames instead of trusting the number."""
import json, numpy as np, sys
from PIL import Image, ImageChops
from sheetlib import *
thr = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0; out = []
with state_update() as s:
    for mk, e in s["frames"].items():
        if not mk.startswith("live_"): continue
        k = mk[5:]; t = f"{W}/thumbs/{e['id']}.png"; l = f"{W}/snaps/{k}.live.png"
        if not (os.path.exists(t) and os.path.exists(l)): out.append((999, k, "no canvas render downloaded")); continue
        a = Image.open(l).convert("L").resize((400, 250)); b = Image.open(t).convert("L").resize((400, 250))
        score = float((np.asarray(ImageChops.difference(a, b)).astype(float) > 40).mean() * 100); out.append((round(score, 2), k, ""))
        e["viewed"] = True; e["diff"] = round(score, 2); e["passed"] = score < thr
out.sort(reverse=True)
print("frames", len(out), f"passed (<{thr}% of pixels differ)", sum(1 for o in out if o[0] < thr))
for o in out[:20]: print(o)
