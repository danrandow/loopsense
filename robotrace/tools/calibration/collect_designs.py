"""Calibration helper: gather every distinct design from race outputs (usage: collect_designs.py REPO_ROOT OUT.json)."""
import json, glob, hashlib, sys
seen={}; 
for p in sorted(glob.glob(sys.argv[1]+"/race-*/**/payload.json", recursive=True)):
    try: d=json.load(open(p))
    except Exception: continue
    if not isinstance(d,dict) or "geometry" not in d or "controller" not in d: continue
    pkg={"geometry":d["geometry"],"controller":d["controller"],"observation_request":d.get("observation_request",{"measurements":["completion"]})}
    h=hashlib.sha1(json.dumps({"g":pkg["geometry"],"c":pkg["controller"]},sort_keys=True).encode()).hexdigest()[:10]
    seen.setdefault(h,(pkg,p))
print(len(seen),"unique designs")
json.dump([{"id":h,"pkg":v[0],"src":v[1].split("/loopsense/")[-1][:60]} for h,v in seen.items()],open(sys.argv[2],"w"))
