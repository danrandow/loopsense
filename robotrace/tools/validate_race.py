#!/usr/bin/env python3
"""Score every iteration's design from a finished race on FRESH seeds, in the free simulator.

    python3 tools/validate_race.py race-40-a race-40-b race-40-c [--seeds 50]

Race scores are noisy and an agent only ever sees its own development seeds. This re-races each iteration's complete
design on seeds nobody has seen (5000+), on the development tracks and on the held-out tracks, so the question
"did this team's designs get better?" is answered by measurement, not by one race's luck. It costs no tokens.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import baseline_search as bs  # noqa: E402


def designs(package: Path) -> dict[int, dict]:
    found = {}
    for folder in sorted(package.glob("iteration-*"), key=lambda p: int(p.name.split("-")[1])):
        current = folder / "entity1" / "current"
        if not current.is_file():
            continue  # no complete robot was delivered in this iteration
        payload = json.loads((folder / "entity1" / "versions" / current.read_text().strip() / "payload.json").read_text())
        found[int(folder.name.split("-")[1])] = {k: payload[k] for k in ("geometry", "controller", "observation_request") if k in payload}
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("races", nargs="+", help="race ids, e.g. race-40-a (packages are looked up next to the loopsense root)")
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--workspace", type=Path, default=ROOT.parent)
    args = ap.parse_args()
    config, tracks = bs.load_config(), bs.load_tracks()
    dev, held = ["oval", "s-bend", "slalom"], ["hairpin", "hairpin-b", "slalom-b"]
    fresh = list(range(5000, 5000 + args.seeds))
    summary: dict[str, list] = {}
    for race in args.races:
        for entrant in ("randow-maps", "opt-eval"):
            package = args.workspace / f"{race}-{entrant}"
            if not package.is_dir():
                continue
            print(f"\n{race} {entrant}  (fresh seeds: {args.seeds} per track)")
            print("  iter | dev mean | slalom finish | held-out mean")
            series = []
            for iteration, design in designs(package).items():
                d = bs.evaluate(design, tracks, dev, fresh, config)
                h = bs.evaluate(design, tracks, held, fresh[:20], config)
                series.append((iteration, d["mean"], h["mean"]))
                print(f"  {iteration:4d} | {d['mean']:8.0f} | {d['tracks']['slalom']['finish_rate']:12.0%} | {h['mean']:12.0f}")
            if len(series) >= 2:
                summary.setdefault(entrant, []).append((series[0], series[-1], max(series, key=lambda t: t[1])))
    if summary:
        print("\nLearning check (dev mean on fresh seeds; first design -> last design, and the best iteration)")
        for entrant, runs in summary.items():
            gains = [last[1] - first[1] for first, last, _ in runs]
            print(f"  {entrant}: first->last change per run {[round(g) for g in gains]}; mean {statistics.fmean(gains):+.0f}; runs improved {sum(g > 0 for g in gains)}/{len(gains)}")


if __name__ == "__main__":
    main()
