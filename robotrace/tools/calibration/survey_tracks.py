"""Calibration helper: finish rates per track for each design and a small-body variant.
usage: survey_tracks.py ROBOTRACE_DIR REPO_ROOT OUT.json DESIGNS.json MAX_DESIGNS TRACKS.json N_SEEDS FIRST_SEED
Uses the config of race-40-c-randow-maps; designs come from collect_designs.py.
Race data moved to robotrace/races/ -- pass REPO_ROOT=.../robotrace/races (not the git repo root) so
race-40-c-randow-maps/config/race.yaml resolves; same for collect_designs.py's REPO_ROOT argument."""
import sys, json, glob, copy, yaml, itertools
from multiprocessing import Pool
RT, ROOT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, RT)
from simulator.adapter import run_trial
from orchestrator.validators import validate_package, ValidationError
race = yaml.safe_load(open(f"{ROOT}/race-40-c-randow-maps/config/race.yaml"))
exp = yaml.safe_load(open(f"{RT}/config/experiment.yaml"))
cfg = dict(race); cfg.setdefault("design_bounds", exp["design_bounds"])
designs=[]
for d in json.load(open(sys.argv[4])):
    try: validate_package(d["pkg"], cfg["design_bounds"])
    except Exception: continue
    designs.append(d)
stride=max(1,len(designs)//int(sys.argv[5])); designs=designs[::stride][:int(sys.argv[5])]
variants=[]
for d in designs:
    variants.append((d["id"],"as-is",d["pkg"]))
    p=copy.deepcopy(d["pkg"]); p["geometry"].update(body_width=0.08, body_length=0.10)
    variants.append((d["id"],"min-body",p))
tracks=json.load(open(sys.argv[6]))  # list of track dicts
seeds=list(range(int(sys.argv[8]),int(sys.argv[8])+int(sys.argv[7])))
def job(a):
    (i,v,p),t=a
    r=[run_trial(p,t,s,cfg) for s in seeds]
    return (i,v,t["id"],sum(x["metrics"]["completion"] for x in r if "metrics" in x),len(seeds),sum(x["score"] for x in r)/len(seeds))
if __name__=="__main__":
    jobs=list(itertools.product(variants,tracks))
    with Pool() as pool: res=pool.map(job,jobs,chunksize=4)
    json.dump(res,open(OUT,"w")); print("done",len(res),"cells;",len(designs),"designs")
