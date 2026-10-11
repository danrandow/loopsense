#!/usr/bin/env python3
"""Free, no-LLM baseline for the Robot Race: how much can plain search improve a design?

Run from the robotrace directory:
    python3 tools/baseline_search.py --track slalom --space full --evals 2000 --train-seeds 20 --out best.json

It answers questions the races cannot answer cheaply: is there headroom beyond the iteration-0 design, how noisy
is a score, and how well does a design found on some seeds hold up on fresh seeds and on the held-out tracks?
The simulator costs no tokens (about 0.01 s per trial), so thousands of evaluations are free.

The search is a (1+1) evolution strategy: mutate a few parameters of the best design so far, keep the change if the
mean score on the TRAIN seeds improves. The best design is then re-scored on fresh VALIDATION seeds (which the search
never saw) and on the held-out tracks, so a design that only got lucky on its train seeds shows up as a drop.
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orchestrator.validators import design_bounds_from_contract  # noqa: E402
from simulator.adapter.headless import run_trial  # noqa: E402

TEMPLATE = ROOT / "package-templates" / "randow-maps"
LINE_LOSS = ["stop", "search_left", "search_right", "last_direction"]
SENSOR_SIZES = [0.008, 0.012, 0.016]


def load_config(template: Path = TEMPLATE) -> dict:
    import yaml
    race = yaml.safe_load((template / "config" / "race.yaml").read_text())
    contract = json.loads((template / "entities" / "entityPub0" / "contract.schema.json").read_text())
    return {"design_bounds": design_bounds_from_contract(contract), "simulator": race["simulator"],
            "evaluation": {"noise": race["evaluation"]["noise"]}, "score": race["score"], "_race": race}


def load_tracks() -> dict:
    tracks = {}
    for path in glob.glob(str(ROOT / "tracks" / "*" / "*.json")):
        track = json.loads(Path(path).read_text())
        tracks[track["id"]] = track
    return tracks


def starting_design(path: str | None) -> dict:
    if path:
        design = json.loads(Path(path).read_text())
        return {k: design[k] for k in ("geometry", "controller", "observation_request")}
    return {"geometry": {"body_length": 0.18, "body_width": 0.14, "mass": 0.8, "sensor_size": 0.012, "wheel_radius": 0.035, "wheel_track": 0.14,
                         "sensor_positions": [{"x": -0.04, "y": 0.04}, {"x": -0.02, "y": 0.05}, {"x": 0, "y": 0.06}, {"x": 0.02, "y": 0.05}, {"x": 0.04, "y": 0.04}]},
            "controller": {"base_speed": 1.2, "kp": 8.0, "ki": 0.5, "kd": 2.0, "line_loss": "last_direction", "sensor_weights": [-1.5, -0.75, 0, 0.75, 1.5]},
            "observation_request": {"measurements": ["completion", "progress"]}}


def clamp(value, low, high):
    return max(low, min(high, value))


def mutate(design: dict, rng: random.Random, space: str) -> dict:
    d = copy.deepcopy(design)
    c, g = d["controller"], d["geometry"]
    moves = ["speed", "kp", "ki", "kd", "weights", "line_loss"]
    if space == "full":
        moves += ["track", "wheel_radius", "body", "mass", "sensor_size", "layout", "layout"]
    for move in rng.sample(moves, k=rng.choice([1, 1, 2, 3])):
        if move == "speed": c["base_speed"] = clamp(c["base_speed"] * rng.uniform(.8, 1.25), .05, 2)
        elif move == "kp": c["kp"] = clamp(c["kp"] * rng.uniform(.6, 1.6) + rng.uniform(-.3, .3), 0, 20)
        elif move == "ki": c["ki"] = clamp(c["ki"] * rng.uniform(.4, 2) + rng.uniform(0, .1), 0, 5)
        elif move == "kd": c["kd"] = clamp(c["kd"] * rng.uniform(.5, 1.8) + rng.uniform(-.2, .2), 0, 10)
        elif move == "weights": c["sensor_weights"] = [clamp(w + rng.gauss(0, .25), -2, 2) for w in c["sensor_weights"]]
        elif move == "line_loss": c["line_loss"] = rng.choice(LINE_LOSS)
        elif move == "track": g["wheel_track"] = clamp(g["wheel_track"] + rng.gauss(0, .015), .08, .18)
        elif move == "wheel_radius": g["wheel_radius"] = clamp(g["wheel_radius"] + rng.gauss(0, .005), .02, .05)
        elif move == "body":
            g["body_width"] = clamp(g["body_width"] + rng.gauss(0, .015), .08, .18)
            g["body_length"] = clamp(g["body_length"] + rng.gauss(0, .02), .10, .24)
        elif move == "mass": g["mass"] = clamp(g["mass"] * rng.uniform(.8, 1.25), .4, 1.5)
        elif move == "sensor_size": g["sensor_size"] = rng.choice(SENSOR_SIZES)
        elif move == "layout":
            n = clamp(len(g["sensor_positions"]) + rng.choice([-1, 0, 0, 0, 1]), 3, 7)
            spread, forward, curve = rng.uniform(.02, .08), rng.uniform(-.02, .08), rng.uniform(0, .03)
            xs = [spread * (2 * i / (n - 1) - 1) for i in range(n)]
            g["sensor_positions"] = [{"x": round(x, 4), "y": round(clamp(forward - curve * abs(x) / spread, -.06, .08), 4)} for x in xs]
            wmax = clamp(abs(c["sensor_weights"][-1]) if c["sensor_weights"] else 1.5, .5, 2)
            c["sensor_weights"] = [round(wmax * (2 * i / (n - 1) - 1), 3) for i in range(n)]
    return d


def evaluate(design: dict, tracks: dict, names: list[str], seeds: list[int], config: dict) -> dict:
    per_track = {}
    for name in names:
        trials = [run_trial(design, tracks[name], seed, config) for seed in seeds]
        scores = [float(t["score"]) for t in trials]
        per_track[name] = {"mean": statistics.mean(scores), "finish_rate": sum(t.get("termination_reason") == "finished" for t in trials) / len(trials)}
    return {"mean": statistics.mean(v["mean"] for v in per_track.values()), "tracks": per_track}


def fmt(result: dict) -> str:
    return f"mean {result['mean']:.0f} | " + ", ".join(f"{k} {v['mean']:.0f} (finish {v['finish_rate']:.0%})" for k, v in result["tracks"].items())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--track", nargs="+", default=["oval", "s-bend", "slalom"], help="development tracks to optimise on")
    ap.add_argument("--space", choices=["controller", "full"], default="controller")
    ap.add_argument("--evals", type=int, default=500)
    ap.add_argument("--train-seeds", type=int, default=20)
    ap.add_argument("--validation-seeds", type=int, default=50)
    ap.add_argument("--start", help="JSON file holding a design (or a payload with geometry/controller); default is the iteration-0 style design")
    ap.add_argument("--rng", type=int, default=1)
    ap.add_argument("--out", help="write the best design here")
    args = ap.parse_args()

    config, tracks, rng = load_config(), load_tracks(), random.Random(args.rng)
    train = list(range(1000, 1000 + args.train_seeds))
    validation = list(range(5000, 5000 + args.validation_seeds))
    held_out = [t for t in ("hairpin", "hairpin-b", "slalom-b") if t in tracks]
    start = starting_design(args.start)
    best, best_score = start, evaluate(start, tracks, args.track, train, config)
    print(f"start  train: {fmt(best_score)}", flush=True)
    began = time.time()
    for n in range(1, args.evals + 1):
        candidate = mutate(best, rng, args.space)
        score = evaluate(candidate, tracks, args.track, train, config)
        if score["mean"] > best_score["mean"]:
            best, best_score = candidate, score
            print(f"eval {n:5d} train: {fmt(score)}", flush=True)
    print(f"\n{args.evals} evaluations x {len(train)} seeds x {len(args.track)} tracks in {time.time() - began:.0f} s")
    for label, design in (("start", start), ("best ", best)):
        print(f"{label} train      : {fmt(evaluate(design, tracks, args.track, train, config))}")
        print(f"{label} validation : {fmt(evaluate(design, tracks, args.track, validation, config))}   <- fresh seeds the search never saw")
        print(f"{label} held-out   : {fmt(evaluate(design, tracks, held_out, list(range(101, 111)), config))}")
    if args.out:
        Path(args.out).write_text(json.dumps(best, indent=2))
        print(f"best design written to {args.out}")


if __name__ == "__main__":
    main()
