#!/usr/bin/env python3
"""Zero-cost held-out scoring for Gate 3b: score every Arm B submitted design (agent + reconstructed matched
baselines) and the Phase 0 ES ceiling designs on the held-out tracks/seeds, side by side.

Not part of the harness and not a new evidence path -- a read-only analysis of files already on disk
(tools/probe_tool.py's --out JSON, and phase0/ceiling_rng*.json). The matched baselines' final designs were not
saved by probe_tool.py, so they are reconstructed deterministically here with the exact same rng seeds and
n_evals the original run used (random_hillclimb/hillclimb_independent_draw are pure functions of
(start, rng_seed, n) with no model calls), which costs zero tokens and reproduces the exact design bit-for-bit.

Held-out = seeds 101-110 on hairpin/hairpin-b/slalom-b, matching PHASE0_FREEZE.md §3a's convention exactly, so
the ES ceiling numbers recomputed here should reproduce 599.8 / sd 203.6 as a cross-check.

Run from the robotrace directory: python3 tools/score_heldout.py
"""
from __future__ import annotations

import glob
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from baseline_search import evaluate, load_config, load_tracks, starting_design  # noqa: E402
from probe_tool import hillclimb_independent_draw, random_hillclimb  # noqa: E402

HELD_OUT_TRACKS = ["hairpin", "hairpin-b", "slalom-b"]
HELD_OUT_SEEDS = list(range(101, 111))
EVIDENCE_SEEDS = list(range(1, 21))
SPACE = "full"

# (file, rng base used for that invocation's --rng) -- run index within the file supplies the +run offset.
ARM_B_FILES = [("phase1/arm_b_100ev_r1.json", 1), ("phase1/arm_b_100ev_batch2.json", 2), ("phase1/arm_b_100ev_batch3.json", 3)]


def main() -> None:
    config, tracks = load_config(), load_tracks()
    race = config["_race"]
    dev = list(race["evaluation"]["development_tracks"])
    start = starting_design(None)

    def held_out_score(design: dict) -> dict:
        return evaluate(design, tracks, HELD_OUT_TRACKS, HELD_OUT_SEEDS, config)

    # ev0 (starting design's own evidence) is identical across all replicates -- compute once.
    from probe_step import evidence_for
    ev0 = evidence_for(start, tracks, dev, EVIDENCE_SEEDS, config)
    rows = []
    for path, rng_base in ARM_B_FILES:
        data = json.loads((ROOT / path).read_text())
        for rec in data["replicates"]:
            run, n = rec["run"], rec["n_evals"]
            agent_design = rec["final_design"]
            if agent_design is not None:
                rows.append({"kind": "agent", "source": f"{Path(path).stem}#{run}", "n_evals": n,
                             "held_out": held_out_score(agent_design)})
            draw1_final = random_hillclimb(start, ev0, tracks, dev, EVIDENCE_SEEDS, config,
                                            random.Random(rng_base * 1000 + run), n, SPACE)
            rows.append({"kind": "matched_baseline_draw1", "source": f"{Path(path).stem}#{run}", "n_evals": n,
                         "held_out": held_out_score(draw1_final)})
            draw2_final = hillclimb_independent_draw(start, tracks, dev, EVIDENCE_SEEDS, config,
                                                      random.Random(rng_base * 2000 + run), n, SPACE)
            rows.append({"kind": "matched_baseline_draw2", "source": f"{Path(path).stem}#{run}", "n_evals": n,
                         "held_out": held_out_score(draw2_final)})

    for path in sorted(glob.glob(str(ROOT / "phase0" / "ceiling_rng*.json"))):
        design = json.loads(Path(path).read_text())
        rows.append({"kind": "es_ceiling", "source": Path(path).stem, "n_evals": None, "held_out": held_out_score(design)})

    print(f"{'kind':26s} {'source':28s} {'N':>4s} {'held-out mean':>14s}  per-track (finish%)")
    for r in rows:
        ho = r["held_out"]
        per_track = " | ".join(f"{k} {v['mean']:.0f} ({v['finish_rate']:.0%})" for k, v in ho["tracks"].items())
        n_str = "" if r["n_evals"] is None else str(r["n_evals"])
        print(f"{r['kind']:26s} {r['source']:28s} {n_str:>4s} {ho['mean']:14.1f}  {per_track}")

    def stats(kind: str) -> tuple[float, float, int]:
        # Sample sd (ddof=1), matching PHASE0_FREEZE.md §3a's convention -- its reported sd 203.6 for the same
        # 5 ES designs only reproduces with stdev, not pstdev (the individual held-out means reproduce almost
        # exactly either way: 794.2/578.5/720.7/265.6/639.2 here vs 794/579/721/266/639 there).
        vals = [r["held_out"]["mean"] for r in rows if r["kind"] == kind]
        return (statistics.mean(vals), statistics.stdev(vals), len(vals)) if len(vals) > 1 else (vals[0] if vals else 0.0, 0.0, len(vals))

    print()
    for kind in ("agent", "matched_baseline_draw1", "matched_baseline_draw2", "es_ceiling"):
        mean, sd, n = stats(kind)
        print(f"{kind:26s} n={n:3d} mean {mean:7.1f}  sd {sd:6.1f}")

    Path(ROOT / "phase1" / "heldout_scores.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
